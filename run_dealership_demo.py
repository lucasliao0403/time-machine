#!/usr/bin/env python3
"""
Simple demo runner for the dealership agent with better error handling
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Check for API key first
if not os.getenv("OPENAI_API_KEY"):
    print("❌ ERROR: OpenAI API key not found!")
    print("Please set OPENAI_API_KEY environment variable.")
    exit(1)

from dealership_customer_support_agent import create_dealership_agent

def run_simple_demo():
    """Run a simple automated demo without user input"""
    print("🚗 Running Automated Dealership Demo")
    print("=" * 50)
    
    try:
        # Create the agent
        agent = create_dealership_agent()
        
        # Initialize with proper state
        initial_state = {
            "messages": [],
            "customer_id": None,
            "customer_info": None,
            "inquiry_type": None,
            "current_context": "Starting conversation",
            "agent_notes": "New conversation started",
            "needs_human_agent": False,
            "conversation_summary": "",
            "detected_intent": "",
            "recommended_actions": []
        }
        
        print("✅ Agent created successfully")
        print("✅ Initial state prepared")
        print("📊 Recording will be saved to: dealership_customer_support.db")
        
        # For now, just test that the agent can be created and compiled
        print("✅ Demo setup complete - agent is ready for interactive use")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_simple_demo()
    
    if success:
        print("\n🎯 Agent is ready! Run the full demo with:")
        print("   python dealership_customer_support_agent.py")
    else:
        print("\n❌ Demo setup failed")
