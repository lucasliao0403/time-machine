#!/usr/bin/env python3
"""
FastAPI backend for TimeMachine Web UI
Serves TimeMachine data and provides REST API for counterfactual analysis
"""

import sys
import os
from pathlib import Path

# Add parent directory to Python path to import timemachine
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to load environment variables from .env file if dotenv is available
try:
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    load_dotenv(env_path)
    print(f"[DEBUG] Loading .env from: {env_path}")
    print(f"[DEBUG] .env file exists: {env_path.exists()}")
    print(f"[DEBUG] OPENAI_API_KEY loaded: {'OPENAI_API_KEY' in os.environ}")
except ImportError:
    print("[DEBUG] dotenv not available, skipping .env file loading")
    print(f"[DEBUG] OPENAI_API_KEY in env: {'OPENAI_API_KEY' in os.environ}")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from collections import defaultdict, Counter

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

# Global recorder instance - prioritize test database
import glob
import os
test_db = "quick_demo.db"
fallback_db = "llm_test.db" 
default_db = "timemachine_recordings.db"

if os.path.exists(test_db):
    db_path = os.path.abspath(test_db)
    print(f"[INIT] Using quick_demo database: {db_path}")
elif os.path.exists(fallback_db):
    db_path = os.path.abspath(fallback_db)
    print(f"[INIT] Using fallback LLM test database: {db_path}")
elif os.path.exists(default_db):
    db_path = os.path.abspath(default_db)
    print(f"[INIT] Using default database: {db_path}")
else:
    # Look for any other .db files
    db_files = glob.glob("../*.db") + glob.glob("*.db")
    if db_files:
        db_path = os.path.abspath(db_files[0])
        print(f"[INIT] Using found database: {db_path}")
    else:
        db_path = default_db
        print(f"[INIT] Creating new database: {db_path}")

print(f"[INIT] Database exists: {os.path.exists(db_path)}")
recorder = TimeMachineRecorder(db_path)
if not os.path.exists(db_path):
    print(f"[INIT] Initializing database...")
    recorder.init_database()

def get_recorder():
    """Get the global recorder instance"""
    return recorder

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
        
        # Enhance executions with LLM call data
        enhanced_executions = []
        for exec in executions:
            # Get LLM calls for this execution
            llm_calls = recorder.get_llm_calls(exec['id'])
            
            enhanced_executions.append(
                NodeExecution(
                    id=exec['id'],
                    node_name=exec['node_name'],
                    timestamp=exec['timestamp'],
                    duration_ms=exec.get('duration_ms', 0),
                    status=exec.get('status', 'unknown'),
                    input_state=json.loads(exec.get('input_state', '{}')),
                    output_state=json.loads(exec.get('output_state', '{}')),
                    error_message=exec.get('error_message'),
                    llm_calls=llm_calls
                )
            )
        
        return enhanced_executions
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

@app.get("/api/flow-visualization/{graph_run_id}")
def get_flow_visualization(graph_run_id: str):
    """Generate 2D flow visualization data for a graph run"""
    print(f"[BACKEND] get_flow_visualization called with graph_run_id: {graph_run_id}")
    
    try:
        print("[BACKEND] Getting recorder...")
        recorder = get_recorder()
        print(f"[BACKEND] Recorder initialized, db_path: {recorder.db_path}")
        
        # Check if database exists
        import os
        db_exists = os.path.exists(recorder.db_path)
        print(f"[BACKEND] Database exists: {db_exists}, path: {recorder.db_path}")
        
        # Get all executions for this graph run
        print(f"[BACKEND] Getting executions for graph_run_id: {graph_run_id}")
        executions = recorder.get_graph_executions(graph_run_id)
        print(f"[BACKEND] Found {len(executions) if executions else 0} executions")
        
        if not executions:
            print(f"[BACKEND] No executions found for graph_run_id: {graph_run_id}")
            # Let's also check what graph runs exist
            try:
                all_runs = recorder.list_graph_runs()
                print(f"[BACKEND] Available graph runs: {[run.get('graph_run_id', 'unknown') for run in all_runs]}")
            except Exception as list_error:
                print(f"[BACKEND] Error listing graph runs: {list_error}")
            raise HTTPException(status_code=404, detail=f"Graph run not found: {graph_run_id}. Check if any executions are recorded.")
        
        # Sort executions by timestamp to determine flow order
        sorted_executions = sorted(executions, key=lambda x: x['timestamp'])
        
        # Build nodes
        nodes = {}
        node_stats = defaultdict(lambda: {'count': 0, 'durations': [], 'successes': 0})
        
        for execution in sorted_executions:
            node_name = execution['node_name']
            node_stats[node_name]['count'] += 1
            if execution.get('duration_ms'):
                node_stats[node_name]['durations'].append(execution['duration_ms'])
            if execution.get('status') == 'success':
                node_stats[node_name]['successes'] += 1
        
        # Create flow nodes
        flow_nodes = []
        for i, (node_name, stats) in enumerate(node_stats.items()):
            avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            success_rate = stats['successes'] / stats['count'] if stats['count'] > 0 else 0
            
            flow_nodes.append({
                'id': node_name,
                'name': node_name,
                'type': 'start' if i == 0 else ('end' if i == len(node_stats) - 1 else 'node'),
                'position': {'x': i * 200, 'y': 100},  # Simple horizontal layout
                'executionCount': stats['count'],
                'avgDuration': avg_duration,
                'successRate': success_rate,
                'lastExecuted': max([e['timestamp'] for e in sorted_executions if e['node_name'] == node_name])
            })
        
        # Build edges from execution sequence
        edges = []
        edge_stats = defaultdict(lambda: {'count': 0, 'durations': []})
        
        for i in range(len(sorted_executions) - 1):
            current = sorted_executions[i]
            next_exec = sorted_executions[i + 1]
            
            edge_key = f"{current['node_name']}->{next_exec['node_name']}"
            edge_stats[edge_key]['count'] += 1
            
            if current.get('duration_ms'):
                edge_stats[edge_key]['durations'].append(current['duration_ms'])
        
        # Create flow edges
        flow_edges = []
        total_transitions = len(sorted_executions) - 1
        
        for edge_key, stats in edge_stats.items():
            source, target = edge_key.split('->')
            frequency = (stats['count'] / total_transitions * 100) if total_transitions > 0 else 0
            avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            
            flow_edges.append({
                'id': edge_key,
                'source': source,
                'target': target,
                'executionCount': stats['count'],
                'frequency': frequency,
                'avgDuration': avg_duration,
                'metadata': {'type': 'always'}  # For single run, no conditionals
            })
        
        # Calculate statistics
        node_names = [node['name'] for node in flow_nodes]
        statistics = {
            'totalRuns': 1,
            'mostCommonPath': node_names,
            'branchingPoints': [],  # No branching in single run
            'deadEnds': [node_names[-1]] if node_names else [],
            'averagePathLength': len(node_names),
            'pathVariability': 0.0  # Single run = no variability
        }
        
        # Calculate bounds for visualization
        bounds = {
            'minX': 0,
            'maxX': max([node['position']['x'] for node in flow_nodes]) + 100 if flow_nodes else 200,
            'minY': 0,
            'maxY': 200
        }
        
        return {
            'nodes': flow_nodes,
            'edges': flow_edges,
            'statistics': statistics,
            'bounds': bounds
        }
        
    except Exception as e:
        print(f"Error generating flow visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/aggregate-flow-visualization")
def get_aggregate_flow_visualization():
    """Generate aggregate 2D flow visualization across all graph runs"""
    print("[BACKEND] get_aggregate_flow_visualization called")
    
    try:
        print("[BACKEND] Getting recorder for aggregate visualization...")
        recorder = get_recorder()
        print(f"[BACKEND] Recorder initialized, db_path: {recorder.db_path}")
        
        # Check if database exists
        import os
        db_exists = os.path.exists(recorder.db_path)
        print(f"[BACKEND] Database exists: {db_exists}, path: {recorder.db_path}")
        
        # Get all graph runs
        print("[BACKEND] Getting all graph runs...")
        graph_runs = recorder.list_graph_runs()
        print(f"[BACKEND] Found {len(graph_runs) if graph_runs else 0} graph runs")
        
        if not graph_runs:
            return {
                'nodes': [],
                'edges': [],
                'statistics': {
                    'totalRuns': 0,
                    'mostCommonPath': [],
                    'branchingPoints': [],
                    'deadEnds': [],
                    'averagePathLength': 0,
                    'pathVariability': 0.0
                },
                'bounds': {'minX': 0, 'maxX': 200, 'minY': 0, 'maxY': 200}
            }
        
        # Aggregate data across all runs
        all_paths = []
        node_stats = defaultdict(lambda: {'count': 0, 'durations': [], 'successes': 0, 'last_executed': 0})
        edge_stats = defaultdict(lambda: {'count': 0, 'durations': []})
        
        for run in graph_runs:
            executions = recorder.get_graph_executions(run['graph_run_id'])
            sorted_executions = sorted(executions, key=lambda x: x['timestamp'])
            
            # Track path for this run
            path = [e['node_name'] for e in sorted_executions]
            all_paths.append(path)
            
            # Update node statistics
            for execution in sorted_executions:
                node_name = execution['node_name']
                node_stats[node_name]['count'] += 1
                if execution.get('duration_ms'):
                    node_stats[node_name]['durations'].append(execution['duration_ms'])
                if execution.get('status') == 'success':
                    node_stats[node_name]['successes'] += 1
                node_stats[node_name]['last_executed'] = max(
                    node_stats[node_name]['last_executed'], 
                    execution['timestamp']
                )
            
            # Update edge statistics
            for i in range(len(sorted_executions) - 1):
                current = sorted_executions[i]
                next_exec = sorted_executions[i + 1]
                edge_key = f"{current['node_name']}->{next_exec['node_name']}"
                edge_stats[edge_key]['count'] += 1
                if current.get('duration_ms'):
                    edge_stats[edge_key]['durations'].append(current['duration_ms'])
        
        # Create aggregated nodes with positioning
        flow_nodes = []
        unique_nodes = list(node_stats.keys())
        
        # Simple grid layout for multiple nodes
        cols = max(3, int(len(unique_nodes) ** 0.5))
        for i, (node_name, stats) in enumerate(node_stats.items()):
            row = i // cols
            col = i % cols
            
            avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            success_rate = stats['successes'] / stats['count'] if stats['count'] > 0 else 0
            
            flow_nodes.append({
                'id': node_name,
                'name': node_name,
                'type': 'node',  # Determine type based on usage patterns
                'position': {'x': col * 200 + 100, 'y': row * 150 + 100},
                'executionCount': stats['count'],
                'avgDuration': avg_duration,
                'successRate': success_rate,
                'lastExecuted': stats['last_executed']
            })
        
        # Create aggregated edges
        flow_edges = []
        total_runs = len(graph_runs)
        
        for edge_key, stats in edge_stats.items():
            source, target = edge_key.split('->')
            frequency = (stats['count'] / total_runs * 100) if total_runs > 0 else 0
            avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            
            flow_edges.append({
                'id': edge_key,
                'source': source,
                'target': target,
                'executionCount': stats['count'],
                'frequency': frequency,
                'avgDuration': avg_duration,
                'metadata': {
                    'type': 'conditional' if frequency < 100 else 'always'
                }
            })
        
        # Calculate branching points
        branching_points = []
        edge_sources = defaultdict(list)
        for edge in flow_edges:
            edge_sources[edge['source']].append({
                'targetNode': edge['target'],
                'frequency': edge['frequency']
            })
        
        for source, targets in edge_sources.items():
            if len(targets) > 1:
                branching_points.append({
                    'nodeId': source,
                    'branches': targets
                })
        
        # Find most common path
        path_counter = Counter([tuple(path) for path in all_paths])
        most_common_path = list(path_counter.most_common(1)[0][0]) if path_counter else []
        
        # Calculate path variability
        unique_paths = len(set([tuple(path) for path in all_paths]))
        path_variability = (unique_paths - 1) / max(1, total_runs) if total_runs > 1 else 0.0
        
        statistics = {
            'totalRuns': total_runs,
            'mostCommonPath': most_common_path,
            'branchingPoints': branching_points,
            'deadEnds': [],  # TODO: Calculate actual dead ends
            'averagePathLength': sum(len(path) for path in all_paths) / len(all_paths) if all_paths else 0,
            'pathVariability': path_variability
        }
        
        # Calculate bounds
        if flow_nodes:
            bounds = {
                'minX': min([node['position']['x'] for node in flow_nodes]) - 50,
                'maxX': max([node['position']['x'] for node in flow_nodes]) + 50,
                'minY': min([node['position']['y'] for node in flow_nodes]) - 50,
                'maxY': max([node['position']['y'] for node in flow_nodes]) + 50
            }
        else:
            bounds = {'minX': 0, 'maxX': 200, 'minY': 0, 'maxY': 200}
        
        return {
            'nodes': flow_nodes,
            'edges': flow_edges,
            'statistics': statistics,
            'bounds': bounds
        }
        
    except Exception as e:
        print(f"Error generating aggregate flow visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting TimeMachine FastAPI backend...")
    print("API docs available at: http://localhost:8000/docs")
    print("React app should run on: http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
