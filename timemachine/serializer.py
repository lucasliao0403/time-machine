"""
State Serialization for TimeMachine
Handles complex LangGraph state objects for storage
"""
import json
from typing import Any, Dict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


class StateSerializer:
    """Serializes LangGraph state objects to/from JSON"""
    
    def serialize_state(self, state: Any) -> str:
        """Convert LangGraph state to JSON string for storage"""
        if isinstance(state, dict):
            return self._serialize_dict(state)
        elif hasattr(state, '__dict__'):
            return self._serialize_object(state)
        else:
            return json.dumps(state, default=self._json_serializer)
    
    def deserialize_state(self, serialized_state: str) -> Any:
        """Convert JSON string back to LangGraph state"""
        try:
            data = json.loads(serialized_state)
            return self._deserialize_dict(data)
        except (json.JSONDecodeError, TypeError):
            return serialized_state
    
    def _serialize_dict(self, state_dict: Dict[str, Any]) -> str:
        """Handle complex state dictionaries with messages"""
        serialized = {}
        for key, value in state_dict.items():
            if key == "messages" and isinstance(value, list):
                # Special handling for LangChain messages
                serialized[key] = [self._serialize_message(msg) for msg in value]
            else:
                serialized[key] = value
        return json.dumps(serialized, default=self._json_serializer)
    
    def _serialize_object(self, obj: Any) -> str:
        """Serialize objects with __dict__ attribute"""
        return json.dumps(obj.__dict__, default=self._json_serializer)
    
    def _serialize_message(self, message: BaseMessage) -> Dict[str, Any]:
        """Serialize LangChain message objects"""
        return {
            "_type": message.__class__.__name__,
            "content": message.content,
            "additional_kwargs": getattr(message, 'additional_kwargs', {}),
            "response_metadata": getattr(message, 'response_metadata', {}),
        }
    
    def _deserialize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize dictionary, handling special message types"""
        result = {}
        for key, value in data.items():
            if key == "messages" and isinstance(value, list):
                result[key] = [self._deserialize_message(msg) for msg in value]
            else:
                result[key] = value
        return result
    
    def _deserialize_message(self, msg_data: Dict[str, Any]) -> BaseMessage:
        """Deserialize LangChain message objects"""
        msg_type = msg_data.get("_type", "BaseMessage")
        content = msg_data.get("content", "")
        additional_kwargs = msg_data.get("additional_kwargs", {})
        
        # Map message types to classes
        message_classes = {
            "HumanMessage": HumanMessage,
            "AIMessage": AIMessage,
            "SystemMessage": SystemMessage,
        }
        
        message_class = message_classes.get(msg_type, HumanMessage)
        return message_class(content=content, additional_kwargs=additional_kwargs)
    
    def _json_serializer(self, obj: Any) -> str:
        """Default JSON serializer for unknown objects"""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
