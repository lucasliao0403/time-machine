"""
Test Phase 2: LLM Tracking functionality
Tests LLM call detection and cost analysis
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from timemachine.analysis.llm_tracker import LLMTracker, LLMCall
from timemachine.analysis.cost_analyzer import CostAnalyzer
from timemachine.core.recorder import TimeMachineRecorder


class TestState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str


def mock_llm_node(state: TestState):
    """Mock node that simulates LLM usage"""
    topic = state.get('topic', 'AI')
    # Simulate LLM response
    response = AIMessage(
        content=f"Here's information about {topic}: It's a fascinating subject with many applications.",
        response_metadata={'model': 'gpt-3.5-turbo', 'finish_reason': 'stop'}
    )
    return {"messages": [response]}


def test_llm_call_detection():
    """Test LLM call detection from state changes"""
    print("[TEST] LLM Call Detection")
    print("=" * 40)
    
    tracker = LLMTracker()
    
    # Simulate input and output states
    input_state = {
        "messages": [HumanMessage("Tell me about AI")],
        "topic": "AI"
    }
    
    output_state = {
        "messages": [
            HumanMessage("Tell me about AI"),
            AIMessage("AI is fascinating...", response_metadata={'model': 'gpt-3.5-turbo'})
        ],
        "topic": "AI"
    }
    
    # Detect LLM calls
    calls = tracker.detect_llm_call("exec_123", mock_llm_node, input_state, output_state)
    
    success = len(calls) > 0
    if success:
        call = calls[0]
        print(f"  Detected LLM call: {call.model_name}")
        print(f"  Input tokens: {call.input_tokens}")
        print(f"  Output tokens: {call.output_tokens}")
        print(f"  Estimated cost: ${call.cost_usd:.4f}")
    
    return success


def test_cost_calculation():
    """Test cost calculation for different models"""
    print("\n[TEST] Cost Calculation")
    print("=" * 40)
    
    tracker = LLMTracker()
    
    test_cases = [
        {'model': 'gpt-4', 'input': 1000, 'output': 500, 'expected_range': (0.04, 0.06)},
        {'model': 'gpt-3.5-turbo', 'input': 1000, 'output': 500, 'expected_range': (0.002, 0.004)},
        {'model': 'claude-3-sonnet', 'input': 1000, 'output': 500, 'expected_range': (0.008, 0.012)},
    ]
    
    all_passed = True
    for case in test_cases:
        cost = tracker.calculate_cost(case['model'], case['input'], case['output'])
        min_expected, max_expected = case['expected_range']
        
        passed = min_expected <= cost <= max_expected
        all_passed = all_passed and passed
        
        print(f"  {case['model']}: ${cost:.4f} {'[PASS]' if passed else '[FAIL]'}")
    
    return all_passed


def test_cost_analyzer():
    """Test cost analysis functionality"""
    print("\n[TEST] Cost Analysis")
    print("=" * 40)
    
    # Create mock LLM calls
    calls = [
        LLMCall(
            id="call_1", execution_id="exec_1", model_name="gpt-4", provider="openai",
            temperature=0.7, max_tokens=None, prompt="Test prompt 1", response="Test response 1",
            input_tokens=100, output_tokens=50, total_tokens=150,
            cost_usd=0.0045, duration_ms=1200, timestamp=1234567890, metadata={}
        ),
        LLMCall(
            id="call_2", execution_id="exec_2", model_name="gpt-3.5-turbo", provider="openai",
            temperature=0.7, max_tokens=None, prompt="Test prompt 2", response="Test response 2",
            input_tokens=200, output_tokens=100, total_tokens=300,
            cost_usd=0.0006, duration_ms=800, timestamp=1234567891, metadata={}
        )
    ]
    
    analyzer = CostAnalyzer()
    
    # Simulate getting calls (would normally come from recorder)
    original_get_calls = analyzer._get_llm_calls
    analyzer._get_llm_calls = lambda graph_run_id=None, time_period=None: calls
    
    try:
        breakdown = analyzer.analyze_costs()
        
        success = (
            breakdown.total_calls == 2 and
            breakdown.total_cost > 0 and
            len(breakdown.cost_by_model) == 2 and
            len(breakdown.optimization_suggestions) >= 0
        )
        
        print(f"  Total calls: {breakdown.total_calls}")
        print(f"  Total cost: ${breakdown.total_cost:.4f}")
        print(f"  Models used: {list(breakdown.cost_by_model.keys())}")
        print(f"  Suggestions: {len(breakdown.optimization_suggestions)}")
        
        return success
        
    finally:
        analyzer._get_llm_calls = original_get_calls


def test_pattern_detection():
    """Test pattern detection in LLM usage"""
    print("\n[TEST] Pattern Detection")
    print("=" * 40)
    
    from timemachine.analysis.patterns import PatternDetector
    
    # Create mock data with patterns
    executions = [
        {'id': 'exec_1', 'node_name': 'node1', 'duration_ms': 1000, 'status': 'success'},
        {'id': 'exec_2', 'node_name': 'node2', 'duration_ms': 6000, 'status': 'success'},  # Slow
        {'id': 'exec_3', 'node_name': 'node3', 'duration_ms': 500, 'status': 'error'},    # Error
    ]
    
    llm_calls = [
        LLMCall(
            id="call_1", execution_id="exec_1", model_name="gpt-4", provider="openai",
            temperature=0.7, max_tokens=None, prompt="Expensive prompt", response="Response",
            input_tokens=2500, output_tokens=1500, total_tokens=4000,  # High tokens
            cost_usd=0.12, duration_ms=1200, timestamp=1234567890, metadata={}
        ),
    ]
    
    detector = PatternDetector()
    
    # Mock the data retrieval methods
    detector._get_executions = lambda graph_run_id=None, time_period=None: executions
    detector._get_llm_calls = lambda graph_run_id=None, time_period=None: llm_calls
    
    summary = detector.detect_patterns()
    
    success = (
        summary.total_patterns > 0 and
        len(summary.patterns_by_category) > 0 and
        len(summary.top_recommendations) >= 0
    )
    
    print(f"  Total patterns detected: {summary.total_patterns}")
    print(f"  Critical issues: {summary.critical_issues}")
    print(f"  High priority: {summary.high_priority}")
    print(f"  Categories: {list(summary.patterns_by_category.keys())}")
    
    return success


def test_integration_with_recorder():
    """Test integration between LLM tracking and recorder"""
    print("\n[TEST] Integration with Recorder")
    print("=" * 40)
    
    # Create temporary recorder
    recorder = TimeMachineRecorder("test/test_phase2_integration.db")
    tracker = LLMTracker(recorder)
    
    # Create a mock LLM call
    llm_call = LLMCall(
        id="integration_call_1",
        execution_id="integration_exec_1",
        model_name="gpt-3.5-turbo",
        provider="openai",
        temperature=0.7,
        max_tokens=None,
        prompt="Integration test prompt",
        response="Integration test response",
        input_tokens=50,
        output_tokens=25,
        total_tokens=75,
        cost_usd=0.0002,
        duration_ms=500,
        timestamp=1234567890,
        metadata={'test': True}
    )
    
    try:
        # Save LLM call
        tracker.save_llm_call(llm_call)
        
        # Retrieve LLM calls
        retrieved_calls = tracker.get_calls_for_execution("integration_exec_1")
        
        success = len(retrieved_calls) > 0
        print(f"  Saved and retrieved LLM call: {'[PASS]' if success else '[FAIL]'}")
        
        return success
        
    except Exception as e:
        print(f"  Integration test failed: {e}")
        return False


def run_all_phase2_tests():
    """Run all Phase 2 tests"""
    print("[TEST] TimeMachine Phase 2 Test Suite")
    print("=" * 60)
    
    tests = [
        test_llm_call_detection,
        test_cost_calculation,
        test_cost_analyzer,
        test_pattern_detection,
        test_integration_with_recorder
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n[INFO] Phase 2 Test Results:")
    print(f"  Passed: {passed}/{total}")
    print(f"  Success rate: {passed/total*100:.1f}%")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_phase2_tests()
    print(f"\n{'[PASS] ALL PHASE 2 TESTS PASSED' if success else '[FAIL] SOME PHASE 2 TESTS FAILED'}")
