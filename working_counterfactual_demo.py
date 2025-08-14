#!/usr/bin/env python3
"""
Working Counterfactual Demo
Shows how to record an agent AND run counterfactuals with proper function access
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
    user_input = "artificial intelligence"
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

@timemachine.record("working_demo.db")
def create_agent():
    chat_graph = StateGraph(ChatState)
    chat_graph.add_node("step1", first_step)
    chat_graph.add_node("step2", second_step)
    chat_graph.add_edge(START, "step1")
    chat_graph.add_edge("step1", "step2")
    chat_graph.add_edge("step2", END)
    return chat_graph

def run_recording_and_counterfactuals():
    print("🎯 Recording Agent...")
    print("=" * 30)
    
    # Create and run agent - this stores functions in memory
    agent = create_agent()
    result = agent.invoke({"messages": [], "topic": ""})
    
    print("\n✅ Recording complete!")
    
    # Get the TimeMachine graph instance that has the function registry
    timemachine_graph = create_agent._timemachine_graph
    print(f"Functions available: {list(timemachine_graph.function_registry.keys())}")
    
    # Now set up counterfactual analysis with access to functions
    print("\n🧪 Running Counterfactual Analysis...")
    print("=" * 40)
    
    from timemachine.replay.engine import ReplayEngine
    from timemachine.replay.counterfactual import CounterfactualEngine
    
    # Create replay engine and give it access to the function registry
    replay_engine = ReplayEngine(timemachine_graph.recorder)
    replay_engine._function_registry = timemachine_graph.function_registry
    
    # Create counterfactual engine
    engine = CounterfactualEngine(replay_engine)
    
    # Get the latest execution to test on
    runs = timemachine_graph.recorder.list_graph_runs()
    executions = timemachine_graph.recorder.get_graph_executions(runs[0]['graph_run_id'])
    
    # Test temperature sensitivity on the second step (the AI generation)
    second_step_exec = next(e for e in executions if e['node_name'] == 'step2')
    print(f"Testing counterfactuals on execution: {second_step_exec['id']}")
    
    # Run temperature analysis
    temp_analysis = engine.analyze_temperature_sensitivity(
        second_step_exec['id'], 
        [0.1, 0.5, 0.9]
    )
    
    print(f"\n📊 Results:")
    print(f"Scenarios tested: {len(temp_analysis.scenarios)}")
    print(f"Successful scenarios: {sum(1 for s in temp_analysis.scenarios if s.replay_result.success)}")
    
    for i, scenario in enumerate(temp_analysis.scenarios):
        temp = scenario.scenario.modifications.get('temperature')
        success = "✅" if scenario.replay_result.success else "❌"
        diff = scenario.replay_result.output_difference_score
        print(f"  {success} Temperature {temp}: difference={diff:.3f}")
        
        if scenario.replay_result.success:
            original = str(scenario.replay_result.original_output)[:100]
            replayed = str(scenario.replay_result.replayed_output)[:100]
            print(f"    Original: {original}...")
            print(f"    Replayed: {replayed}...")
        else:
            print(f"    Error: {scenario.replay_result.error}")
    
    print(f"\nBest scenario: {temp_analysis.best_scenario.scenario.name if temp_analysis.best_scenario else 'None'}")
    print("\n🎉 Counterfactual analysis complete!")

if __name__ == "__main__":
    run_recording_and_counterfactuals()
