# Two-Step LangGraph Agent for TimeMachine
#
# LangGraph agents are built by:
# 1. Define state (what data flows between nodes)
# 2. Create node functions (the actual logic)
# 3. Build graph (connect nodes with edges)
# 4. Compile and run
#
# Memory: LangGraph state automatically persists data between nodes!

# Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# Import LangGraph and LangChain components
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Step 1: Define state schema
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # Message history (automatic memory!)
    topic: str  # Topic from first step (passed to second step)

# Step 2: Create node functions
def first_step(state: ChatState):
    """First node: Ask user for their favorite topic."""
    # Ask user for input
    print("What's your favorite topic to learn about?")
    user_input = input("> ")
    
    # Store user's response as the topic
    user_message = HumanMessage(content=user_input)
    
    return {
        "messages": [user_message], 
        "topic": user_input  # Store topic for next step
    }

def second_step(state: ChatState):
    """Second node: Generate response about the user's topic."""
    topic = state["topic"]  # Get topic from previous step
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    
    # Create prompt using the user's topic
    prompt = HumanMessage(content=f"Tell me one fascinating fact about {topic}")
    response = llm.invoke([prompt])
    
    print(f"\nHere's a fascinating fact about {topic}:")
    print(response.content)
    
    return {"messages": [response]}  # Add to conversation

# Step 3: Build the graph
chat_graph = StateGraph(ChatState)  # Initialize graph with state schema
chat_graph.add_node("step1", first_step)  # Add first step
chat_graph.add_node("step2", second_step)  # Add second step
chat_graph.add_edge(START, "step1")  # Connect start to step 1
chat_graph.add_edge("step1", "step2")  # Connect step 1 to step 2
chat_graph.add_edge("step2", END)  # Connect step 2 to end

# Step 4: Compile the graph into executable agent
chat_agent = chat_graph.compile()

# Run the two-step agent
if __name__ == "__main__":
    print("🤖 Two-Step Agent Demo")
    print("=" * 30)
    
    # Run the agent (will prompt for input and show response)
    result = chat_agent.invoke({"messages": [], "topic": ""})
