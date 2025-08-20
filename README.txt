# TimeMachine - Branch Testing for LangGraph Agents

TimeMachine is a time-travel debugger for LangGraph agents that records executions and enables powerful counterfactual scenario analysis. Think of it as a flight recorder + experimental testing lab for your AI agents.

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd time-machine

# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies (already included in venv)
pip install -r requirements.txt
```

### Step 1: Record Your Agent

```python
import timemachine
from langgraph.graph import StateGraph

@timemachine.record("my_recordings.db")
def create_my_agent():
    graph = StateGraph(MyState)
    # ... configure your graph ...
    return graph

# Your recordings happen automatically
agent = create_my_agent()
result = agent.invoke({"messages": [HumanMessage("Hello")]})
```

### Step 2: Run Branch Experiments

```python
from timemachine.replay import CounterfactualEngine

engine = CounterfactualEngine()

# Test different models across execution branches
model_comparison = engine.analyze_model_alternatives("execution_id", 
    ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"])

# Experiment with different temperatures
temp_analysis = engine.analyze_temperature_sensitivity("execution_id", 
    [0.1, 0.5, 0.9])

print(f"Tested {len(model_comparison.scenarios)} model scenarios")
```

## ✨ Core Features

### 🎯 Phase 1: Core Recording (COMPLETE)
- **Node Execution Recording** - Captures input/output state for every LangGraph node
- **State Serialization** - Handles complex LangChain objects (BaseMessage, etc.)
- **SQLite Storage** - Persistent, queryable execution history
- **Multiple Integration Methods** - Decorator, context manager, or direct wrapping
- **Error Handling** - Graceful recording even when nodes fail

### 🎮 Phase 2: Branch Testing (COMPLETE)  
- **Counterfactual Analysis** - Pure scenario testing across execution branches
- **Model Alternatives** - Compare different AI models (GPT-4 vs GPT-3.5 vs Claude)
- **Temperature Sensitivity** - Test how creativity settings affect outputs
- **Prompt Variations** - Experiment with different prompt formulations
- **Parameter Sweeps** - Try ranges of parameter values
- **Replay Engine** - Re-execute scenarios with modifications

### **Phase 2.5: In depth test**

Test with a real agent with real LLM calls to validate counterfactual analysis works in practice:
- Use actual OpenAI/Anthropic API calls (not mocks)
- Test temperature variations produce meaningful output differences
- Verify model swapping works across different providers
- Measure actual execution performance and reliability
- Validate state serialization with complex real-world data
- Test counterfactuals on multi-step agents with dependencies

### **Phase 2.8: Missing Critical Features**

Before building UI, we need:
- **Execution Browsing**: List and filter recorded graph runs by date, status, duration
- **Data Export**: Export execution data to JSON/CSV for external analysis
- **Batch Analysis**: Run counterfactuals on multiple executions at once
- **Result Comparison**: Side-by-side comparison of original vs counterfactual outputs
- **Search & Query**: Find executions by state content, node names, or metadata
- **Cleanup Tools**: Archive old recordings, manage database size
- **Performance Metrics**: Track replay success rates, execution times, memory usage

## 🎮 Branch Testing Examples

### Model Comparison
```python
from timemachine.replay import CounterfactualEngine

engine = CounterfactualEngine()

# Compare different AI models
comparison = engine.analyze_model_alternatives("execution_123", 
    ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"])

print(f"Tested {len(comparison.scenarios)} models")
print(f"Tested {len(comparison.scenarios)} scenarios")
for insight in comparison.insights:
    print(f"- {insight}")
```

### Temperature Sensitivity
```python
# Test how creativity affects outputs
temp_analysis = engine.analyze_temperature_sensitivity("execution_123", 
    [0.1, 0.5, 0.9])

print("Temperature effects:")
for scenario in temp_analysis.scenarios:
    temp = scenario.scenario.modifications['temperature']
    success = scenario.replay_result.success
          print(f"  Temperature {temp}: {'Success' if success else 'Failed'}")
```

### Prompt Experiments
```python
# Test different prompt formulations
prompts = [
    {"content": "Be creative and detailed", "description": "Creative"},
    {"content": "Be concise and factual", "description": "Factual"},
    {"content": "Use examples and analogies", "description": "Educational"}
]

prompt_analysis = engine.analyze_prompt_variations("execution_123", prompts)
print(f"Tested {len(prompt_analysis.scenarios)} prompt variations")
```

### Web UI Interface
```bash
# Start the web interface
cd web
npm install
npm run dev

# In another terminal, start the backend
python backend.py

# Open http://localhost:3000 in your browser
```

### Parameter Sweeps
```python
# Test ranges of values systematically
max_tokens_sweep = engine.analyze_parameter_sweep("execution_123",
    "max_tokens", [50, 100, 200, 500])

print("Token limit effects:")
for scenario in max_tokens_sweep.scenarios:
    tokens = scenario.scenario.modifications['max_tokens']
    output_len = len(scenario.replay_result.replayed_output.get('content', ''))
    print(f"  Max {tokens} tokens → {output_len} chars output")
```

## 🎯 Why TimeMachine?

### For Developers
- **Debug Complex Flows** - See exactly what happened in each node
- **Test Branch Scenarios** - Safely experiment with different parameters
- **Compare Approaches** - Evaluate model alternatives without rebuilding
- **Understand Sensitivity** - See how small changes affect outputs

### For Teams  
- **Collaborative Experimentation** - Share counterfactual analyses
- **Safe Parameter Tuning** - Test configurations without risking production
- **Model Selection** - Compare AI models systematically
- **Prompt Engineering** - Optimize prompts through systematic testing

## 🏗️ Architecture

TimeMachine operates in two simplified phases:

1. **Recording Phase** - Captures all node executions with full state
2. **Branch Testing Phase** - Enables counterfactual scenario analysis

### Current Structure (Phase 3)
```
time-machine/
├── timemachine/
│   ├── __init__.py           # Main API exports  
│   ├── core/                 # Phase 1: Core recording
│   │   ├── recorder.py       # Database operations
│   │   ├── wrapper.py        # Node instrumentation  
│   │   ├── serializer.py     # State serialization
│   │   └── decorator.py      # Integration helpers
│   └── replay/               # Phase 2: Branch testing
│       ├── engine.py         # Replay orchestration
│       └── counterfactual.py # Counterfactual scenarios
├── web/                      # Phase 3: Web UI
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React components
│   │   ├── lib/              # API client and utilities
│   │   └── types/            # TypeScript definitions
│   ├── backend.py            # FastAPI backend
│   └── package.json          # Node.js dependencies
├── test/                     # Comprehensive test suite
├── sample_agent.py           # Demo LangGraph agent
└── requirements.txt          # Python dependencies
```

## 🔍 What Gets Recorded

TimeMachine captures comprehensive execution data:

### Node Execution Details
- **Input State** - Complete state before node execution
- **Output State** - Complete state after node execution  
- **Execution Metadata** - Timestamps, duration, success/failure
- **Error Information** - Full error details when nodes fail
- **Graph Structure** - Node relationships and execution order

### State Information
- **LangChain Messages** - Full message history with metadata
- **Custom State Fields** - All TypedDict fields in your state
- **Complex Objects** - Proper serialization of nested data structures

## 🛠️ Integration Methods

### Method 1: Decorator (Recommended)
```python
@timemachine.record("recordings.db")
def create_agent():
    graph = StateGraph(ChatState)
    # ... build graph ...
    return graph  # Return StateGraph, not compiled

agent = create_agent()  # Auto-compiles with recording
```

### Method 2: Context Manager
```python
with timemachine.recording("recordings.db"):
    agent = create_agent()
    result = agent.invoke({"messages": [HumanMessage("Hello")]})
```

### Method 3: Direct Wrapping
```python
graph = StateGraph(ChatState)
# ... build graph ...

tm_graph = timemachine.TimeMachineGraph(graph, "recordings.db")
agent = tm_graph.compile()
```

## 📈 Development Status

### ✅ Phase 1: Core Recording (COMPLETE)
- [x] Node execution recording
- [x] State serialization
- [x] SQLite storage
- [x] Multiple integration methods
- [x] Error handling
- [x] Comprehensive testing

### ✅ Phase 2: Simplified Branch Testing (COMPLETE)
- [x] Counterfactual analysis engine
- [x] Model alternatives comparison
- [x] Temperature sensitivity testing
- [x] Prompt variation experiments
- [x] Parameter sweep analysis
- [x] Replay engine for modifications

### ✅ Phase 3: Web UI (COMPLETE)
- [x] Next.js web application with TypeScript
- [x] Modern dark theme with glass morphism design
- [x] Graph runs browser and execution timeline
- [x] Interactive counterfactual analysis interface
- [x] Real-time results visualization with charts
- [x] FastAPI backend integration
- [x] Responsive design with Tailwind CSS
- [x] Framer Motion animations and micro-interactions
- [x] Professional enterprise-grade UI/UX

## 📝 Sample Agents

### Basic Sample Agent (`quick_demo.py`)
A simple two-step LangGraph agent that:
1. Asks for a topic (or uses mock input in tests)
2. Generates an AI response about that topic

Perfect for testing TimeMachine integration:

```python
# Run with TimeMachine recording
python quick_demo.py
```

### Comprehensive Dealership Customer Support Agent (`dealership_customer_support_agent.py`)
A realistic customer support agent for a car dealership featuring:
- **7 conversation nodes** with real GPT calls
- **Human-in-the-loop intervention** for complex decisions
- **Mock dealership databases** (customers, inventory, service, financing)
- **Terminal-based conversation flow** with realistic customer interactions
- **Multiple inquiry types** (service, sales, complaints, financing)
- **Real-world scenarios** including escalation and approval workflows

Features 7+ real GPT API calls:
1. Intent analysis and customer greeting
2. Customer identification and personalization
3. Detailed inquiry processing
4. Information processing and recommendations
5. Solution development with pricing/scheduling
6. Human agent consultation and decisions
7. Conversation finalization and follow-up

```python
# Run interactive dealership demo (requires OPENAI_API_KEY)
python dealership_customer_support_agent.py

# Validate agent structure
python test_dealership_agent.py
```

## 🌐 Web Interface

TimeMachine includes a modern web interface built with Next.js and TypeScript:

### Features
- **Modern Dark Theme** - Professional dark interface with glass morphism effects and smooth animations
- **Graph Runs Browser** - View all recorded agent executions with elegant card-based design
- **Unified Flow Interface** - Single interface combining flow visualization, execution details, and testing
- **Interactive Node Selection** - Click any node to view all executions and run tests immediately
- **Seamless Testing Workflow** - No tab switching: select node → view executions → test → see results
- **Multi-Execution Support** - Handle circular flows by showing all executions for each node
- **Real-time Visualization** - 2D flow graphs with D3.js and interactive counterfactual analysis
- **Responsive Design** - Works seamlessly on desktop and mobile devices with fluid transitions
- **Framer Motion Animations** - Smooth micro-interactions and page transitions for enhanced UX

### Quick Start
```bash
# Install and start the web UI
cd web
npm install
npm run dev

# Start the backend API (in another terminal)
python backend.py

# Open http://localhost:3000
```

### Usage Flow
1. **Record Executions** → Use Python decorators to capture agent runs
2. **Browse Runs** → View all recorded graph runs in the web interface
3. **Explore Flow** → Select a run to view the unified flow visualization  
4. **Test Nodes** → Click any node to see executions and run counterfactual tests
5. **Analyze Results** → Compare original vs modified outputs in the same interface

## 🛠️ Development

### Requirements
- Python 3.11+
- Node.js 18+ and npm (for web UI)
- LangGraph 0.2.68+
- LangChain Core 0.3.74+
- SQLAlchemy 2.0.43+
- FastAPI 0.104+ (for web backend)
- OpenAI API key (for sample agent)

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### Running Tests
```bash
# Run Python tests
python test/run_all_tests.py

# Run specific tests
python test/test_basic_functionality.py
python test/test_phase2_replay.py

# Test with real agent (requires OpenAI API key)
python test/test_real_agent_e2e.py

# Start web interface for manual testing
cd web
npm run dev
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests to ensure everything works
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangGraph team for the excellent agent framework
- LangChain team for the foundational components
- The open-source community for inspiration and feedback