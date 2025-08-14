# TimeMachine - Time-Travel Debugger for LangGraph Agents

TimeMachine is a comprehensive debugging and recording system for LangGraph agents that captures every node execution with full state tracking. Think of it as a "flight recorder" for your AI agents.

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

### Basic Usage

#### Method 1: Decorator (Recommended)
```python
import timemachine
from langgraph.graph import StateGraph

@timemachine.record("my_recordings.db")
def create_my_agent():
    graph = StateGraph(MyState)
    graph.add_node("step1", my_function)
    graph.add_node("step2", another_function)
    # ... add edges ...
    return graph  # Return StateGraph, not compiled

# Use your agent normally
agent = create_my_agent()
result = agent.invoke({"messages": [], "data": "test"})
```

#### Method 2: Direct Wrapping
```python
import timemachine

# Wrap your existing graph
graph = StateGraph(MyState)
# ... build your graph ...

tm_graph = timemachine.TimeMachineGraph(graph, "recordings.db")
agent = tm_graph.compile()
result = agent.invoke(initial_state)
```

#### Method 3: Context Manager
```python
import timemachine

with timemachine.recording("context_recordings.db"):
    agent = create_my_agent()
    result = agent.invoke(initial_state)
```

## 📁 Project Structure

### Current Structure (Phase 1)
```
time-machine/
├── timemachine/              # Core TimeMachine library
│   ├── __init__.py          # Public API
│   ├── recorder.py          # SQLite recording engine
│   ├── wrapper.py           # Node and graph wrappers
│   ├── serializer.py        # State serialization
│   └── decorator.py         # Integration decorators
├── test/                    # Test suite
│   ├── README.md           # Test documentation
│   ├── run_all_tests.py    # Test runner
│   ├── test_basic_functionality.py
│   ├── test_serialization.py
│   ├── test_decorator_integration.py
│   ├── test_context_manager.py
│   └── test_demo_sample_agent.py
├── sample_agent.py         # Example LangGraph agent
├── architecture.md         # Technical architecture
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore patterns
└── README.txt             # This file
```

### Future Structure (Full Product)
```
time-machine/
├── timemachine/
│   ├── __init__.py           # Main API exports
│   ├── core/                 # Core recording functionality
│   │   ├── __init__.py
│   │   ├── recorder.py       # Database operations
│   │   ├── wrapper.py        # Node instrumentation
│   │   ├── serializer.py     # State serialization
│   │   └── decorator.py      # Integration helpers
│   ├── analysis/             # Phase 2: Data analysis
│   │   ├── __init__.py
│   │   ├── llm_tracker.py    # LLM call detection
│   │   ├── cost_analyzer.py  # Token/cost tracking
│   │   └── patterns.py       # Pattern detection
│   ├── replay/               # Phase 2: Counterfactual engine
│   │   ├── __init__.py
│   │   ├── engine.py         # Replay orchestration
│   │   ├── counterfactual.py # "What if" scenarios
│   │   └── cache.py          # Response caching
│   ├── web/                  # Phase 3: Web UI backend
│   │   ├── __init__.py
│   │   ├── api.py            # FastAPI routes
│   │   ├── models.py         # Pydantic models
│   │   └── auth.py           # Authentication
│   └── utils/                # Shared utilities
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       ├── exceptions.py     # Custom exceptions
│       └── validators.py     # Input validation
├── web/                      # Phase 3: Web UI frontend
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── public/
├── cli/                      # Command-line interface
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── commands/
│   │   ├── record.py        # Recording commands
│   │   ├── replay.py        # Replay commands
│   │   └── analyze.py       # Analysis commands
├── examples/                 # Usage examples
│   ├── basic_usage.py
│   ├── advanced_agent.py
│   └── integrations/
│       ├── langchain_example.py
│       └── llamaindex_example.py
├── test/                     # Tests
├── docs/                     # Documentation
│   ├── source/
│   ├── build/
│   └── api/
└── scripts/                  # Development scripts
    ├── setup.py
    ├── build.py
    └── deploy.py
```

## 🔍 What Gets Recorded

TimeMachine captures comprehensive execution data:

### Node Execution Records
- **Execution ID**: Unique identifier for each node execution
- **Graph Run ID**: Groups all nodes from a single graph execution
- **Node Name**: Which node was executed
- **Timestamp**: When execution started
- **Input State**: Complete state passed to the node (JSON serialized)
- **Output State**: Complete state returned by the node (JSON serialized)
- **Duration**: Execution time in milliseconds
- **Status**: success/error/interrupted
- **Error Messages**: Full error details if execution failed

### State Serialization
- **LangChain Messages**: Proper handling of HumanMessage, AIMessage, SystemMessage
- **Complex Objects**: Nested dictionaries and lists
- **Type Preservation**: Message types and metadata maintained
- **JSON Storage**: Human-readable database format

## 🧪 Testing

### Run All Tests
```bash
python test/run_all_tests.py
```

### Run Individual Tests
```bash
python test/test_basic_functionality.py     # Core functionality
python test/test_serialization.py          # State serialization
python test/test_decorator_integration.py  # Decorator approach
python test/test_context_manager.py        # Context manager
python test/test_demo_sample_agent.py      # Complete demo
```

### Test Coverage
- ✅ Node execution recording
- ✅ State serialization/deserialization
- ✅ Error handling and recovery
- ✅ All integration methods
- ✅ LangChain message handling
- ✅ Multi-node graph execution
- ✅ Database persistence

## 📊 Viewing Recordings

### Programmatic Access
```python
import timemachine

# Access recordings
recorder = timemachine.TimeMachineRecorder("my_recordings.db")

# List all graph runs
runs = recorder.list_graph_runs()
print(f"Found {len(runs)} graph executions")

# Get detailed execution data
for run in runs:
    graph_run_id = run['graph_run_id']
    executions = recorder.get_graph_executions(graph_run_id)
    
    print(f"Graph run {graph_run_id[:8]}...")
    for execution in executions:
        print(f"  - {execution['node_name']}: {execution['status']} ({execution['duration_ms']}ms)")
```

### Database Schema
SQLite database with three main tables:
- **`node_executions`**: Main execution records
- **`llm_calls`**: LLM interaction tracking (ready for Phase 2)
- **`graph_snapshots`**: Graph topology storage

## 🏗️ Architecture

TimeMachine follows a modular architecture:

### Core Components
1. **TimeMachineNodeWrapper**: Wraps individual node functions for recording
2. **TimeMachineGraph**: Wraps entire StateGraph for automatic instrumentation
3. **TimeMachineRecorder**: Manages SQLite database operations
4. **StateSerializer**: Handles complex state object serialization

### Integration Methods
1. **Decorator**: `@timemachine.record()` - Zero-code-change approach
2. **Direct Wrapping**: `TimeMachineGraph(graph)` - Explicit control
3. **Context Manager**: `with timemachine.recording():` - Scope-based recording

### Key Features
- **Zero-Code-Change Integration**: Use decorators for existing agents
- **Automatic State Handling**: Complex LangGraph states serialized properly
- **Error Recovery**: Failed executions properly recorded with error details
- **Performance Tracking**: Millisecond-precision timing data
- **Cross-Platform**: Works on Windows, Linux, and macOS

## 🔧 Implementation Status

### ✅ Phase 1: Core Recording (COMPLETE)
- [x] Node execution recording
- [x] State serialization
- [x] SQLite storage
- [x] Multiple integration methods
- [x] Error handling
- [x] Comprehensive testing

### 🚧 Phase 2: LLM Integration (PLANNED)
- [ ] LLM call detection within nodes
- [ ] Model parameter extraction
- [ ] Token usage tracking
- [ ] Cost estimation
- [ ] Response caching

### **Phase 2.5: Simplification (Next)**

Cut out unnecessary features like caching responses and tracking AI, and finding problems and waste. Focus only on "what if" games.

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
OPENAI_API_KEY=your_key_here
```

### Running Tests
All tests are designed to work without external API calls (using mocks).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite: `python test/run_all_tests.py`
5. Submit a pull request

## 📄 License

[License information would go here]

## 🙋 Support

For questions, issues, or feature requests:
1. Check the `test/` directory for examples
2. Review `architecture.md` for technical details
3. Open an issue on the repository

---

**TimeMachine** - Making LangGraph agent debugging as easy as time travel! 🕰️