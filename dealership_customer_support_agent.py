#!/usr/bin/env python3
"""
Comprehensive Dealership Customer Support Agent
Real GPT calls with human-in-the-loop conversation for car dealership customer service

Features:
- 7 distinct conversation steps with GPT-4 calls
- Human agent intervention points
- Mock dealership databases (inventory, customers, service)
- Terminal input/output for realistic conversation flow
- Customer service escalation handling
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Annotated, TypedDict, Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

import timemachine
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# ================================
# MOCK DEALERSHIP DATABASES
# ================================

CUSTOMER_DATABASE = {
    "C001": {
        "name": "Sarah Johnson", 
        "phone": "(555) 123-4567",
        "email": "sarah.johnson@email.com",
        "vehicles": ["2019 Honda Civic - License: ABC123"],
        "service_history": ["Oil change 2024-01-15", "Brake inspection 2023-11-20"],
        "preferred_contact": "phone",
        "loyalty_tier": "Gold"
    },
    "C002": {
        "name": "Mike Rodriguez",
        "phone": "(555) 987-6543", 
        "email": "mike.r@email.com",
        "vehicles": ["2021 Toyota Camry - License: XYZ789"],
        "service_history": ["Tire rotation 2024-02-01"],
        "preferred_contact": "email",
        "loyalty_tier": "Silver"
    }
}

INVENTORY_DATABASE = {
    "2024 Honda Civic": {"price": 28500, "stock": 3, "mpg": "32/42", "features": ["Apple CarPlay", "Honda Sensing", "CVT"]},
    "2024 Toyota Camry": {"price": 31200, "stock": 2, "mpg": "28/39", "features": ["Toyota Safety Sense", "8-inch Display", "Wireless Charging"]},
    "2024 Ford Mustang": {"price": 38900, "stock": 1, "mpg": "21/32", "features": ["SYNC 4", "Performance Package", "Premium Audio"]},
    "2023 Subaru Outback": {"price": 29500, "stock": 4, "mpg": "26/35", "features": ["EyeSight Safety", "All-Wheel Drive", "9.1-inch Screen"]}
}

SERVICE_SLOTS = {
    "2024-12-23": ["9:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"],
    "2024-12-24": ["9:00 AM", "11:00 AM"],  # Holiday hours
    "2024-12-26": ["9:00 AM", "10:30 AM", "1:00 PM", "2:30 PM", "4:00 PM"],
    "2024-12-27": ["9:00 AM", "11:00 AM", "2:00 PM", "3:30 PM"]
}

FINANCING_RATES = {
    "excellent": {"rate": 3.9, "term_years": [3, 4, 5, 6]},
    "good": {"rate": 5.9, "term_years": [3, 4, 5, 6]},
    "fair": {"rate": 8.9, "term_years": [4, 5, 6]},
    "poor": {"rate": 12.9, "term_years": [5, 6]}
}

# ================================
# CONVERSATION STATE
# ================================

class DealershipState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    customer_id: Optional[str]
    customer_info: Optional[Dict]
    inquiry_type: Optional[str]  # "service", "sales", "complaint", "financing"
    current_context: str
    agent_notes: str
    needs_human_agent: bool
    conversation_summary: str
    detected_intent: str
    recommended_actions: List[str]

# ================================
# HELPER FUNCTIONS
# ================================

def parse_gpt_json(response_content: str) -> dict:
    """Robust JSON parsing for GPT responses"""
    try:
        # Clean the response content to extract JSON
        content = response_content.strip()
        
        # Try to find JSON in the response
        if content.startswith('```json'):
            # Extract JSON from code block
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                content = content[start:end]
        elif not content.startswith('{'):
            # Try to find the first { and last }
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                content = content[start:end]
        
        return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[DEBUG] JSON parsing failed: {e}")
        print(f"[DEBUG] Raw content: {response_content[:200]}...")
        return None

def log_node_result(node_name: str, result):
    """Log the result of each node execution"""
    print(f"[DEBUG] Node '{node_name}' completed")
    print(f"[DEBUG] Result type: {type(result)}")
    if result is None:
        print(f"[DEBUG] ❌ Node '{node_name}' returned None!")
    elif isinstance(result, dict):
        print(f"[DEBUG] Result keys: {list(result.keys())}")
        print(f"[DEBUG] ✅ Node '{node_name}' returned valid dict")
    else:
        print(f"[DEBUG] ❌ Node '{node_name}' returned unexpected type: {type(result)}")
    return result

# ================================
# CONVERSATION NODES WITH REAL GPT CALLS
# ================================

def initial_greeting_node(state: DealershipState):
    """Node 1: GPT analyzes customer greeting and identifies intent"""
    print("\n" + "="*60)
    print("🚗 PREMIER AUTO DEALERSHIP - Customer Support")
    print("="*60)
    print(f"[DEBUG] Starting initial_greeting_node with state type: {type(state)}")
    
    # Get customer input
    customer_input = input("\n👋 Customer says: ")
    print(f"\n[SYSTEM] Customer: {customer_input}")
    
    # GPT Call 1: Analyze customer intent and extract information
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    analysis_prompt = f"""
You are a car dealership customer service AI. Analyze this customer message and extract:

Customer message: "{customer_input}"

Respond with a JSON object containing:
1. "intent": The main reason for calling (service, sales, complaint, financing, general_inquiry)
2. "urgency": How urgent this seems (low, medium, high, critical)  
3. "customer_emotion": The customer's emotional state (calm, frustrated, excited, confused, angry)
4. "key_details": Any specific details mentioned (car model, problem, timeline, etc.)
5. "response": A friendly, professional response acknowledging their request

Be professional and helpful. Focus on understanding their needs.
"""
    
    response = llm.invoke([HumanMessage(analysis_prompt)])
    
    analysis = parse_gpt_json(response.content)
    if analysis:
        print(f"\n[AI ANALYSIS] Intent: {analysis.get('intent', 'unknown')}")
        print(f"[AI ANALYSIS] Urgency: {analysis.get('urgency', 'unknown')}")
        print(f"[AI ANALYSIS] Emotion: {analysis.get('customer_emotion', 'unknown')}")
        
        # Display AI response to customer
        ai_response = analysis.get('response', 'Thank you for contacting us. How can I help you today?')
        print(f"\n🤖 Support AI: {ai_response}")
        
        result = {
            "messages": [HumanMessage(customer_input), AIMessage(response.content)],
            "detected_intent": analysis.get('intent', 'general_inquiry'),
            "current_context": f"Customer emotion: {analysis.get('customer_emotion', 'calm')}, Urgency: {analysis.get('urgency', 'medium')}",
            "agent_notes": f"Initial contact - Intent: {analysis.get('intent', 'unknown')}"
        }
        return log_node_result("initial_greeting_node", result)
    else:
        print(f"\n🤖 Support AI: Thank you for contacting Premier Auto Dealership. I'm here to help you today!")
        result = {
            "messages": [HumanMessage(customer_input), AIMessage(response.content)],
            "detected_intent": "general_inquiry",
            "current_context": "Analysis failed - using fallback",
            "agent_notes": "Initial contact - analysis parsing failed"
        }
        return log_node_result("initial_greeting_node", result)

def customer_identification_node(state: DealershipState):
    """Node 2: GPT helps identify customer and retrieve their information"""
    print(f"[DEBUG] Starting customer_identification_node with state type: {type(state)}")
    print(f"\n[SYSTEM] Current context: {state['current_context']}")
    
    # Ask for customer identification
    customer_id_input = input("\n📞 Please provide your phone number or customer ID: ")
    print(f"\n[SYSTEM] Customer provided: {customer_id_input}")
    
    # Simple lookup simulation (in real system, this would be database query)
    found_customer = None
    for cust_id, cust_data in CUSTOMER_DATABASE.items():
        if customer_id_input in cust_data["phone"] or customer_id_input == cust_id:
            found_customer = (cust_id, cust_data)
            break
    
    # GPT Call 2: Generate personalized greeting based on customer data
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4)
    
    if found_customer:
        cust_id, cust_data = found_customer
        personalization_prompt = f"""
You are a car dealership customer service representative. Generate a warm, personalized greeting for this returning customer:

Customer Information:
- Name: {cust_data['name']}
- Loyalty Tier: {cust_data['loyalty_tier']}
- Vehicles: {', '.join(cust_data['vehicles'])}
- Recent Service: {cust_data['service_history'][-1] if cust_data['service_history'] else 'None'}
- Previous Intent: {state.get('detected_intent', 'unknown')}

Create a friendly, professional greeting that:
1. Welcomes them back by name
2. Acknowledges their loyalty status
3. References their vehicle if relevant to their inquiry type
4. Asks how you can help them today

Keep it conversational and not too long.
"""
        
        response = llm.invoke([HumanMessage(personalization_prompt)])
        greeting = response.content
        
        print(f"\n🤖 Support AI: {greeting}")
        
        result = {
            "customer_id": cust_id,
            "customer_info": cust_data,
            "messages": [AIMessage(response.content)],
            "current_context": f"Identified customer: {cust_data['name']} ({cust_data['loyalty_tier']} tier)",
            "agent_notes": state.get("agent_notes", "") + f" | Customer identified: {cust_data['name']}"
        }
        return log_node_result("customer_identification_node", result)
    else:
        new_customer_prompt = f"""
You are a car dealership customer service representative. This appears to be a new customer who provided: "{customer_id_input}"

Generate a professional response that:
1. Politely explains we don't have them in our system yet
2. Asks for their name and contact information
3. Assures them we're happy to help new customers
4. Asks about their specific needs today

Be welcoming and helpful, not apologetic about the system limitation.
"""
        
        response = llm.invoke([HumanMessage(new_customer_prompt)])
        greeting = response.content
        
        print(f"\n🤖 Support AI: {greeting}")
        
        result = {
            "customer_id": None,
            "customer_info": None,
            "messages": [AIMessage(response.content)],
            "current_context": f"New customer - provided: {customer_id_input}",
            "agent_notes": state.get("agent_notes", "") + f" | New customer: {customer_id_input}"
        }
        return log_node_result("customer_identification_node", result)

def detailed_inquiry_node(state: DealershipState):
    """Node 3: GPT conducts detailed inquiry based on detected intent"""
    print(f"\n[SYSTEM] Processing {state.get('detected_intent', 'general')} inquiry...")
    
    # Get detailed information from customer
    detailed_info = input("\n🔍 Please tell me more about what you need help with today: ")
    print(f"\n[SYSTEM] Customer details: {detailed_info}")
    
    # GPT Call 3: Process detailed inquiry and determine next steps
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    customer_context = ""
    if state.get("customer_info"):
        customer_context = f"Customer: {state['customer_info']['name']} ({state['customer_info']['loyalty_tier']} tier)"
    
    detailed_prompt = f"""
You are a car dealership customer service specialist. Analyze this detailed customer inquiry:

{customer_context}
Initial Intent: {state.get('detected_intent', 'unknown')}
Customer Details: "{detailed_info}"

Based on the inquiry, provide a JSON response with:
1. "inquiry_category": Specific category (service_appointment, vehicle_purchase, trade_in, financing, warranty_claim, complaint)
2. "required_information": List of additional info needed to help them
3. "urgency_level": Updated urgency (routine, priority, urgent, emergency)
4. "next_actions": Recommended next steps
5. "response": Professional response acknowledging their needs and explaining next steps

Consider their loyalty tier if applicable and be thorough in your analysis.
"""
    
    response = llm.invoke([HumanMessage(detailed_prompt)])
    
    analysis = parse_gpt_json(response.content)
    if analysis:
        print(f"\n[AI ANALYSIS] Category: {analysis.get('inquiry_category', 'general')}")
        print(f"[AI ANALYSIS] Urgency: {analysis.get('urgency_level', 'routine')}")
        print(f"[AI ANALYSIS] Required info: {', '.join(analysis.get('required_information', []))}")
        
        ai_response = analysis.get('response', 'I understand your request. Let me help you with that.')
        print(f"\n🤖 Support AI: {ai_response}")
        
        return {
            "inquiry_type": analysis.get('inquiry_category', 'general'),
            "messages": [HumanMessage(detailed_info), AIMessage(response.content)],
            "current_context": f"Detailed inquiry: {analysis.get('inquiry_category', 'general')} - {analysis.get('urgency_level', 'routine')}",
            "agent_notes": state.get("agent_notes", "") + f" | Inquiry: {analysis.get('inquiry_category', 'general')}",
            "recommended_actions": analysis.get('next_actions', [])
        }
    else:
        print(f"\n🤖 Support AI: I understand you need help with that. Let me look into the best options for you.")
        return {
            "inquiry_type": "general",
            "messages": [HumanMessage(detailed_info), AIMessage(response.content)],
            "current_context": f"Detailed inquiry received: {detailed_info[:50]}...",
            "agent_notes": state.get("agent_notes", "") + " | Detailed inquiry processed"
        }

def information_processing_node(state: DealershipState):
    """Node 4: GPT processes specific information and provides initial recommendations"""
    print(f"\n[SYSTEM] Processing {state.get('inquiry_type', 'general')} request...")
    
    inquiry_type = state.get('inquiry_type', 'general')
    
    # Get relevant data based on inquiry type
    relevant_data = ""
    if inquiry_type in ['vehicle_purchase', 'trade_in']:
        relevant_data = f"Available inventory: {list(INVENTORY_DATABASE.keys())}"
    elif inquiry_type == 'service_appointment':
        available_dates = list(SERVICE_SLOTS.keys())
        relevant_data = f"Available service dates: {available_dates}"
    elif inquiry_type == 'financing':
        relevant_data = f"Current rates: Excellent credit: {FINANCING_RATES['excellent']['rate']}%, Good credit: {FINANCING_RATES['good']['rate']}%"
    
    # Ask for specific preferences
    preferences = input(f"\n💭 What are your specific preferences or requirements? ")
    print(f"\n[SYSTEM] Customer preferences: {preferences}")
    
    # GPT Call 4: Generate tailored recommendations
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4)
    
    customer_info = state.get('customer_info') or {}
    loyalty_context = f" (valued {customer_info.get('loyalty_tier', 'new')} customer)" if customer_info else ""
    
    processing_prompt = f"""
You are a car dealership specialist processing a {inquiry_type} request.

Customer Context{loyalty_context}:
{f"Customer: {customer_info.get('name', 'New Customer')}" if customer_info else "New Customer"}
{f"Current Vehicles: {', '.join(customer_info.get('vehicles', []))}" if customer_info else ""}

Inquiry Type: {inquiry_type}
Customer Preferences: "{preferences}"
Available Data: {relevant_data}

Provide a JSON response with:
1. "recommendations": List of 2-3 specific recommendations based on their needs
2. "additional_questions": Questions to ask to better serve them
3. "estimated_timeline": How long this process might take
4. "requires_human": true/false if this needs human agent involvement
5. "response": Professional response with your recommendations

Be specific and helpful, considering their loyalty status if applicable.
"""
    
    response = llm.invoke([HumanMessage(processing_prompt)])
    
    analysis = parse_gpt_json(response.content)
    if analysis:
        print(f"\n[AI RECOMMENDATIONS]:")
        for i, rec in enumerate(analysis.get('recommendations', []), 1):
            print(f"  {i}. {rec}")
        
        print(f"\n[AI ANALYSIS] Timeline: {analysis.get('estimated_timeline', 'TBD')}")
        print(f"[AI ANALYSIS] Needs human agent: {analysis.get('requires_human', False)}")
        
        ai_response = analysis.get('response', 'Based on your needs, I have some recommendations for you.')
        print(f"\n🤖 Support AI: {ai_response}")
        
        return {
            "messages": [HumanMessage(preferences), AIMessage(response.content)],
            "current_context": f"Recommendations provided for {inquiry_type}",
            "agent_notes": state.get("agent_notes", "") + f" | Recommendations: {len(analysis.get('recommendations', []))} options",
            "needs_human_agent": analysis.get('requires_human', False),
            "recommended_actions": analysis.get('recommendations', [])
        }
    else:
        print(f"\n🤖 Support AI: Let me find the best options for your {inquiry_type} needs.")
        return {
            "messages": [HumanMessage(preferences), AIMessage(response.content)],
            "current_context": f"Processing {inquiry_type} request",
            "agent_notes": state.get("agent_notes", "") + f" | Processing {inquiry_type}",
            "needs_human_agent": True
        }

def solution_development_node(state: DealershipState):
    """Node 5: GPT develops comprehensive solution with pricing/scheduling"""
    print(f"\n[SYSTEM] Developing comprehensive solution...")
    print(f"[DEBUG] State type: {type(state)}")
    print(f"[DEBUG] State keys: {list(state.keys()) if state else 'None'}")
    
    inquiry_type = state.get('inquiry_type', 'general')
    customer_choice = input(f"\n✅ Which recommendation interests you most? (or ask for more details): ")
    print(f"\n[SYSTEM] Customer choice: {customer_choice}")
    
    # GPT Call 5: Develop detailed solution with specifics
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    # Get relevant pricing/scheduling data
    solution_data = ""
    if inquiry_type == 'vehicle_purchase':
        solution_data = json.dumps(INVENTORY_DATABASE, indent=2)
    elif inquiry_type == 'service_appointment':
        solution_data = json.dumps(SERVICE_SLOTS, indent=2)
    elif inquiry_type == 'financing':
        solution_data = json.dumps(FINANCING_RATES, indent=2)
    
    customer_info = state.get('customer_info') or {}
    
    solution_prompt = f"""
You are a car dealership solutions specialist. Develop a detailed solution for this customer:

Customer: {customer_info.get('name', 'New Customer')} ({customer_info.get('loyalty_tier', 'Standard')} tier)
Inquiry Type: {inquiry_type}
Customer Choice: "{customer_choice}"
Available Data: {solution_data}

Create a JSON response with:
1. "solution_details": Comprehensive solution addressing their choice
2. "pricing": Specific pricing information if applicable
3. "timeline": Detailed timeline for next steps
4. "benefits": Key benefits of this solution for them
5. "next_steps": Specific actions to move forward
6. "requires_approval": true/false if this needs manager/human approval
7. "response": Professional presentation of the complete solution

Consider their loyalty tier for any applicable discounts or priority service.

IMPORTANT: Respond ONLY with valid JSON. Do not include any text before or after the JSON object.
"""
    
    print(f"[DEBUG] About to call GPT with prompt length: {len(solution_prompt)}")
    
    try:
        response = llm.invoke([HumanMessage(solution_prompt)])
        print(f"[DEBUG] GPT response received successfully")
        print(f"[DEBUG] Response type: {type(response)}")
        print(f"[DEBUG] Response has content: {hasattr(response, 'content')}")
        
        if hasattr(response, 'content'):
            print(f"[DEBUG] Content type: {type(response.content)}")
            print(f"[DEBUG] Content length: {len(response.content)}")
            print(f"[DEBUG] Raw GPT response: {response.content[:300]}...")
        else:
            print(f"[DEBUG] Response object: {response}")
            
    except Exception as e:
        print(f"[DEBUG] Error calling GPT: {e}")
        import traceback
        traceback.print_exc()
        return {
            "messages": [HumanMessage(customer_choice), AIMessage("Error occurred during processing")],
            "current_context": f"Error in solution development",
            "agent_notes": state.get("agent_notes", "") + f" | Error: {str(e)}",
            "needs_human_agent": True
        }
    
    print(f"[DEBUG] About to parse JSON...")
    solution = parse_gpt_json(response.content)
    print(f"[DEBUG] JSON parsing completed")
    print(f"[DEBUG] Parsed solution: {solution}")
    print(f"[DEBUG] Solution type: {type(solution)}")
    print(f"[DEBUG] Solution is truthy: {bool(solution)}")
    
    if solution:
        print(f"[DEBUG] Entering solution success branch")
        
        try:
            print(f"[DEBUG] Getting solution_details...")
            solution_details = solution.get('solution_details', 'Custom solution developed')
            print(f"[DEBUG] solution_details: {solution_details}")
            
            print(f"[DEBUG] Getting pricing...")
            pricing = solution.get('pricing')
            print(f"[DEBUG] pricing: {pricing}")
            
            print(f"[DEBUG] Getting timeline...")
            timeline = solution.get('timeline', 'TBD')
            print(f"[DEBUG] timeline: {timeline}")
            
            print(f"[DEBUG] Getting requires_approval...")
            requires_approval = solution.get('requires_approval', False)
            print(f"[DEBUG] requires_approval: {requires_approval}")
            
            print(f"\n[SOLUTION DETAILS]:")
            print(f"  Solution: {solution_details}")
            if pricing:
                print(f"  Pricing: {pricing}")
            print(f"  Timeline: {timeline}")
            print(f"  Requires approval: {requires_approval}")
            
            print(f"[DEBUG] Getting response...")
            ai_response = solution.get('response', 'I\'ve developed a comprehensive solution for your needs.')
            print(f"[DEBUG] ai_response: {ai_response}")
            print(f"\n🤖 Support AI: {ai_response}")
            
            print(f"[DEBUG] Building return dict...")
            print(f"[DEBUG] state type: {type(state)}")
            print(f"[DEBUG] state.get('agent_notes', ''): {state.get('agent_notes', '')}")
            
            return_dict = {
                "messages": [HumanMessage(customer_choice), AIMessage(response.content)],
                "current_context": f"Solution developed for {inquiry_type} - approval needed: {requires_approval}",
                "agent_notes": state.get("agent_notes", "") + f" | Solution: {solution_details[:50] if solution_details else 'Custom'}...",
                "needs_human_agent": requires_approval,
                "conversation_summary": solution_details or ''
            }
            print(f"[DEBUG] Return dict created successfully")
            return return_dict
            
        except Exception as e:
            print(f"[DEBUG] Error in solution success branch: {e}")
            import traceback
            traceback.print_exc()
            return {
                "messages": [HumanMessage(customer_choice), AIMessage(response.content)],
                "current_context": f"Error processing solution",
                "agent_notes": state.get("agent_notes", "") + f" | Error: {str(e)}",
                "needs_human_agent": True
            }
        
    else:
        print(f"[DEBUG] Entering solution fallback branch")
        print(f"\n🤖 Support AI: I've prepared a detailed solution for your {inquiry_type} needs.")
        
        try:
            return_dict = {
                "messages": [HumanMessage(customer_choice), AIMessage(response.content)],
                "current_context": f"Solution developed for {inquiry_type}",
                "agent_notes": state.get("agent_notes", "") + f" | Solution developed",
                "needs_human_agent": True
            }
            print(f"[DEBUG] Fallback return dict created successfully")
            return return_dict
            
        except Exception as e:
            print(f"[DEBUG] Error in fallback branch: {e}")
            import traceback
            traceback.print_exc()
            return {
                "messages": [HumanMessage(customer_choice), AIMessage("Fallback response")],
                "current_context": "Error in fallback",
                "agent_notes": "Error occurred",
                "needs_human_agent": True
            }

def human_agent_consultation_node(state: DealershipState):
    """Node 6: Human agent intervention for complex decisions"""
    if not state.get('needs_human_agent', False):
        print(f"\n[SYSTEM] No human agent needed - proceeding to finalization...")
        return {
            "messages": [AIMessage("Proceeding with automated processing...")],
            "current_context": state.get('current_context', '') + " | No human intervention needed",
            "agent_notes": state.get("agent_notes", "") + " | Automated processing"
        }
    
    print(f"\n" + "="*60)
    print("👨‍💼 HUMAN AGENT INTERVENTION REQUIRED")
    print("="*60)
    print(f"Customer: {state.get('customer_info', {}).get('name', 'New Customer')}")
    print(f"Inquiry: {state.get('inquiry_type', 'general')}")
    print(f"Context: {state.get('current_context', 'N/A')}")
    print(f"Notes: {state.get('agent_notes', 'N/A')}")
    
    # Simulate human agent decision
    human_input = input(f"\n👨‍💼 Human Agent - What's your decision/guidance? ")
    print(f"\n[HUMAN AGENT] Decision: {human_input}")
    
    # GPT Call 6: Human agent communicates decision to customer
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4)
    
    human_agent_prompt = f"""
You are a senior customer service manager at a car dealership. Communicate the human agent's decision to the customer professionally.

Customer Context: {state.get('customer_info', {}).get('name', 'New Customer')}
Inquiry Type: {state.get('inquiry_type', 'general')}
Human Agent Decision: "{human_input}"
Customer Loyalty: {state.get('customer_info', {}).get('loyalty_tier', 'Standard')}

Create a professional response that:
1. Introduces you as the manager/senior agent
2. Explains the decision clearly
3. Emphasizes customer care and relationship
4. Outlines next steps
5. Asks if they have any questions

Be authoritative but friendly, showing that their business is valued.
"""
    
    response = llm.invoke([HumanMessage(human_agent_prompt)])
    
    print(f"\n👨‍💼 Senior Agent: {response.content}")
    
    return {
        "messages": [HumanMessage(human_input), AIMessage(response.content)],
        "current_context": f"Human agent intervention - {human_input[:30]}...",
        "agent_notes": state.get("agent_notes", "") + f" | Human decision: {human_input}",
        "needs_human_agent": False
    }

def conversation_finalization_node(state: DealershipState):
    """Node 7: GPT finalizes conversation with next steps and follow-up"""
    print(f"\n[SYSTEM] Finalizing conversation and next steps...")
    
    # Get final customer satisfaction
    satisfaction = input(f"\n📋 Are you satisfied with the solution we've provided? Any final questions? ")
    print(f"\n[SYSTEM] Customer feedback: {satisfaction}")
    
    # GPT Call 7: Generate comprehensive wrap-up and follow-up plan
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    customer_info = state.get('customer_info') or {}
    
    finalization_prompt = f"""
You are a car dealership customer service representative finalizing a conversation.

Customer Summary:
- Name: {customer_info.get('name', 'New Customer')}
- Loyalty Tier: {customer_info.get('loyalty_tier', 'Standard')}
- Inquiry Type: {state.get('inquiry_type', 'general')}
- Final Feedback: "{satisfaction}"
- Agent Notes: {state.get('agent_notes', 'N/A')}

Create a JSON response with:
1. "follow_up_actions": Specific actions the dealership will take
2. "customer_commitments": What the customer needs to do next
3. "timeline": When things will happen
4. "contact_method": How we'll stay in touch
5. "satisfaction_score": Rate their satisfaction 1-10 based on their feedback
6. "additional_opportunities": Other services they might be interested in
7. "response": Professional closing that summarizes everything and thanks them

Ensure they feel valued and clear about next steps.
"""
    
    response = llm.invoke([HumanMessage(finalization_prompt)])
    
    finalization = parse_gpt_json(response.content)
    if finalization:
        
        print(f"\n[FINALIZATION SUMMARY]:")
        print(f"  Follow-up actions: {', '.join(finalization.get('follow_up_actions', []))}")
        print(f"  Customer next steps: {', '.join(finalization.get('customer_commitments', []))}")
        print(f"  Timeline: {finalization.get('timeline', 'TBD')}")
        print(f"  Satisfaction score: {finalization.get('satisfaction_score', 'N/A')}/10")
        
        ai_response = finalization.get('response', 'Thank you for choosing Premier Auto Dealership. We appreciate your business!')
        print(f"\n🤖 Support AI: {ai_response}")
        
        print(f"\n" + "="*60)
        print("📞 CONVERSATION COMPLETED")
        print("="*60)
        
        return {
            "messages": [HumanMessage(satisfaction), AIMessage(response.content)],
            "current_context": f"Conversation completed - satisfaction: {finalization.get('satisfaction_score', 'N/A')}/10",
            "agent_notes": state.get("agent_notes", "") + f" | Completed - satisfaction: {finalization.get('satisfaction_score', 'N/A')}/10",
            "conversation_summary": finalization.get('response', 'Conversation completed successfully')
        }
    else:
        print(f"\n🤖 Support AI: Thank you for choosing Premier Auto Dealership. We'll follow up with you soon!")
        return {
            "messages": [HumanMessage(satisfaction), AIMessage(response.content)],
            "current_context": "Conversation completed",
            "agent_notes": state.get("agent_notes", "") + " | Conversation finalized"
        }

# ================================
# GRAPH CREATION AND EXECUTION
# ================================

@timemachine.record("dealership_customer_support.db")

def create_dealership_agent():
    """Create the comprehensive dealership customer support agent"""
    workflow = StateGraph(DealershipState)
    
    # Add all conversation nodes
    workflow.add_node("greeting", initial_greeting_node)
    workflow.add_node("identification", customer_identification_node)
    workflow.add_node("inquiry", detailed_inquiry_node)
    workflow.add_node("processing", information_processing_node)
    workflow.add_node("solution", solution_development_node)
    workflow.add_node("human_agent", human_agent_consultation_node)
    workflow.add_node("finalization", conversation_finalization_node)
    
    # Define conversation flow
    workflow.add_edge(START, "greeting")
    workflow.add_edge("greeting", "identification")
    workflow.add_edge("identification", "inquiry")
    workflow.add_edge("inquiry", "processing")
    workflow.add_edge("processing", "solution")
    workflow.add_edge("solution", "human_agent")
    workflow.add_edge("human_agent", "finalization")
    workflow.add_edge("finalization", END)
    
    return workflow

def run_dealership_demo():
    """Run the comprehensive dealership customer support demo"""
    print("🚗 Dealership Customer Support Agent Demo")
    print("=" * 50)
    print("This agent will simulate a real customer service conversation")
    print("with multiple GPT calls and human-in-the-loop intervention.")
    print("=" * 50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OpenAI API key not found!")
        print("Please set OPENAI_API_KEY environment variable.")
        return False
    
    try:
        # Create and run the agent
        agent = create_dealership_agent()
        
        # Initialize conversation state
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
        
        # Run the conversation
        print(f"[DEBUG] About to invoke agent with initial_state: {initial_state}")
        try:
            result = agent.invoke(initial_state)
            print(f"[DEBUG] Agent invoke completed successfully")
            print(f"[DEBUG] Result type: {type(result)}")
            print(f"[DEBUG] Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"[DEBUG] Agent invoke failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print(f"\n✅ Conversation completed successfully!")
        print(f"📊 Total messages exchanged: {len(result.get('messages', []))}")
        print(f"📝 Final summary: {result.get('conversation_summary', 'N/A')[:100]}...")
        print(f"🗃️ Recording saved to: dealership_customer_support.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running dealership agent: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TimeMachine Dealership Customer Support Agent")
    print("Real GPT calls with Human-in-the-Loop conversation")
    print("=" * 60)
    
    success = run_dealership_demo()
    
    if success:
        print("\n🌐 View recordings in web UI:")
        print("   cd web && python backend.py")
        print("   npm run dev")
        print("   Open http://localhost:3000")
    
    print(f"\n{'[PASS] DEMO COMPLETED' if success else '[FAIL] DEMO FAILED'}")
