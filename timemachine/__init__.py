# TimeMachine - Time-travel debugger for LangGraph agents
# Main API - imports from reorganized modules

# Phase 1: Core Recording
from .core.recorder import TimeMachineRecorder
from .core.wrapper import TimeMachineNodeWrapper, TimeMachineGraph, wrap_graph
from .core.serializer import StateSerializer
from .core.decorator import record, recording

# Phase 2: Analysis and Replay (importing new features)
from .analysis.llm_tracker import LLMTracker
from .analysis.cost_analyzer import CostAnalyzer
from .analysis.patterns import PatternDetector
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
    
    # Analysis
    'LLMTracker',
    'CostAnalyzer', 
    'PatternDetector',
    
    # Replay
    'ReplayEngine',
    'CounterfactualEngine'
]

__version__ = "0.2.0"
