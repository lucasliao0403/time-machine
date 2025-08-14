# TimeMachine - "What If" Games for LangGraph Agents

TimeMachine is a time-travel debugger for LangGraph agents that records executions and enables powerful "what if" scenario analysis. Think of it as a flight recorder + counterfactual experiment lab for your AI agents.

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

### Step 2: Run "What If" Experiments

```python
from timemachine.replay import CounterfactualEngine

engine = CounterfactualEngine()

# What if we used different models?
model_comparison = engine.analyze_model_alternatives("execution_id", 
    ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"])

# What if we used different temperatures?
temp_analysis = engine.analyze_temperature_sensitivity("execution_id", 
    [0.1, 0.5, 0.9])

print(f"Best scenario: {model_comparison.best_scenario.scenario.name}")
```

## ✨ Core Features

### 🎯 Phase 1: Core Recording (COMPLETE)
- **Node Execution Recording** - Captures input/output state for every LangGraph node
- **State Serialization** - Handles complex LangChain objects (BaseMessage, etc.)
- **SQLite Storage** - Persistent, queryable execution history
- **Multiple Integration Methods** - Decorator, context manager, or direct wrapping
- **Error Handling** - Graceful recording even when nodes fail

### 🎮 Phase 2: "What If" Games (COMPLETE)  
- **Counterfactual Analysis** - Pure "what if" scenario testing
- **Model Alternatives** - Compare different AI models (GPT-4 vs GPT-3.5 vs Claude)
- **Temperature Sensitivity** - Test how creativity settings affect outputs
- **Prompt Variations** - Experiment with different prompt formulations
- **Parameter Sweeps** - Try ranges of parameter values
- **Replay Engine** - Re-execute scenarios with modifications

### **Phase 2.5: In depth test**

Test with a real agent with real LLM calls. 
Implement counterfactuals with REAL LLM calls if needed.

## 🎮 "What If" Examples

### Model Comparison
```python
from timemachine.replay import CounterfactualEngine

engine = CounterfactualEngine()

# Compare different AI models
comparison = engine.analyze_model_alternatives("execution_123", 
    ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"])

print(f"Tested {len(comparison.scenarios)} models")
print(f"Best result: {comparison.best_scenario.scenario.name}")
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
    change = scenario.replay_result.output_difference_score
    print(f"  Temperature {temp}: {change:.1%} output change")
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
print(f"Best prompt approach: {prompt_analysis.best_scenario.scenario.name}")
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
- **Test "What If" Scenarios** - Safely experiment with different parameters
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
2. **"What If" Phase** - Enables counterfactual scenario analysis

### Current Structure (Phase 2)
```
time-machine/
├── timemachine/
│   ├── __init__.py           # Main API exports  
│   ├── core/                 # Phase 1: Core recording
│   │   ├── recorder.py       # Database operations
│   │   ├── wrapper.py        # Node instrumentation  
│   │   ├── serializer.py     # State serialization
│   │   └── decorator.py      # Integration helpers
│   └── replay/               # Phase 3: "What if" games
│       ├── engine.py         # Replay orchestration
│       └── counterfactual.py # Counterfactual scenarios
├── test/                     # Simplified test suite
├── sample_agent.py           # Demo LangGraph agent
└── requirements.txt          # Dependencies
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

### ✅ Phase 2: Simplified "What If" Games (COMPLETE)
- [x] Counterfactual analysis engine
- [x] Model alternatives comparison
- [x] Temperature sensitivity testing
- [x] Prompt variation experiments
- [x] Parameter sweep analysis
- [x] Replay engine for modifications

### 🚧 Phase 3: Web UI (PLANNED)
- [ ] Web-based execution viewer
- [ ] State inspection interface
- [ ] Timeline visualization
- [ ] Debugging tools
- [ ] Export capabilities

## 📝 Sample Agent

The repository includes `sample_agent.py` - a simple two-step LangGraph agent that:
1. Asks for a topic (or uses mock input in tests)
2. Generates an AI response about that topic

Perfect for testing TimeMachine integration:

```python
# Run with TimeMachine recording
python test/test_demo_sample_agent.py
```

## 🛠️ Development

### Requirements
- Python 3.11+
- LangGraph 0.2.68+
- LangChain Core 0.3.74+
- SQLAlchemy 2.0.43+
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
# Run all tests
python test/run_all_tests.py

# Run specific tests
python test/test_basic_functionality.py
python test/test_phase2_replay.py
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