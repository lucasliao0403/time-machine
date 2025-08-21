"""
TimeMachine Recording Engine
Records node executions to SQLite database
"""
import sqlite3
import json
import time
import uuid
from typing import Any, Dict, Optional
from pathlib import Path


class TimeMachineRecorder:
    """Records LangGraph node executions to SQLite database"""
    
    def __init__(self, db_path: str = "timemachine_recordings.db"):
        self.db_path = db_path
        self.function_registry = {}  # Store node functions for replay
        self.init_database()
        
    def register_node_function(self, node_name: str, node_function: Any):
        """Register a node function for replay"""
        self.function_registry[node_name] = node_function
        
        # Try to persist function information to database
        try:
            import inspect
            import time
            
            # Extract the actual function from LangGraph wrappers
            actual_function = node_function
            if hasattr(node_function, 'func'):
                actual_function = node_function.func
            elif hasattr(node_function, '_func'):
                actual_function = node_function._func
            
            function_module = getattr(actual_function, '__module__', 'unknown')
            function_name = getattr(actual_function, '__name__', 'unknown')
            
            # Try to get source code (may fail for some functions)
            try:
                function_source = inspect.getsource(actual_function)
            except (OSError, TypeError):
                function_source = str(actual_function)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO function_registry 
                    (node_name, function_module, function_name, function_source, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (node_name, function_module, function_name, function_source, int(time.time())))
                conn.commit()
                
        except Exception as e:
            print(f"[DEBUG] Could not persist function {node_name}: {e}")
        
    def get_node_function(self, node_name: str) -> Optional[Any]:
        """Get a registered node function"""
        # First try in-memory registry
        if node_name in self.function_registry:
            return self.function_registry[node_name]
        
        # Try to load from database and reconstruct
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT function_module, function_name, function_source 
                    FROM function_registry 
                    WHERE node_name = ?
                """, (node_name,))
                result = cursor.fetchone()
                
                if result:
                    module_name, func_name, source = result
                    print(f"[DEBUG] Found function info for {node_name}: {module_name}.{func_name}")
                    
                    # Try to import the function from its original module
                    try:
                        import importlib
                        if module_name != 'unknown':
                            module = importlib.import_module(module_name)
                            function = getattr(module, func_name)
                            
                            # Cache it for future use
                            self.function_registry[node_name] = function
                            return function
                        else:
                            print(f"[DEBUG] Cannot import function with unknown module: {node_name}")
                        
                    except (ImportError, AttributeError) as e:
                        print(f"[DEBUG] Could not import {module_name}.{func_name}: {e}")
                        
        except Exception as e:
            print(f"[DEBUG] Error loading function from database: {e}")
        
        return None
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS node_executions (
                    id TEXT PRIMARY KEY,
                    graph_run_id TEXT,
                    node_name TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    input_state TEXT,
                    output_state TEXT,
                    duration_ms INTEGER,
                    status TEXT,
                    error_message TEXT,
                    graph_structure TEXT,
                    node_position INTEGER,
                    total_tokens INTEGER,
                    estimated_cost REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id TEXT PRIMARY KEY,
                    execution_id TEXT REFERENCES node_executions(id),
                    model_name TEXT,
                    temperature REAL,
                    prompt TEXT,
                    response TEXT,
                    tokens_used INTEGER,
                    timestamp INTEGER,
                    duration_ms INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS graph_snapshots (
                    graph_run_id TEXT PRIMARY KEY,
                    nodes TEXT,
                    edges TEXT,
                    start_node TEXT,
                    end_nodes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS function_registry (
                    node_name TEXT PRIMARY KEY,
                    function_module TEXT,
                    function_name TEXT,
                    function_source TEXT,
                    created_at INTEGER
                )
            """)
            
            conn.commit()
    
    def start_execution(self, node_name: str, input_state: Any, 
                       graph_run_id: Optional[str] = None, 
                       timestamp: Optional[float] = None) -> str:
        """Start recording a node execution"""
        execution_id = str(uuid.uuid4())
        timestamp = timestamp or time.time()
        graph_run_id = graph_run_id or str(uuid.uuid4())
        
        # Serialize input state
        from .serializer import StateSerializer
        serializer = StateSerializer()
        serialized_input = serializer.serialize_state(input_state)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO node_executions 
                (id, graph_run_id, node_name, timestamp, input_state, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (execution_id, graph_run_id, node_name, int(timestamp * 1000), 
                  serialized_input, "running"))
            conn.commit()
        
        return execution_id
    
    def complete_execution(self, execution_id: str, output_state: Any = None,
                          duration_ms: Optional[float] = None, 
                          status: str = "success", error: Optional[str] = None):
        """Complete recording a node execution"""
        serialized_output = None
        if output_state is not None:
            from .serializer import StateSerializer
            serializer = StateSerializer()
            serialized_output = serializer.serialize_state(output_state)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE node_executions 
                SET output_state = ?, duration_ms = ?, status = ?, error_message = ?
                WHERE id = ?
            """, (serialized_output, duration_ms, status, error, execution_id))
            conn.commit()
    
    def get_graph_run_id(self, execution_id: str) -> Optional[str]:
        """Get the graph run ID for an execution"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT graph_run_id FROM node_executions WHERE id = ?",
                (execution_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def list_graph_runs(self) -> list[Dict[str, Any]]:
        """List all recorded graph runs"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT graph_run_id, MIN(timestamp) as start_time, 
                       COUNT(*) as node_count, 
                       GROUP_CONCAT(node_name) as nodes
                FROM node_executions 
                GROUP BY graph_run_id
                ORDER BY start_time DESC
            """)
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def get_graph_executions(self, graph_run_id: str) -> list[Dict[str, Any]]:
        """Get all node executions for a graph run"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM node_executions 
                WHERE graph_run_id = ?
                ORDER BY timestamp
            """, (graph_run_id,))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def save_llm_call(self, llm_call):
        """Save LLM call data to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO llm_calls 
                (id, execution_id, model_name, temperature, prompt, response, 
                 tokens_used, timestamp, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                llm_call.id,
                llm_call.execution_id,
                llm_call.model_name,
                llm_call.temperature,
                llm_call.prompt,
                llm_call.response,
                llm_call.total_tokens,
                int(llm_call.timestamp * 1000),
                llm_call.duration_ms
            ))
            conn.commit()
    
    def get_llm_calls(self, execution_id: str) -> list[Dict[str, Any]]:
        """Get all LLM calls for a specific execution"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM llm_calls 
                WHERE execution_id = ?
                ORDER BY timestamp
            """, (execution_id,))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def get_llm_calls_for_graph_run(self, graph_run_id: str) -> list[Dict[str, Any]]:
        """Get all LLM calls for a graph run"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT lc.* FROM llm_calls lc
                JOIN node_executions ne ON lc.execution_id = ne.id
                WHERE ne.graph_run_id = ?
                ORDER BY lc.timestamp
            """, (graph_run_id,))
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def get_execution_by_id(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific execution by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM node_executions 
                WHERE id = ?
            """, (execution_id,))
            row = cursor.fetchone()
            if row:
                return dict(zip([col[0] for col in cursor.description], row))
            return None
    
    def update_execution_with_llm_data(self, execution_id: str, total_tokens: int, estimated_cost: float):
        """Update execution with aggregated LLM data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE node_executions 
                SET total_tokens = ?, estimated_cost = ?
                WHERE id = ?
            """, (total_tokens, estimated_cost, execution_id))
            conn.commit()