"""
Basic functionality test for TimeMachine
Tests core node wrapping and recording capabilities
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import timemachine

# Simple test state
class TestState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    counter: int

def test_node_1(state: TestState):
    """First test node"""
    print(f"Node 1: counter = {state.get('counter', 0)}")
    return {
        "messages": [HumanMessage("From node 1")],
        "counter": state.get('counter', 0) + 1
    }

def test_node_2(state: TestState):
    """Second test node"""
    print(f"Node 2: counter = {state.get('counter', 0)}")
    return {
        "messages": [HumanMessage("From node 2")],
        "counter": state.get('counter', 0) + 10
    }

def cleanup_test_files():
    """Clean up test database files"""
    db_files = ["test/test_basic.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"[CLEANUP] Removed {db_file}")
            except Exception as e:
                print(f"[WARNING] Could not remove {db_file}: {e}")

def test_basic_recording():
    """Test basic TimeMachine recording functionality"""
    db_path = "test/test_basic.db"
    
    print("[TEST] Testing Basic TimeMachine Recording")
    print("=" * 40)
    
    try:
        # Create a simple graph
        graph = StateGraph(TestState)
        graph.add_node("node1", test_node_1)
        graph.add_node("node2", test_node_2)
        graph.add_edge(START, "node1")
        graph.add_edge("node1", "node2")
        graph.add_edge("node2", END)
        
        # Wrap with TimeMachine
        tm_graph = timemachine.TimeMachineGraph(graph, db_path)
        agent = tm_graph.compile()
        
        # Test execution
        result = agent.invoke({"messages": [], "counter": 0})
        
        print(f"Final result: {result}")
        
        # Check recordings
        recorder = tm_graph.get_recorder()
        runs = recorder.list_graph_runs()
        print(f"Recorded {len(runs)} graph runs")
        
        success = False
        if runs:
            graph_run_id = runs[0]['graph_run_id']
            executions = recorder.get_graph_executions(graph_run_id)
            print(f"Graph run {graph_run_id[:8]}... had {len(executions)} node executions:")
            for execution in executions:
                print(f"  - {execution['node_name']}: {execution['status']}")
            
            success = len(runs) > 0 and len(executions) == 2
        
        return success
    
    finally:
        # Always cleanup, even if test fails
        cleanup_test_files()

if __name__ == "__main__":
    success = test_basic_recording()
    print(f"\n{'[PASS] Test PASSED' if success else '[FAIL] Test FAILED'}")
