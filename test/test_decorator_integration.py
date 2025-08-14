"""
Test TimeMachine decorator integration
Tests the @timemachine.record() decorator functionality
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import timemachine

# Mock the agent functionality for testing without LLM calls
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str

def mock_first_step(state: ChatState):
    """Mock first step - no user input required"""
    topic = "python"  # Hardcoded for testing
    user_message = HumanMessage(content=topic)
    return {
        "messages": [user_message], 
        "topic": topic
    }

def mock_second_step(state: ChatState):
    """Mock second step - no LLM call required"""
    topic = state["topic"]
    # Mock LLM response
    response = AIMessage(content=f"Python is a versatile programming language! Here's a fact about {topic}: Python was named after Monty Python's Flying Circus.")
    return {"messages": [response]}

@timemachine.record("test/test_decorator.db")
def create_test_agent():
    """Create agent with TimeMachine recording enabled"""
    chat_graph = StateGraph(ChatState)
    chat_graph.add_node("step1", mock_first_step)
    chat_graph.add_node("step2", mock_second_step)
    chat_graph.add_edge(START, "step1")
    chat_graph.add_edge("step1", "step2")
    chat_graph.add_edge("step2", END)
    return chat_graph

def cleanup_test_files():
    """Clean up test database files"""
    db_files = ["test/test_decorator.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"[CLEANUP] Removed {db_file}")
            except Exception as e:
                print(f"[WARNING] Could not remove {db_file}: {e}")

def test_decorator_integration():
    """Test decorator integration"""
    db_path = "test/test_decorator.db"
    
    print("[TEST] TimeMachine Decorator Integration Test")
    print("=" * 40)
    
    try:
        # Create and run agent
        agent = create_test_agent()
        result = agent.invoke({"messages": [], "topic": ""})
        
        print(f"[PASS] Agent execution completed!")
        print(f"Final messages: {len(result['messages'])}")
        print(f"Final topic: {result['topic']}")
        
        # Check recordings
        recorder = timemachine.TimeMachineRecorder(db_path)
        runs = recorder.list_graph_runs()
        print(f"\n[INFO] Recorded {len(runs)} graph runs")
        
        success = False
        if runs:
            graph_run_id = runs[0]['graph_run_id']
            executions = recorder.get_graph_executions(graph_run_id)
            print(f"\nGraph run {graph_run_id[:8]}... details:")
            print(f"  - Total nodes executed: {len(executions)}")
            
            for execution in executions:
                print(f"  - Node: {execution['node_name']}")
                print(f"    Status: {execution['status']}")
                print(f"    Duration: {execution['duration_ms']}ms")
                if execution['error_message']:
                    print(f"    Error: {execution['error_message']}")
            
            success = len(executions) >= 2 and all(e['status'] == 'success' for e in executions)
        
        return success
    
    finally:
        # Always cleanup, even if test fails
        cleanup_test_files()

if __name__ == "__main__":
    success = test_decorator_integration()
    print(f"\n{'[PASS] Test PASSED' if success else '[FAIL] Test FAILED'}")
