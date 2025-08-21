# TimeMachine - LangGraph Agent Debugger

TimeMachine records LangGraph agent executions and enables counterfactual testing through a modern web interface.

## Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
git clone https://github.com/lucasliao0403/time-machine
cd time-machine

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key (optional, for demos)
# Create .env file with: OPENAI_API_KEY=your_key_here
```

### 2. Record Agent Executions

Add TimeMachine recording to your LangGraph agent:

```python
import timemachine
from langgraph.graph import StateGraph

@timemachine.record("recordings.db")
def create_my_agent():
    graph = StateGraph(MyState)
    # ... configure your graph ...
    return graph

# Run your agent normally - executions are recorded automatically
agent = create_my_agent()
result = agent.invoke({"messages": [HumanMessage("Hello")]})
```

### 3. Start Web Interface

```bash
# Terminal 1: Start backend API
python web/backend.py

# Terminal 2: Start frontend (in web/ directory)
cd web
npm install
npm run dev

# Open http://localhost:3000 in browser
```

## Demo Agents

### Run Sample Agent

```bash
# Simple demo agent
python run_dealership_demo.py
```

### Run Dealership Agent (requires OpenAI API key)

```bash
# Interactive customer support agent with 7 GPT calls
python dealership_customer_support_agent.py
```

## Testing

```bash
# Run all tests
python test/run_all_tests.py

# Test specific functionality
python test/test_basic_functionality.py
python test/test_phase2_replay.py
```

## Core Features

- **Automatic Recording**: Captures all node executions with full state
- **Web Interface**: Modern UI for browsing executions and running tests
- **Counterfactual Testing**: Test different models, temperatures, and prompts
- **Flow Visualization**: Interactive 2D graphs showing execution patterns
- **Zero Code Changes**: Just add a decorator to your agent function

## Requirements

- Python 3.11+
- Node.js 18+ (for web interface)
- OpenAI API key (for demo agents only)

## Integration Methods

```python
# Method 1: Decorator (recommended)
@timemachine.record("recordings.db")
def create_agent():
    return StateGraph(MyState).compile()

# Method 2: Context manager
with timemachine.recording("recordings.db"):
    result = agent.invoke(input_data)

# Method 3: Direct wrapping
tm_graph = timemachine.TimeMachineGraph(graph, "recordings.db")
agent = tm_graph.compile()
```