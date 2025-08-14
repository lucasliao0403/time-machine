#!/usr/bin/env python3
"""
Quick Demo: Record sample_agent.py with TimeMachine
Minimal changes to your existing agent
"""

import os
from dotenv import load_dotenv
load_dotenv()

import timemachine
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str

def first_step(state: ChatState):
    # Use mock input for demo (no user interaction needed)
    user_input = "artificial intelligence"  # You can change this
    print(f"[NODE 1] Topic selected: {user_input}")
    
    user_message = HumanMessage(content=user_input)
    return {"messages": [user_message], "topic": user_input}

def second_step(state: ChatState):
    topic = state["topic"]
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    
    prompt = HumanMessage(content=f"Tell me one fascinating fact about {topic}")
    response = llm.invoke([prompt])
    
    print(f"[NODE 2] Generated fact about {topic}:")
    print(f"Response: {response.content}")
    
    return {"messages": [response]}

# 🎯 ADD TIMEMACHINE: Just wrap your graph creation with the decorator
@timemachine.record("quick_demo.db")
def create_agent():
    chat_graph = StateGraph(ChatState)
    chat_graph.add_node("step1", first_step)
    chat_graph.add_node("step2", second_step)
    chat_graph.add_edge(START, "step1")
    chat_graph.add_edge("step1", "step2")
    chat_graph.add_edge("step2", END)
    return chat_graph

if __name__ == "__main__":
    print("🎯 TimeMachine Quick Demo")
    print("=" * 30)
    
    # Create and run - automatically recorded!
    agent = create_agent()
    result = agent.invoke({"messages": [], "topic": ""})
    
    print("\n✅ Done! Check quick_demo.db for recordings")
    print("🌐 View in web UI: cd web && python backend.py && npm run dev")
