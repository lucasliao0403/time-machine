"""
Test TimeMachine state serialization
Tests the StateSerializer functionality for complex state objects
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph.message import add_messages

from timemachine.serializer import StateSerializer

class ComplexState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str
    count: int
    data: dict

def test_message_serialization():
    """Test serialization of LangChain messages"""
    print("[TEST] Testing Message Serialization")
    print("=" * 40)
    
    serializer = StateSerializer()
    
    # Create test messages
    messages = [
        HumanMessage(content="Hello, how are you?"),
        AIMessage(content="I'm doing well, thank you!", additional_kwargs={"model": "gpt-3.5-turbo"}),
        SystemMessage(content="You are a helpful assistant.")
    ]
    
    # Test serialization
    serialized = serializer.serialize_state({"messages": messages, "topic": "greetings"})
    print(f"Serialized: {len(serialized)} characters")
    
    # Test deserialization
    deserialized = serializer.deserialize_state(serialized)
    print(f"Deserialized messages: {len(deserialized['messages'])}")
    
    # Verify message types are preserved
    success = True
    for orig, deser in zip(messages, deserialized['messages']):
        if type(orig) != type(deser):
            print(f"[FAIL] Type mismatch: {type(orig)} != {type(deser)}")
            success = False
        elif orig.content != deser.content:
            print(f"[FAIL] Content mismatch: {orig.content} != {deser.content}")
            success = False
    
    if success:
        print("[PASS] All message types and content preserved")
    
    return success

def test_complex_state_serialization():
    """Test serialization of complex state objects"""
    print("\n[TEST] Testing Complex State Serialization")
    print("=" * 40)
    
    serializer = StateSerializer()
    
    # Create complex state
    complex_state = {
        "messages": [
            HumanMessage("Test message"),
            AIMessage("Response message", response_metadata={"finish_reason": "stop"})
        ],
        "topic": "testing",
        "count": 42,
        "data": {
            "nested": True,
            "values": [1, 2, 3],
            "config": {"enabled": True}
        }
    }
    
    # Test serialization
    serialized = serializer.serialize_state(complex_state)
    print(f"Serialized complex state: {len(serialized)} characters")
    
    # Test deserialization
    deserialized = serializer.deserialize_state(serialized)
    
    # Verify structure
    success = (
        len(deserialized["messages"]) == 2 and
        deserialized["topic"] == "testing" and
        deserialized["count"] == 42 and
        deserialized["data"]["nested"] == True and
        len(deserialized["data"]["values"]) == 3
    )
    
    if success:
        print("[PASS] Complex state structure preserved")
    else:
        print("[FAIL] Complex state structure not preserved")
        print(f"Deserialized: {deserialized}")
    
    return success

def test_edge_cases():
    """Test serialization edge cases"""
    print("\n[TEST] Testing Serialization Edge Cases")
    print("=" * 40)
    
    serializer = StateSerializer()
    
    # Test empty state
    empty_state = {"messages": [], "topic": ""}
    serialized = serializer.serialize_state(empty_state)
    deserialized = serializer.deserialize_state(serialized)
    
    success1 = len(deserialized["messages"]) == 0 and deserialized["topic"] == ""
    print(f"Empty state: {'[PASS]' if success1 else '[FAIL]'}")
    
    # Test None values
    none_state = {"messages": None, "topic": None}
    try:
        serialized = serializer.serialize_state(none_state)
        deserialized = serializer.deserialize_state(serialized)
        success2 = True
        print("None values: [PASS]")
    except Exception as e:
        print(f"None values: [FAIL] {e}")
        success2 = False
    
    # Test non-dict state
    simple_state = "simple string"
    try:
        serialized = serializer.serialize_state(simple_state)
        deserialized = serializer.deserialize_state(serialized)
        success3 = deserialized == simple_state
        print(f"Simple string: {'[PASS]' if success3 else '[FAIL]'}")
    except Exception as e:
        print(f"Simple string: [FAIL] {e}")
        success3 = False
    
    return success1 and success2 and success3

def run_all_serialization_tests():
    """Run all serialization tests"""
    print("[TEST] TimeMachine Serialization Test Suite")
    print("=" * 50)
    
    test1 = test_message_serialization()
    test2 = test_complex_state_serialization()
    test3 = test_edge_cases()
    
    all_passed = test1 and test2 and test3
    
    print(f"\n[INFO] Test Results:")
    print(f"  Message Serialization: {'[PASS]' if test1 else '[FAIL]'}")
    print(f"  Complex State: {'[PASS]' if test2 else '[FAIL]'}")
    print(f"  Edge Cases: {'[PASS]' if test3 else '[FAIL]'}")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_serialization_tests()
    print(f"\n{'[PASS] ALL TESTS PASSED' if success else '[FAIL] SOME TESTS FAILED'}")
