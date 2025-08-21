"""
Replay Engine for TimeMachine - Phase 2.5 Simplified
Replays recorded executions with optional modifications
Focus on essential replay functionality for counterfactual analysis
"""
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from copy import deepcopy

from ..core.serializer import StateSerializer


@dataclass
class ReplayResult:
    """Result of a replay execution"""
    original_execution_id: str
    replay_id: str
    original_output: Any
    replayed_output: Any
    changes_made: List[str]
    success: bool
    error: Optional[str]
    duration_ms: float
    cost_difference: float  # Simplified - not actively calculated in 2.5


@dataclass
class ReplayConfiguration:
    """Configuration for replay execution"""
    modify_llm_params: Optional[Dict[str, Any]] = None  # temperature, model, etc.
    replace_inputs: Optional[Dict[str, Any]] = None     # Replace specific inputs
    modify_state: Optional[Dict[str, Any]] = None       # Modify state values
    use_cached_responses: bool = True                   # Use cached LLM responses
    record_replay: bool = True                          # Record the replay execution


class ReplayEngine:
    """Engine for replaying recorded executions with modifications"""
    
    def __init__(self, recorder=None, cache=None):
        self.recorder = recorder
        self.cache = cache
        self.serializer = StateSerializer()
        
    def replay_execution(self, execution_id: str, 
                        config: Optional[ReplayConfiguration] = None) -> ReplayResult:
        """Replay a specific node execution with optional modifications"""
        config = config or ReplayConfiguration()
        
        # Get original execution data
        original_execution = self._get_execution(execution_id)
        if not original_execution:
            return ReplayResult(
                original_execution_id=execution_id,
                replay_id="",
                original_output=None,
                replayed_output=None,
                changes_made=[],
                success=False,
                error="Execution not found",
                duration_ms=0.0,
                cost_difference=0.0
            )
        
        try:
            # Prepare replay environment
            input_state = self._prepare_input_state(original_execution, config)
            node_function = self._get_node_function(original_execution['node_name'])
            
            if not node_function:
                raise ValueError(f"Node function '{original_execution['node_name']}' not found")
            
            # Execute replay
            import time
            start_time = time.time()
            
            if config.modify_llm_params:
                replayed_output = self._replay_with_llm_modifications(
                    node_function, input_state, config.modify_llm_params
                )
            else:
                # Handle both plain functions and RunnableCallable objects
                if hasattr(node_function, 'invoke'):
                    replayed_output = node_function.invoke(input_state)
                else:
                    replayed_output = node_function(input_state)
            
            duration = (time.time() - start_time) * 1000
            
            # Analyze results
            original_output = self.serializer.deserialize_state(original_execution['output_state'])
            changes_made = self._get_changes_made(config)
            
            # Cost tracking simplified in Phase 2.5
            cost_diff = 0.0
            
            return ReplayResult(
                original_execution_id=execution_id,
                replay_id=f"replay_{execution_id}_{int(time.time())}",
                original_output=original_output,
                replayed_output=replayed_output,
                changes_made=changes_made,
                success=True,
                error=None,
                duration_ms=duration,
                cost_difference=cost_diff
            )
            
        except Exception as e:
            return ReplayResult(
                original_execution_id=execution_id,
                replay_id="",
                original_output=None,
                replayed_output=None,
                changes_made=[],
                success=False,
                error=str(e),
                duration_ms=0.0,
                cost_difference=0.0
            )
    
    def replay_graph_run(self, graph_run_id: str, 
                        config: Optional[ReplayConfiguration] = None) -> List[ReplayResult]:
        """Replay an entire graph execution"""
        executions = self._get_graph_executions(graph_run_id)
        results = []
        
        for execution in executions:
            result = self.replay_execution(execution['id'], config)
            results.append(result)
        
        return results
    
    def _prepare_input_state(self, execution: Dict, config: ReplayConfiguration) -> Any:
        """Prepare input state for replay with modifications"""
        input_state = self.serializer.deserialize_state(execution['input_state'])
        
        # Apply state modifications
        if config.modify_state:
            input_state = self._apply_state_modifications(input_state, config.modify_state)
        
        # Apply input replacements
        if config.replace_inputs:
            input_state = self._apply_input_replacements(input_state, config.replace_inputs)
        
        return input_state
    
    def _apply_state_modifications(self, state: Any, modifications: Dict[str, Any]) -> Any:
        """Apply modifications to state"""
        if isinstance(state, dict):
            modified_state = deepcopy(state)
            for key, value in modifications.items():
                if '.' in key:
                    # Nested key like "metadata.user_id"
                    self._set_nested_value(modified_state, key, value)
                else:
                    modified_state[key] = value
            return modified_state
        return state
    
    def _set_nested_value(self, obj: Dict, key_path: str, value: Any):
        """Set nested dictionary value using dot notation"""
        keys = key_path.split('.')
        current = obj
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _apply_input_replacements(self, state: Any, replacements: Dict[str, Any]) -> Any:
        """Apply input replacements to state"""
        if isinstance(state, dict) and 'messages' in state:
            modified_state = deepcopy(state)
            messages = modified_state['messages']
            
            for i, replacement in replacements.items():
                if isinstance(i, str) and i.isdigit():
                    idx = int(i)
                    if 0 <= idx < len(messages):
                        # Replace message content
                        if hasattr(messages[idx], 'content'):
                            messages[idx].content = replacement
            
            return modified_state
        return state
    
    def _replay_with_llm_modifications(self, node_function: Any, input_state: Any, 
                                     llm_modifications: Dict[str, Any]) -> Any:
        """Replay with LLM parameter modifications"""
        # This is a simplified approach - in practice, you'd need to:
        # 1. Identify LLM calls within the node function
        # 2. Intercept those calls
        # 3. Apply the modifications
        # 4. Execute with modified parameters
        
        # For now, we'll monkey-patch common LLM classes
        original_methods = {}
        
        try:
            # Patch ChatOpenAI if available
            try:
                from langchain_openai import ChatOpenAI
                original_methods['ChatOpenAI.invoke'] = ChatOpenAI.invoke
                
                def modified_invoke(self, *args, **kwargs):
                    # Apply modifications
                    if 'temperature' in llm_modifications:
                        self.temperature = llm_modifications['temperature']
                    if 'model_name' in llm_modifications:
                        self.model_name = llm_modifications['model_name']
                    if 'max_tokens' in llm_modifications:
                        self.max_tokens = llm_modifications['max_tokens']
                    
                    return original_methods['ChatOpenAI.invoke'](self, *args, **kwargs)
                
                ChatOpenAI.invoke = modified_invoke
                
            except ImportError:
                pass
            
            # Execute the node function  
            if hasattr(node_function, 'invoke'):
                result = node_function.invoke(input_state)
            else:
                result = node_function(input_state)
            return result
            
        finally:
            # Restore original methods
            for method_path, original_method in original_methods.items():
                class_name, method_name = method_path.split('.')
                if class_name == 'ChatOpenAI':
                    try:
                        from langchain_openai import ChatOpenAI
                        setattr(ChatOpenAI, method_name, original_method)
                    except ImportError:
                        pass
    
    def _get_node_function(self, node_name: str) -> Optional[Any]:
        """Get the original node function from global registry"""
        # Try to get from explicitly set function registry
        if hasattr(self, '_function_registry') and node_name in self._function_registry:
            return self._function_registry[node_name]
        
        # Try to get from recorder if available
        if self.recorder and hasattr(self.recorder, 'function_registry'):
            function = self.recorder.function_registry.get(node_name)
            if function:
                return function
        
        # Try to get from recorder's get_node_function method
        if self.recorder and hasattr(self.recorder, 'get_node_function'):
            function = self.recorder.get_node_function(node_name)
            if function:
                return function
        
        # Try to get from global decorator registry
        try:
            from ..core.decorator import record
            if hasattr(record, '_global_registry'):
                for db_path, timemachine_graph in record._global_registry.items():
                    if hasattr(timemachine_graph, 'function_registry'):
                        function = timemachine_graph.function_registry.get(node_name)
                        if function:
                            return function
        except ImportError:
            pass
        
        return None
    

    
    def _calculate_cost_difference(self, execution_id: str, config: ReplayConfiguration) -> float:
        """Calculate cost difference between original and replay - simplified in Phase 2.5"""
        # Cost analysis removed in Phase 2.5 simplification
        return 0.0
    
    def _get_changes_made(self, config: ReplayConfiguration) -> List[str]:
        """Get list of changes made during replay"""
        changes = []
        
        if config.modify_llm_params:
            for param, value in config.modify_llm_params.items():
                changes.append(f"Modified LLM {param} to {value}")
        
        if config.replace_inputs:
            changes.append(f"Replaced {len(config.replace_inputs)} input(s)")
        
        if config.modify_state:
            changes.append(f"Modified {len(config.modify_state)} state value(s)")
        
        return changes
    
    def _get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution data from recorder"""
        if not self.recorder:
            return None
        
        # Get execution by ID from recorder
        return self.recorder.get_execution_by_id(execution_id)
    
    def _get_graph_executions(self, graph_run_id: str) -> List[Dict]:
        """Get all executions for a graph run"""
        if not self.recorder:
            return []
        # This would be implemented in the recorder
        return []
