"""
Test TimeMachine context manager
Tests the 'with timemachine.recording():' context manager functionality
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

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str

def simple_step_1(state: ChatState):
    """Simple first step"""
    return {
        "messages": [HumanMessage("Hello from step 1")],
        "topic": "testing"
    }

def simple_step_2(state: ChatState):
    """Simple second step"""
    topic = state["topic"]
    return {
        "messages": [AIMessage(f"Response about {topic} from step 2")]
    }

def create_regular_agent():
    """Create regular agent without recording"""
    chat_graph = StateGraph(ChatState)
    chat_graph.add_node("step1", simple_step_1)
    chat_graph.add_node("step2", simple_step_2)
    chat_graph.add_edge(START, "step1")
    chat_graph.add_edge("step1", "step2")
    chat_graph.add_edge("step2", END)
    return chat_graph.compile()

def cleanup_test_files():
    """Clean up test database files"""
    db_files = ["test/test_context.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"[CLEANUP] Removed {db_file}")
            except Exception as e:
                print(f"[WARNING] Could not remove {db_file}: {e}")

def test_context_manager():
    """Test context manager approach"""
    db_path = "test/test_context.db"
    
    print("[TEST] TimeMachine Context Manager Test")
    print("=" * 40)
    
    try:
        with timemachine.recording(db_path):
            agent = create_regular_agent()
            result = agent.invoke({"messages": [], "topic": ""})
        
        print(f"[PASS] Context manager execution completed!")
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
            print(f"Graph run {graph_run_id[:8]}... had {len(executions)} node executions")
            
            for execution in executions:
                print(f"  - {execution['node_name']}: {execution['status']}")
            
            success = len(executions) >= 2 and all(e['status'] == 'success' for e in executions)
        
        return success
        
    except Exception as e:
        print(f"[FAIL] Context manager test failed: {e}")
        return False
    
    finally:
        # Always cleanup, even if test fails
        cleanup_test_files()

if __name__ == "__main__":
    success = test_context_manager()
    print(f"\n{'[PASS] Test PASSED' if success else '[FAIL] Test FAILED'}")
