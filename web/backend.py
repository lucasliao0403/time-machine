#!/usr/bin/env python3
"""
FastAPI backend for TimeMachine Web UI
Serves TimeMachine data and provides REST API for counterfactual analysis
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to Python path to import timemachine
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file in project root
env_path = project_root / ".env"
load_dotenv(env_path)
print(f"[DEBUG] Loading .env from: {env_path}")
print(f"[DEBUG] .env file exists: {env_path.exists()}")
print(f"[DEBUG] OPENAI_API_KEY loaded: {'OPENAI_API_KEY' in os.environ}")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

import timemachine
from timemachine.core.recorder import TimeMachineRecorder
from timemachine.replay.engine import ReplayEngine, ReplayConfiguration
from timemachine.replay.counterfactual import CounterfactualEngine

app = FastAPI(title="TimeMachine API", version="1.0.0")

# Enable CORS for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global recorder instance - look for any existing database
import glob
import os
db_files = glob.glob("../*.db") + glob.glob("*.db")
if db_files:
    db_path = os.path.abspath(db_files[0])
else:
    db_path = "timemachine_recordings.db"
print(f"Using database: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")
recorder = TimeMachineRecorder(db_path)

# Pydantic models for API
class GraphRun(BaseModel):
    graph_run_id: str
    start_time: datetime
    execution_count: int
    status: str

class NodeExecution(BaseModel):
    id: str
    node_name: str
    timestamp: int
    duration_ms: float
    status: str
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    error_message: Optional[str] = None

class CounterfactualRequest(BaseModel):
    execution_id: str
    modifications: Dict[str, Any]
    modification_type: str  # 'model', 'temperature', 'prompt', 'custom'

class CounterfactualResult(BaseModel):
    scenario_name: str
    success: bool
    original_output: Dict[str, Any]
    replayed_output: Dict[str, Any]
    difference_score: float
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "TimeMachine API", "version": "1.0.0"}

@app.get("/api/graph-runs", response_model=List[GraphRun])
async def get_graph_runs():
    """Get all recorded graph runs"""
    try:
        runs = recorder.list_graph_runs()
        return [
            GraphRun(
                graph_run_id=run['graph_run_id'],
                start_time=datetime.fromtimestamp(run['start_time'] / 1000),  # Convert milliseconds to seconds
                execution_count=run['node_count'],  # Use node_count from actual schema
                status='completed'  # Default status
            )
            for run in runs
        ]
    except Exception as e:
        print(f"[DEBUG] Error getting graph runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph-runs/{graph_run_id}/executions", response_model=List[NodeExecution])
async def get_graph_executions(graph_run_id: str):
    """Get all node executions for a specific graph run"""
    try:
        executions = recorder.get_graph_executions(graph_run_id)
        return [
            NodeExecution(
                id=exec['id'],
                node_name=exec['node_name'],
                timestamp=exec['timestamp'],
                duration_ms=exec.get('duration_ms', 0),
                status=exec.get('status', 'unknown'),
                input_state=json.loads(exec.get('input_state', '{}')),
                output_state=json.loads(exec.get('output_state', '{}')),
                error_message=exec.get('error_message')
            )
            for exec in executions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get details of a specific execution"""
    try:
        execution = recorder.get_execution_by_id(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "id": execution['id'],
            "node_name": execution['node_name'],
            "timestamp": execution['timestamp'],
            "duration_ms": execution.get('duration_ms', 0),
            "status": execution.get('status', 'unknown'),
            "input_state": json.loads(execution.get('input_state', '{}')),
            "output_state": json.loads(execution.get('output_state', '{}')),
            "error_message": execution.get('error_message')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/counterfactuals/temperature")
async def analyze_temperature_sensitivity(request: CounterfactualRequest):
    """Run temperature sensitivity analysis"""
    try:
        # Import the function registry
        try:
            from function_registry import get_function_registry
            function_registry = get_function_registry()
            print(f"[DEBUG] Function registry loaded: {list(function_registry.keys())}")
        except Exception as e:
            print(f"[DEBUG] Error loading function registry: {e}")
            function_registry = {}
        
        replay_engine = ReplayEngine(recorder)
        replay_engine._function_registry = function_registry
        engine = CounterfactualEngine(replay_engine)
        
        # Extract temperature values from modifications
        temperatures = request.modifications.get('temperatures', [0.1, 0.5, 0.9])
        
        analysis = engine.analyze_temperature_sensitivity(request.execution_id, temperatures)
        
        results = []
        for scenario in analysis.scenarios:
            results.append(CounterfactualResult(
                scenario_name=f"Temperature {scenario.scenario.modifications.get('temperature')}",
                success=scenario.replay_result.success,
                original_output=scenario.replay_result.original_output or {},
                replayed_output=scenario.replay_result.replayed_output or {},
                difference_score=scenario.replay_result.output_difference_score,
                error=scenario.replay_result.error if not scenario.replay_result.success else None
            ))
        
        return {
            "scenarios": results,
            "best_scenario": analysis.best_scenario.scenario.name if analysis.best_scenario else None,
            "insights": analysis.insights,
            "recommendations": analysis.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/counterfactuals/models")
async def analyze_model_alternatives(request: CounterfactualRequest):
    """Run model comparison analysis"""
    try:
        # Import the function registry
        try:
            from function_registry import get_function_registry
            function_registry = get_function_registry()
            print(f"[DEBUG] Model analysis function registry: {list(function_registry.keys())}")
        except Exception as e:
            print(f"[DEBUG] Error loading function registry for models: {e}")
            function_registry = {}
        
        replay_engine = ReplayEngine(recorder)
        replay_engine._function_registry = function_registry
        engine = CounterfactualEngine(replay_engine)
        
        # Extract model names from modifications
        models = request.modifications.get('models', ['gpt-3.5-turbo', 'gpt-4o-mini'])
        
        analysis = engine.analyze_model_alternatives(request.execution_id, models)
        
        results = []
        for scenario in analysis.scenarios:
            results.append(CounterfactualResult(
                scenario_name=f"Model {scenario.scenario.modifications.get('model_name')}",
                success=scenario.replay_result.success,
                original_output=scenario.replay_result.original_output or {},
                replayed_output=scenario.replay_result.replayed_output or {},
                difference_score=scenario.replay_result.output_difference_score,
                error=scenario.replay_result.error if not scenario.replay_result.success else None
            ))
        
        return {
            "scenarios": results,
            "best_scenario": analysis.best_scenario.scenario.name if analysis.best_scenario else None,
            "insights": analysis.insights,
            "recommendations": analysis.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/counterfactuals/custom")
async def run_custom_counterfactual(request: CounterfactualRequest):
    """Run custom counterfactual with arbitrary modifications"""
    try:
        replay_engine = ReplayEngine(recorder)
        
        # Create replay configuration
        config = ReplayConfiguration(
            modify_llm_params=request.modifications,
            modify_state=request.modifications.get('state_modifications', {})
        )
        
        result = replay_engine.replay_execution(request.execution_id, config)
        
        return CounterfactualResult(
            scenario_name=f"Custom {request.modification_type}",
            success=result.success,
            original_output=result.original_output or {},
            replayed_output=result.replayed_output or {},
            difference_score=result.output_difference_score,
            error=result.error if not result.success else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get database statistics"""
    try:
        runs = recorder.list_graph_runs()
        total_executions = sum(run['node_count'] for run in runs)  # Use node_count
        
        latest_run_data = None
        if runs:
            latest = runs[0]
            latest_run_data = {
                "graph_run_id": latest['graph_run_id'],
                "start_time": datetime.fromtimestamp(latest['start_time'] / 1000).isoformat(),
                "execution_count": latest['node_count'],
                "status": "completed"
            }
        
        return {
            "total_graph_runs": len(runs),
            "total_executions": total_executions,
            "database_path": recorder.db_path,
            "latest_run": latest_run_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting TimeMachine FastAPI backend...")
    print("API docs available at: http://localhost:8000/docs")
    print("React app should run on: http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
