"""
TimeMachine Node and Graph Wrappers
Wraps LangGraph nodes and graphs for execution recording
"""
import time
import uuid
from typing import Any, Dict, Optional, Callable
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph

from .recorder import TimeMachineRecorder


class TimeMachineNodeWrapper:
    """Wraps a LangGraph node function to record execution"""
    
    def __init__(self, original_node_func: Callable, node_name: str, 
                 recorder: TimeMachineRecorder, graph_run_id: Optional[str] = None):
        self.original_func = original_node_func
        self.node_name = node_name
        self.recorder = recorder
        self.graph_run_id = graph_run_id or str(uuid.uuid4())
        
        # Preserve original function attributes
        if hasattr(original_node_func, '__name__'):
            self.__name__ = original_node_func.__name__
        if hasattr(original_node_func, '__doc__'):
            self.__doc__ = original_node_func.__doc__
    
    def __call__(self, state: Any, config: Optional[Dict] = None) -> Any:
        """Execute the wrapped node with recording"""
        # Record execution start
        execution_id = self.recorder.start_execution(
            node_name=self.node_name,
            input_state=state,
            graph_run_id=self.graph_run_id,
            timestamp=time.time()
        )
        
        try:
            # Execute original node function
            start_time = time.time()
            
            # Handle both function and Runnable types
            if hasattr(self.original_func, 'invoke'):
                # It's a Runnable object
                result = self.original_func.invoke(state, config)
            elif callable(self.original_func):
                # It's a direct function
                result = self.original_func(state, config) if config else self.original_func(state)
            else:
                raise TypeError(f"Node function is not callable: {type(self.original_func)}")
                
            duration = time.time() - start_time
            
            # Record successful completion
            self.recorder.complete_execution(
                execution_id=execution_id,
                output_state=result,
                duration_ms=duration * 1000,
                status="success"
            )
            
            return result
            
        except Exception as e:
            # Record failure
            self.recorder.complete_execution(
                execution_id=execution_id,
                status="error",
                error=str(e)
            )
            raise


class TimeMachineGraph:
    """Wraps a LangGraph StateGraph to enable node-level recording"""
    
    def __init__(self, original_graph: StateGraph, 
                 db_path: str = "timemachine_recordings.db"):
        self.original_graph = original_graph
        self.recorder = TimeMachineRecorder(db_path)
        self.graph_run_id = str(uuid.uuid4())
        self.function_registry = {}  # Store node functions for replay
        self._is_instrumented = False
    
    def instrument_graph(self):
        """Wrap all nodes in the graph before compilation for recording"""
        if self._is_instrumented:
            # Temporarily restore original compile method if patched by context manager
            original_compile = getattr(self.original_graph.__class__, '_original_compile', None)
            if original_compile:
                return original_compile(self.original_graph)
            else:
                return self.original_graph.compile()
        
        # Create a new StateGraph with wrapped nodes
        from langgraph.graph.state import StateGraph
        
        # Create new graph with same state type
        new_graph = StateGraph(self.original_graph.schema)
        
        # Copy all nodes with wrapping
        for node_name, node_spec in self.original_graph.nodes.items():
            if hasattr(node_spec, 'runnable') and node_spec.runnable is not None:
                original_func = node_spec.runnable
                
                # Store function in registries for replay
                self.function_registry[node_name] = original_func
                self.recorder.register_node_function(node_name, original_func)
                
                # Create wrapped version
                wrapped_func = TimeMachineNodeWrapper(
                    original_node_func=original_func,
                    node_name=node_name,
                    recorder=self.recorder,
                    graph_run_id=self.graph_run_id
                )
                
                # Add wrapped node to new graph
                new_graph.add_node(node_name, wrapped_func)
        
        # Copy all edges
        for edge in self.original_graph.edges:
            # Handle both tuple format and object format
            if isinstance(edge, tuple):
                source, target = edge
                new_graph.add_edge(source, target)
            else:
                new_graph.add_edge(edge.source, edge.target)
        
        # Copy conditional edges if any
        if hasattr(self.original_graph, 'conditional_edges'):
            for conditional_edge in self.original_graph.conditional_edges:
                new_graph.add_conditional_edges(
                    conditional_edge.source,
                    conditional_edge.condition,
                    conditional_edge.conditional_edge_mapping
                )
        
        # Copy entry and finish points
        if hasattr(self.original_graph, '_entry_point'):
            new_graph._entry_point = self.original_graph._entry_point
        if hasattr(self.original_graph, '_finish_point'):
            new_graph._finish_point = self.original_graph._finish_point
            
        self._is_instrumented = True
        
        # Compile the new graph
        return new_graph.compile()
    
    def compile(self) -> Any:
        """Compile the graph with instrumentation"""
        return self.instrument_graph()
    
    def get_recorder(self) -> TimeMachineRecorder:
        """Get the recorder instance for this graph"""
        return self.recorder
    
    def get_graph_run_id(self) -> str:
        """Get the current graph run ID"""
        return self.graph_run_id


def wrap_graph(graph: StateGraph, db_path: str = "timemachine_recordings.db") -> TimeMachineGraph:
    """Convenience function to wrap a StateGraph"""
    return TimeMachineGraph(graph, db_path)
