#!/usr/bin/env python3
"""
Function Registry for TimeMachine Web Backend
Provides access to node functions for counterfactual analysis
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str

def first_step(state: ChatState):
    """Demo first step function"""
    user_input = "artificial intelligence"
    print(f"[REPLAY] Topic selected: {user_input}")
    user_message = HumanMessage(content=user_input)
    return {"messages": [user_message], "topic": user_input}

def second_step(state: ChatState):
    """Demo second step function"""
    topic = state["topic"]
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    prompt = HumanMessage(content=f"Tell me one fascinating fact about {topic}")
    response = llm.invoke([prompt])
    print(f"[REPLAY] Generated fact about {topic}")
    return {"messages": [response]}

# Function registry that the backend can import
FUNCTION_REGISTRY = {
    'step1': first_step,
    'step2': second_step
}

def get_function_registry():
    """Get the function registry for counterfactual analysis"""
    return FUNCTION_REGISTRY
