"""
TimeMachine Decorator Interface
Provides easy integration with existing LangGraph code
"""
from typing import Callable, Any, Optional
from functools import wraps
from langgraph.graph import StateGraph

from .wrapper import TimeMachineGraph


def record(db_path: str = "timemachine_recordings.db"):
    """
    Decorator to enable TimeMachine recording for LangGraph agents
    
    Usage:
        @timemachine.record()
        def create_my_agent():
            graph = StateGraph(MyState)
            # ... add nodes and edges ...
            return graph.compile()
    
    Or:
        @timemachine.record("custom_recordings.db")
        def create_my_agent():
            # ... 
            return graph.compile()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Execute the original function to get the graph
            result = func(*args, **kwargs)
            
            # If result is a StateGraph, wrap it and compile
            if isinstance(result, StateGraph):
                timemachine_graph = TimeMachineGraph(result, db_path)
                
                # Store global reference for function registry access
                wrapper._timemachine_graph = timemachine_graph
                
                # Also store in a global registry for replay access
                if not hasattr(record, '_global_registry'):
                    record._global_registry = {}
                record._global_registry[db_path] = timemachine_graph
                
                return timemachine_graph.compile()
            
            # If result is already compiled, we need to access the original graph
            # This is a more complex case - for now, return as-is with a warning
            print("Warning: TimeMachine works best when applied to StateGraph before compilation")
            return result
            
        return wrapper
    return decorator


def wrap_compiled_graph(compiled_graph: Any, db_path: str = "timemachine_recordings.db") -> Any:
    """
    Wrap an already compiled LangGraph for recording
    
    Usage:
        agent = create_my_agent()
        recorded_agent = timemachine.wrap_compiled_graph(agent)
    """
    # This is more complex as we need to access internals of compiled graph
    # For Phase 1, we'll focus on the decorator approach
    print("Warning: wrap_compiled_graph not yet implemented. Use @record decorator instead.")
    return compiled_graph


class RecordingContext:
    """Context manager for TimeMachine recording"""
    
    def __init__(self, db_path: str = "timemachine_recordings.db"):
        self.db_path = db_path
        self.original_compile_methods = {}
    
    def __enter__(self):
        """Patch StateGraph.compile to add recording"""
        self.original_compile = StateGraph.compile
        
        # Store original method as class attribute for TimeMachineGraph to access
        StateGraph._original_compile = self.original_compile
        
        def patched_compile(self_graph):
            # Avoid recursive wrapping by checking if already instrumented
            if hasattr(self_graph, '_timemachine_instrumented'):
                return self.original_compile(self_graph)
            
            # Mark as instrumented to prevent recursion
            self_graph._timemachine_instrumented = True
            timemachine_graph = TimeMachineGraph(self_graph, self.db_path)
            return timemachine_graph.compile()
        
        StateGraph.compile = patched_compile
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original compile method"""
        StateGraph.compile = self.original_compile
        # Clean up the stored reference
        if hasattr(StateGraph, '_original_compile'):
            delattr(StateGraph, '_original_compile')


def recording(db_path: str = "timemachine_recordings.db") -> RecordingContext:
    """
    Context manager for TimeMachine recording
    
    Usage:
        with timemachine.recording():
            agent = create_my_agent()
            result = agent.invoke({"messages": [], "topic": ""})
    """
    return RecordingContext(db_path)
