"""
End-to-End Test with Real OpenAI Agent
Tests TimeMachine with actual LLM API calls in a 3-node agent
"""
import sys
import os
import warnings
from pathlib import Path

# Suppress LangGraph warnings
warnings.filterwarnings("ignore", message="The 'config' parameter should be typed")

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import timemachine
from timemachine.replay import CounterfactualEngine

# Load environment variables from root .env file
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("[SKIP] No OpenAI API key found - skipping real agent test")
    exit(0)


class RealAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str
    analysis: str


def research_node(state: RealAgentState):
    """Node 1: Research the topic"""
    print(f"[NODE 1] Researching: {state['topic']}")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    research_prompt = f"Provide 3 key facts about {state['topic']}. Be concise."
    
    response = llm.invoke([HumanMessage(research_prompt)])
    
    return {
        "messages": [response],
        "analysis": response.content
    }


def analyze_node(state: RealAgentState):
    """Node 2: Analyze the research"""
    print(f"[NODE 2] Analyzing research...")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    analysis_prompt = f"Based on this research: {state['analysis']}\nWhat are the main implications?"
    
    response = llm.invoke([HumanMessage(analysis_prompt)])
    
    return {
        "messages": [response],
        "analysis": state['analysis'] + "\n\nAnalysis: " + response.content
    }


def synthesize_node(state: RealAgentState):
    """Node 3: Create final synthesis"""
    print(f"[NODE 3] Creating synthesis...")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    synthesis_prompt = f"Summarize this analysis in 2 sentences: {state['analysis']}"
    
    response = llm.invoke([HumanMessage(synthesis_prompt)])
    
    return {
        "messages": [response]
    }


@timemachine.record("test/test_real_agent_e2e.db")
def create_real_agent():
    """Create a 3-node agent that makes real LLM calls"""
    workflow = StateGraph(RealAgentState)
    
    workflow.add_node("research", research_node)
    workflow.add_node("analyze", analyze_node) 
    workflow.add_node("synthesize", synthesize_node)
    
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow


def test_real_agent_recording():
    """Test that real agent executions get recorded"""
    print("\n[TEST] Real Agent Recording")
    print("=" * 40)
    
    try:
        agent = create_real_agent()
        
        # Run with real topic
        result = agent.invoke({
            "messages": [HumanMessage("Let's research this topic")],
            "topic": "artificial intelligence",
            "analysis": ""
        })
        
        print(f"[PASS] Agent completed successfully")
        print(f"Final messages: {len(result['messages'])}")
        print(f"Has analysis: {bool(result.get('analysis'))}")
        
        # Show actual AI responses
        print(f"\n[DEBUG] AI Responses:")
        for i, msg in enumerate(result['messages']):
            if hasattr(msg, 'content'):
                print(f"  Message {i+1}: {msg.content}")
        
        # Show final analysis
        if result.get('analysis'):
            print(f"\n[DEBUG] Final Analysis: {result['analysis']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Agent execution failed: {e}")
        return False


def test_real_counterfactuals():
    """Test counterfactual analysis with real recorded execution"""
    print("\n[TEST] Real Counterfactual Analysis")
    print("=" * 40)
    
    try:
        # Get the most recent execution
        recorder = timemachine.TimeMachineRecorder("test/test_real_agent_e2e.db")
        runs = recorder.list_graph_runs()
        
        if not runs:
            print("[FAIL] No recorded runs found")
            return False
        
        latest_run = runs[0]
        executions = recorder.get_graph_executions(latest_run['graph_run_id'])
        
        if len(executions) < 3:
            print(f"[FAIL] Expected 3 executions, got {len(executions)}")
            return False
        
        # Show recorded execution details
        print(f"\n[DEBUG] Recorded Executions:")
        for i, exec_data in enumerate(executions):
            node_name = exec_data.get('node_name', 'unknown')
            status = exec_data.get('status', 'unknown')
            duration = exec_data.get('duration_ms', 0)
            print(f"  Execution {i+1}: {node_name} ({status}, {duration}ms)")
            
            # Show input/output state snippets
            input_state = exec_data.get('input_state', '')
            output_state = exec_data.get('output_state', '')
            print(f"    Input: {input_state}")
            print(f"    Output: {output_state}")
        
        print(f"\n[DEBUG] Testing counterfactuals on execution: {executions[0]['id']}")
        print(f"[DEBUG] Available functions in recorder registry: {list(recorder.function_registry.keys())}")
        
        # Get function registry from global decorator reference
        try:
            timemachine_graph = create_real_agent._timemachine_graph
            print(f"[DEBUG] Available functions in timemachine_graph registry: {list(timemachine_graph.function_registry.keys())}")
            replay_engine = timemachine.ReplayEngine(recorder)
            replay_engine._function_registry = timemachine_graph.function_registry
            print(f"[DEBUG] Assigned function registry to replay engine: {list(replay_engine._function_registry.keys())}")
            engine = CounterfactualEngine(replay_engine)
        except AttributeError:
            print("[DEBUG] No _timemachine_graph attribute found")
            replay_engine = timemachine.ReplayEngine(recorder)
            engine = CounterfactualEngine(replay_engine)
        
        # Test temperature sensitivity on the research node
        research_execution = executions[0]  # First node
        execution_id = research_execution['id']
        temp_analysis = engine.analyze_temperature_sensitivity(
            execution_id, 
            [0.1, 0.9]  # Conservative vs creative
        )
        
        print(f"[INFO] Tested {len(temp_analysis.scenarios)} temperature scenarios")

        
        # Show detailed scenario results
        print(f"\n[DEBUG] Temperature Scenario Results:")
        for i, scenario_result in enumerate(temp_analysis.scenarios):
            temp = scenario_result.scenario.modifications.get('temperature', 'unknown')
            success_status = "SUCCESS" if scenario_result.replay_result.success else "FAILED"
            print(f"  Scenario {i+1} (temp={temp}): {success_status}")
            
            if scenario_result.replay_result.success:
                original = str(scenario_result.replay_result.original_output)
                replayed = str(scenario_result.replay_result.replayed_output)
                print(f"    Original: {original}")
                print(f"    Replayed: {replayed}")
        
        # Show insights
        print(f"\n[DEBUG] Analysis Insights:")
        for insight in temp_analysis.insights:
            print(f"  - {insight}")
        
        success = len(temp_analysis.scenarios) == 2
        print(f"\n[{'PASS' if success else 'FAIL'}] Temperature analysis completed")
        
        return success
        
    except Exception as e:
        print(f"[FAIL] Counterfactual analysis failed: {e}")
        return False


def test_model_alternatives():
    """Test model comparison with real execution"""
    print("\n[TEST] Real Model Alternatives")
    print("=" * 40)
    
    try:
        recorder = timemachine.TimeMachineRecorder("test/test_real_agent_e2e.db")
        runs = recorder.list_graph_runs()
        
        if not runs:
            print("[FAIL] No recorded runs found")
            return False
        
        latest_run = runs[0]
        executions = recorder.get_graph_executions(latest_run['graph_run_id'])
        
        print(f"\n[DEBUG] Testing model alternatives on execution: {executions[-1]['id']}")
        
        # Test model alternatives on synthesis node (simpler task)
        synthesis_execution = executions[-1]  # Last node
        execution_id = synthesis_execution['id']
        
        # Get function registry from global decorator reference
        try:
            timemachine_graph = create_real_agent._timemachine_graph
            replay_engine = timemachine.ReplayEngine(recorder)
            replay_engine._function_registry = timemachine_graph.function_registry
            engine = CounterfactualEngine(replay_engine)
        except AttributeError:
            # Fallback to regular engine if no registry available
            replay_engine = timemachine.ReplayEngine(recorder)
            engine = CounterfactualEngine(replay_engine)
        model_analysis = engine.analyze_model_alternatives(
            execution_id,
            ["gpt-3.5-turbo", "gpt-4o-mini"]  # Two real models
        )
        
        print(f"[INFO] Tested {len(model_analysis.scenarios)} model alternatives")
        
        # Show detailed model comparison results
        print(f"\n[DEBUG] Model Comparison Results:")
        for i, scenario_result in enumerate(model_analysis.scenarios):
            model = scenario_result.scenario.modifications.get('model_name', 'unknown')
            success_status = "SUCCESS" if scenario_result.replay_result.success else "FAILED"
            print(f"  Scenario {i+1} ({model}): {success_status}")
            
            if scenario_result.replay_result.success:
                original = str(scenario_result.replay_result.original_output)
                replayed = str(scenario_result.replay_result.replayed_output)
                print(f"    Original: {original}")
                print(f"    Replayed: {replayed}")
        
        # Show recommendations
        print(f"\n[DEBUG] Model Analysis Recommendations:")
        for rec in model_analysis.recommendations:
            print(f"  - {rec}")
        
        success = len(model_analysis.scenarios) == 2
        print(f"\n[{'PASS' if success else 'FAIL'}] Model analysis completed")
        
        return success
        
    except Exception as e:
        print(f"[FAIL] Model alternatives failed: {e}")
        return False


def run_real_agent_tests():
    """Run end-to-end tests with real OpenAI agent"""
    print("[TEST] Real Agent End-to-End Test Suite")
    print("=" * 60)
    
    tests = [
        test_real_agent_recording,
        test_real_counterfactuals,
        test_model_alternatives
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} crashed: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n[INFO] Real Agent Test Results:")
    print(f"  Passed: {passed}/{total}")
    print(f"  Success rate: {passed/total*100:.1f}%")
    
    return passed == total


if __name__ == "__main__":
    success = run_real_agent_tests()
    print(f"\n{'[PASS] REAL AGENT TESTS PASSED' if success else '[FAIL] SOME REAL AGENT TESTS FAILED'}")
