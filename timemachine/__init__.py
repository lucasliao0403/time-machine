# TimeMachine - Time-travel debugger for LangGraph agents
# Phase 2.5 Simplified API - Focus on "what if" games only

# Phase 1: Core Recording
from .core.recorder import TimeMachineRecorder
from .core.wrapper import TimeMachineNodeWrapper, TimeMachineGraph, wrap_graph
from .core.serializer import StateSerializer
from .core.decorator import record, recording

# Phase 2.5: Only Counterfactual Analysis
from .replay.engine import ReplayEngine
from .replay.counterfactual import CounterfactualEngine

__all__ = [
    # Core recording
    'TimeMachineRecorder',
    'TimeMachineNodeWrapper', 
    'TimeMachineGraph',
    'StateSerializer',
    'record',
    'recording',
    'wrap_graph',
    
    # Counterfactual "what if" analysis only
    'ReplayEngine',
    'CounterfactualEngine'
]

__version__ = "0.2.5"
