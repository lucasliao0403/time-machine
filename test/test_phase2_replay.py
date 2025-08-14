"""
Test Phase 2.5: Simplified Replay and Counterfactual functionality
Tests only the essential "what if" counterfactual analysis
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph.message import add_messages

from timemachine.replay.engine import ReplayEngine, ReplayConfiguration, ReplayResult
from timemachine.replay.counterfactual import CounterfactualEngine, CounterfactualScenario, CounterfactualType
from timemachine.core.recorder import TimeMachineRecorder
from timemachine.core.serializer import StateSerializer


class TestState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str


def simple_test_node(state: TestState):
    """Simple test node function"""
    topic = state.get('topic', 'test')
    return {
        "messages": [AIMessage(f"Processed topic: {topic}")],
        "topic": topic
    }


def test_replay_configuration():
    """Test replay configuration creation and validation"""
    print("[TEST] Replay Configuration")
    print("=" * 40)
    
    # Test basic configuration
    config = ReplayConfiguration(
        modify_llm_params={'temperature': 0.5, 'model_name': 'gpt-4'},
        replace_inputs={'0': 'Modified input'},
        use_cached_responses=True
    )
    
    success = (
        config.modify_llm_params is not None and
        config.replace_inputs is not None and
        config.use_cached_responses == True
    )
    
    print(f"  Configuration created: {'[PASS]' if success else '[FAIL]'}")
    print(f"  LLM params: {config.modify_llm_params}")
    print(f"  Input replacements: {config.replace_inputs}")
    
    return success


def test_replay_engine_basic():
    """Test basic replay engine functionality"""
    print("\n[TEST] Replay Engine Basic")
    print("=" * 40)
    
    # Create mock recorder
    recorder = TimeMachineRecorder("test/test_replay_basic.db")
    
    # Create replay engine
    engine = ReplayEngine(recorder)
    
    # Mock execution data
    mock_execution = {
        'id': 'test_exec_1',
        'node_name': 'test_node',
        'input_state': '{"messages": [], "topic": "test"}',
        'output_state': '{"messages": [{"content": "Original response"}], "topic": "test"}',
        'status': 'success'
    }
    
    # Mock the get_execution method
    original_get_execution = engine._get_execution
    engine._get_execution = lambda exec_id: mock_execution if exec_id == 'test_exec_1' else None
    
    # Mock the get_node_function method to return our test function
    engine._get_node_function = lambda node_name: simple_test_node if node_name == 'test_node' else None
    
    try:
        config = ReplayConfiguration(modify_state={'topic': 'modified_test'})
        result = engine.replay_execution('test_exec_1', config)
        
        success = (
            result.success == True and
            result.original_execution_id == 'test_exec_1' and
            len(result.changes_made) > 0
        )
        
        print(f"  Replay execution: {'[PASS]' if success else '[FAIL]'}")
        print(f"  Changes made: {result.changes_made}")
        print(f"  Success: {result.success}")
        
        return success
        
    except Exception as e:
        print(f"  Replay failed: {e}")
        return False
        
    finally:
        engine._get_execution = original_get_execution


def test_counterfactual_scenarios():
    """Test counterfactual scenario creation"""
    print("\n[TEST] Counterfactual Scenarios")
    print("=" * 40)
    
    # Test scenario creation
    scenario = CounterfactualScenario(
        name="Temperature Test",
        description="What if we used temperature=0.1?",
        type=CounterfactualType.TEMPERATURE_CHANGE,
        modifications={'temperature': 0.1},
        expected_outcome="More deterministic output"
    )
    
    success = (
        scenario.name == "Temperature Test" and
        scenario.type == CounterfactualType.TEMPERATURE_CHANGE and
        'temperature' in scenario.modifications
    )
    
    print(f"  Scenario creation: {'[PASS]' if success else '[FAIL]'}")
    print(f"  Scenario type: {scenario.type}")
    print(f"  Modifications: {scenario.modifications}")
    
    return success


def test_counterfactual_engine():
    """Test counterfactual analysis engine"""
    print("\n[TEST] Counterfactual Engine")
    print("=" * 40)
    
    # Create mock replay engine
    class MockReplayEngine:
        def replay_execution(self, execution_id, config):
            return ReplayResult(
                original_execution_id=execution_id,
                replay_id=f"replay_{execution_id}",
                original_output={"messages": [{"content": "Original"}]},
                replayed_output={"messages": [{"content": "Modified"}]},
                changes_made=["Modified temperature"],
                success=True,
                error=None,
                duration_ms=100.0,
                cost_difference=-0.001,  # Slight savings
                output_difference_score=0.3
            )
    
    engine = CounterfactualEngine(MockReplayEngine())
    
    # Test temperature sensitivity analysis
    comparison = engine.analyze_temperature_sensitivity('test_exec_1', [0.1, 0.7, 1.0])
    
    success = (
        comparison.original_execution_id == 'test_exec_1' and
        len(comparison.scenarios) == 3 and
        comparison.best_scenario is not None
    )
    
    print(f"  Temperature analysis: {'[PASS]' if success else '[FAIL]'}")
    print(f"  Scenarios analyzed: {len(comparison.scenarios)}")
    print(f"  Best scenario: {comparison.best_scenario.scenario.name if comparison.best_scenario else 'None'}")
    print(f"  Recommendations: {len(comparison.recommendations)}")
    
    return success


def test_simple_scenario_analysis():
    """Test simple 'what if' scenario analysis - Phase 2.5 focus"""
    print("\n[TEST] Simple 'What If' Analysis")
    print("=" * 40)
    
    class MockReplayEngine:
        def replay_execution(self, execution_id, config):
            # Simple mock that varies output based on modifications
            output_diff = 0.0
            if config.modify_llm_params:
                if 'temperature' in config.modify_llm_params:
                    temp = config.modify_llm_params['temperature']
                    if temp < 0.3:
                        output_diff = 0.1  # Small change for low temp
                    elif temp > 0.8:
                        output_diff = 0.8  # Big change for high temp
                    else:
                        output_diff = 0.3  # Medium change
                if 'model_name' in config.modify_llm_params:
                    output_diff += 0.2  # Model changes add variance
            
            return ReplayResult(
                original_execution_id=execution_id,
                replay_id=f"replay_{execution_id}",
                original_output={"messages": [{"content": "Original"}]},
                replayed_output={"messages": [{"content": "Modified"}]},
                changes_made=["Parameter modification applied"],
                success=True,
                error=None,
                duration_ms=100.0,
                cost_difference=0.0,  # Not tracking costs in 2.5
                output_difference_score=output_diff
            )
    
    engine = CounterfactualEngine(MockReplayEngine())
    comparison = engine.analyze_temperature_sensitivity('test_exec_1', [0.1, 0.5, 0.9])
    
    success = (
        len(comparison.scenarios) == 3 and
        comparison.best_scenario is not None and
        len(comparison.recommendations) > 0
    )
    
    print(f"  Temperature scenarios: {len(comparison.scenarios)}")
    print(f"  Best scenario: {comparison.best_scenario.scenario.name if comparison.best_scenario else 'None'}")
    print(f"  Recommendations: {len(comparison.recommendations)}")
    
    return success


def test_replay_with_state_modifications():
    """Test replay with state modifications"""
    print("\n[TEST] Replay with State Modifications")
    print("=" * 40)
    
    engine = ReplayEngine()
    serializer = StateSerializer()
    
    # Test state modification logic
    original_state = {
        "messages": [HumanMessage("Original message")],
        "topic": "original_topic",
        "metadata": {"user_id": "123"}
    }
    
    modifications = {
        "topic": "modified_topic",
        "metadata.user_id": "456"
    }
    
    # Mock the preparation method
    modified_state = engine._apply_state_modifications(original_state, modifications)
    
    success = (
        modified_state["topic"] == "modified_topic" and
        modified_state["metadata"]["user_id"] == "456" and
        len(modified_state["messages"]) == 1  # Messages preserved
    )
    
    print(f"  State modifications: {'[PASS]' if success else '[FAIL]'}")
    print(f"  Original topic: {original_state['topic']}")
    print(f"  Modified topic: {modified_state['topic']}")
    print(f"  Nested modification: {modified_state['metadata']['user_id']}")
    
    return success


def run_all_replay_tests():
    """Run all simplified replay and counterfactual tests - Phase 2.5"""
    print("[TEST] TimeMachine Phase 2.5 Simplified Replay Test Suite")
    print("=" * 60)
    
    tests = [
        test_replay_configuration,
        test_replay_engine_basic,
        test_counterfactual_scenarios,
        test_counterfactual_engine,
        test_simple_scenario_analysis,
        test_replay_with_state_modifications
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
    
    print(f"\n[INFO] Phase 2.5 Simplified Test Results:")
    print(f"  Passed: {passed}/{total}")
    print(f"  Success rate: {passed/total*100:.1f}%")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_replay_tests()
    print(f"\n{'[PASS] ALL PHASE 2.5 TESTS PASSED' if success else '[FAIL] SOME PHASE 2.5 TESTS FAILED'}")
