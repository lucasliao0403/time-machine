"""
Demo test showing TimeMachine integration with the sample agent
This demonstrates how TimeMachine works with the actual sample_agent.py
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
load_dotenv()

# Import the original sample agent components
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Import TimeMachine
import timemachine

# Use the same state schema as sample_agent.py
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str

# Mock versions of the sample agent functions for testing
def mock_first_step(state: ChatState):
    """Mock first step - simulates user input"""
    # Simulate user input without actually prompting
    user_input = "artificial intelligence"
    user_message = HumanMessage(content=user_input)
    return {
        "messages": [user_message], 
        "topic": user_input
    }

def mock_second_step(state: ChatState):
    """Mock second step - simulates LLM response"""
    topic = state["topic"]
    
    # Mock LLM response instead of calling OpenAI
    mock_response = f"Here's a fascinating fact about {topic}: AI systems can process and analyze vast amounts of data much faster than humans, enabling breakthroughs in fields like medicine, climate research, and space exploration."
    
    response = AIMessage(content=mock_response)
    print(f"\nHere's a fascinating fact about {topic}:")
    print(response.content)
    
    return {"messages": [response]}

# Method 1: Using the decorator (recommended)
@timemachine.record("test/test_demo_decorator.db")
def create_recorded_agent():
    """Create agent with TimeMachine recording enabled"""
    chat_graph = StateGraph(ChatState)
    chat_graph.add_node("step1", mock_first_step)
    chat_graph.add_node("step2", mock_second_step)
    chat_graph.add_edge(START, "step1")
    chat_graph.add_edge("step1", "step2")
    chat_graph.add_edge("step2", END)
    return chat_graph

# Method 2: Using direct wrapping
def create_regular_agent():
    """Create regular agent without recording"""
    chat_graph = StateGraph(ChatState)
    chat_graph.add_node("step1", mock_first_step)
    chat_graph.add_node("step2", mock_second_step)
    chat_graph.add_edge(START, "step1")
    chat_graph.add_edge("step1", "step2")
    chat_graph.add_edge("step2", END)
    return chat_graph

def test_decorator_approach():
    """Demo using the @timemachine.record() decorator"""
    print("[DEMO] TimeMachine Demo - Decorator Approach")
    print("=" * 50)
    
    # Create agent with recording
    agent = create_recorded_agent()
    
    # Run the agent
    result = agent.invoke({"messages": [], "topic": ""})
    
    print("\n[PASS] Execution recorded to test/test_demo_decorator.db")
    return result

def test_direct_wrapping():
    """Demo using direct TimeMachineGraph wrapping"""
    print("\n[DEMO] TimeMachine Demo - Direct Wrapping Approach")
    print("=" * 50)
    
    # Create regular graph
    graph = create_regular_agent()
    
    # Wrap with TimeMachine
    tm_graph = timemachine.TimeMachineGraph(graph, "test/test_demo_direct.db")
    agent = tm_graph.compile()
    
    # Run the agent
    result = agent.invoke({"messages": [], "topic": ""})
    
    print("\n[PASS] Execution recorded to test/test_demo_direct.db")
    return result

def test_context_manager():
    """Demo using the context manager approach"""
    print("\n[DEMO] TimeMachine Demo - Context Manager Approach")
    print("=" * 50)
    
    with timemachine.recording("test/test_demo_context.db"):
        agent = create_regular_agent().compile()
        result = agent.invoke({"messages": [], "topic": ""})
    
    print("\n[PASS] Execution recorded to test/test_demo_context.db")
    return result

def show_recordings():
    """Show recorded executions from all demo approaches"""
    print("\n[INFO] Recorded Executions Summary")
    print("=" * 40)
    
    databases = [
        ("test/test_demo_decorator.db", "Decorator Approach"),
        ("test/test_demo_direct.db", "Direct Wrapping"),
        ("test/test_demo_context.db", "Context Manager")
    ]
    
    total_runs = 0
    for db_path, method in databases:
        try:
            recorder = timemachine.TimeMachineRecorder(db_path)
            runs = recorder.list_graph_runs()
            total_runs += len(runs)
            
            print(f"\n{method}:")
            print(f"  Database: {db_path}")
            print(f"  Graph runs: {len(runs)}")
            
            if runs:
                # Show details of latest run
                latest_run = runs[0]
                executions = recorder.get_graph_executions(latest_run['graph_run_id'])
                print(f"  Latest run: {latest_run['graph_run_id'][:8]}...")
                print(f"  Nodes executed: {len(executions)}")
                for execution in executions:
                    print(f"    - {execution['node_name']}: {execution['status']} ({execution['duration_ms']}ms)")
        
        except Exception as e:
            print(f"\n{method}: No recordings found")
    
    return total_runs > 0

def run_all_demos():
    """Run all demo approaches"""
    print("[DEMO] TimeMachine Sample Agent Demo Suite")
    print("=" * 60)
    
    # Test all approaches
    result1 = test_decorator_approach()
    result2 = test_direct_wrapping()
    result3 = test_context_manager()
    
    # Show what was recorded
    has_recordings = show_recordings()
    
    # Verify all approaches worked
    success = (
        result1 and len(result1.get('messages', [])) >= 2 and
        result2 and len(result2.get('messages', [])) >= 2 and
        result3 and len(result3.get('messages', [])) >= 2 and
        has_recordings
    )
    
    return success

if __name__ == "__main__":
    success = run_all_demos()
    print(f"\n{'[PASS] ALL DEMOS PASSED' if success else '[FAIL] SOME DEMOS FAILED'}")
