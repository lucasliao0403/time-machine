"""
LLM Call Tracking for TimeMachine
Detects and records LLM interactions within node executions
"""
import re
import time
import uuid
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from contextlib import contextmanager

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from langchain_openai import ChatOpenAI


@dataclass
class LLMCall:
    """Represents a single LLM API call"""
    id: str
    execution_id: str
    model_name: str
    provider: str  # openai, anthropic, etc.
    temperature: float
    max_tokens: Optional[int]
    prompt: str
    response: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    duration_ms: float
    timestamp: float
    metadata: Dict[str, Any]


class LLMTracker:
    """Tracks LLM calls within TimeMachine node executions"""
    
    def __init__(self, recorder=None):
        self.recorder = recorder
        self.active_calls: Dict[str, LLMCall] = {}
        self.model_costs = self._load_model_costs()
        
    def _load_model_costs(self) -> Dict[str, Dict[str, float]]:
        """Load current model pricing (per 1K tokens)"""
        return {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'gpt-3.5-turbo-1106': {'input': 0.001, 'output': 0.002},
            'claude-3-opus': {'input': 0.015, 'output': 0.075},
            'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
            'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
        }
    
    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a model call"""
        model_pricing = self.model_costs.get(model_name.lower())
        if not model_pricing:
            # Default pricing for unknown models
            return (input_tokens + output_tokens) * 0.002 / 1000
        
        input_cost = (input_tokens / 1000) * model_pricing['input']
        output_cost = (output_tokens / 1000) * model_pricing['output']
        return input_cost + output_cost
    
    def detect_llm_call(self, execution_id: str, node_function: Any, 
                       input_state: Any, output_state: Any) -> List[LLMCall]:
        """Detect LLM calls by analyzing node execution"""
        calls = []
        
        # Method 1: Check if node function uses LangChain LLM directly
        if hasattr(node_function, '__code__'):
            calls.extend(self._analyze_function_code(execution_id, node_function, input_state, output_state))
        
        # Method 2: Check state changes for LLM-like patterns
        calls.extend(self._analyze_state_changes(execution_id, input_state, output_state))
        
        # Method 3: Monitor known LLM objects if accessible
        calls.extend(self._monitor_llm_objects(execution_id))
        
        return calls
    
    def _analyze_function_code(self, execution_id: str, func: Any, 
                              input_state: Any, output_state: Any) -> List[LLMCall]:
        """Analyze function code for LLM usage patterns"""
        calls = []
        
        try:
            import inspect
            source = inspect.getsource(func)
            
            # Look for common LLM patterns
            llm_patterns = [
                r'ChatOpenAI\(',
                r'\.invoke\(',
                r'llm\.',
                r'model\.',
                r'openai\.',
                r'anthropic\.'
            ]
            
            for pattern in llm_patterns:
                if re.search(pattern, source):
                    # Found potential LLM usage - create estimated call
                    call = self._create_estimated_call(execution_id, input_state, output_state, 
                                                     pattern, source)
                    if call:
                        calls.append(call)
                    break
                        
        except Exception:
            # Can't analyze source - skip
            pass
            
        return calls
    
    def _analyze_state_changes(self, execution_id: str, input_state: Any, 
                              output_state: Any) -> List[LLMCall]:
        """Analyze state changes to detect LLM outputs"""
        calls = []
        
        try:
            # Check for new AI messages in output
            input_messages = self._extract_messages(input_state)
            output_messages = self._extract_messages(output_state)
            
            new_messages = output_messages[len(input_messages):]
            
            for msg in new_messages:
                if hasattr(msg, '__class__') and 'AI' in msg.__class__.__name__:
                    # Found new AI message - likely from LLM call
                    call = self._create_call_from_message(execution_id, input_messages, msg)
                    calls.append(call)
                    
        except Exception:
            pass
            
        return calls
    
    def _extract_messages(self, state: Any) -> List[BaseMessage]:
        """Extract messages from state"""
        if isinstance(state, dict) and 'messages' in state:
            messages = state['messages']
            if isinstance(messages, list):
                return messages
        return []
    
    def _create_estimated_call(self, execution_id: str, input_state: Any, 
                              output_state: Any, pattern: str, source: str) -> Optional[LLMCall]:
        """Create estimated LLM call from code analysis"""
        try:
            # Estimate model from source code
            model_name = "gpt-3.5-turbo"  # Default
            if 'gpt-4' in source.lower():
                model_name = "gpt-4"
            elif 'claude' in source.lower():
                model_name = "claude-3-sonnet"
            
            # Estimate tokens from content
            input_messages = self._extract_messages(input_state)
            output_messages = self._extract_messages(output_state)
            
            input_text = " ".join([getattr(msg, 'content', '') for msg in input_messages])
            new_messages = output_messages[len(input_messages):]
            output_text = " ".join([getattr(msg, 'content', '') for msg in new_messages])
            
            input_tokens = self._estimate_tokens(input_text)
            output_tokens = self._estimate_tokens(output_text)
            
            cost = self.calculate_cost(model_name, input_tokens, output_tokens)
            
            return LLMCall(
                id=str(uuid.uuid4()),
                execution_id=execution_id,
                model_name=model_name,
                provider=self._get_provider(model_name),
                temperature=0.7,  # Default
                max_tokens=None,
                prompt=input_text,
                response=output_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost_usd=cost,
                duration_ms=100.0,  # Estimated
                timestamp=time.time(),
                metadata={'detection_method': 'code_analysis', 'pattern': pattern}
            )
            
        except Exception:
            return None
    
    def _create_call_from_message(self, execution_id: str, input_messages: List, 
                                 ai_message: Any) -> LLMCall:
        """Create LLM call record from AI message"""
        input_text = " ".join([getattr(msg, 'content', '') for msg in input_messages])
        output_text = getattr(ai_message, 'content', '')
        
        # Try to extract model info from message metadata
        model_name = "gpt-3.5-turbo"  # Default
        metadata = getattr(ai_message, 'response_metadata', {})
        if 'model_name' in metadata:
            model_name = metadata['model_name']
        elif 'model' in metadata:
            model_name = metadata['model']
        
        input_tokens = self._estimate_tokens(input_text)
        output_tokens = self._estimate_tokens(output_text)
        cost = self.calculate_cost(model_name, input_tokens, output_tokens)
        
        return LLMCall(
            id=str(uuid.uuid4()),
            execution_id=execution_id,
            model_name=model_name,
            provider=self._get_provider(model_name),
            temperature=0.7,  # Default
            max_tokens=None,
            prompt=input_text,
            response=output_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost,
            duration_ms=100.0,  # Estimated
            timestamp=time.time(),
            metadata={'detection_method': 'message_analysis', 'response_metadata': metadata}
        )
    
    def _monitor_llm_objects(self, execution_id: str) -> List[LLMCall]:
        """Monitor known LLM objects for calls (advanced)"""
        # This would require monkey-patching LLM classes
        # For Phase 2, we'll keep it simple and return empty
        return []
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        if not text:
            return 0
        # Rough estimate: ~4 characters per token for English
        return max(1, len(text) // 4)
    
    def _get_provider(self, model_name: str) -> str:
        """Get provider from model name"""
        model_name = model_name.lower()
        if 'gpt' in model_name or 'openai' in model_name:
            return 'openai'
        elif 'claude' in model_name:
            return 'anthropic'
        elif 'gemini' in model_name:
            return 'google'
        else:
            return 'unknown'
    
    def save_llm_call(self, call: LLMCall):
        """Save LLM call to database"""
        if self.recorder:
            self.recorder.save_llm_call(call)
    
    def get_calls_for_execution(self, execution_id: str) -> List[LLMCall]:
        """Get all LLM calls for a specific execution"""
        if self.recorder:
            return self.recorder.get_llm_calls(execution_id)
        return []
    
    @contextmanager
    def track_execution(self, execution_id: str):
        """Context manager for tracking LLM calls during execution"""
        try:
            yield self
        finally:
            # Cleanup any tracking state
            if execution_id in self.active_calls:
                del self.active_calls[execution_id]
