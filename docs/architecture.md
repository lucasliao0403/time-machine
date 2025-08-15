# TimeMachine Architecture - Node-Level Recording for LangGraph

## Overview
TimeMachine is a time-travel debugger for LangGraph agents that records every node execution with full context, allowing replay and counterfactual testing.

## Core Concept
```
Original Node: input_state -> node_function() -> output_state
Wrapped Node:  input_state -> [RECORD] -> node_function() -> [RECORD] -> output_state
```

## 1. Recording Architecture

### Node Wrapper Implementation
```python
class TimeMachineNodeWrapper:
    def __init__(self, original_node_func, node_name, recorder):
        self.original_func = original_node_func
        self.node_name = node_name
        self.recorder = recorder
    
    def __call__(self, state, config=None):
        # Record input
        execution_id = self.recorder.start_execution(
            node_name=self.node_name,
            input_state=state,
            timestamp=time.time()
        )
        
        try:
            # Execute original node
            start_time = time.time()
            result = self.original_func(state, config)
            duration = time.time() - start_time
            
            # Record success
            self.recorder.complete_execution(
                execution_id=execution_id,
                output_state=result,
                duration_ms=duration * 1000,
                status="success"
            )
            
            return result
            
        except Exception as e:
            # Record failure
            self.recorder.complete_execution(
                execution_id=execution_id,
                error=str(e),
                status="error"
            )
            raise
```

### Automatic Graph Instrumentation
```python
class TimeMachineGraph:
    def __init__(self, original_graph):
        self.original_graph = original_graph
        self.recorder = TimeMachineRecorder()
        
    def instrument_graph(self):
        """Wrap all nodes in the compiled graph"""
        for node_name, node in self.original_graph.nodes.items():
            wrapped_node = TimeMachineNodeWrapper(
                original_node_func=node.runnable,
                node_name=node_name,
                recorder=self.recorder
            )
            self.original_graph.nodes[node_name].runnable = wrapped_node
```

## 2. Database Schema

### SQLite Tables
```sql
-- Main executions table
CREATE TABLE node_executions (
    id TEXT PRIMARY KEY,
    graph_run_id TEXT,      -- Groups nodes from same graph execution
    node_name TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    input_state TEXT,       -- JSON serialized state
    output_state TEXT,      -- JSON serialized state  
    duration_ms INTEGER,
    status TEXT,            -- 'success', 'error', 'interrupted'
    error_message TEXT,
    
    -- Metadata for replay
    graph_structure TEXT,   -- JSON of graph topology
    node_position INTEGER,  -- Order in execution sequence
    
    -- Cost tracking
    total_tokens INTEGER,
    estimated_cost REAL
);

-- LLM calls within nodes (for detailed debugging)
CREATE TABLE llm_calls (
    id TEXT PRIMARY KEY,
    execution_id TEXT REFERENCES node_executions(id),
    model_name TEXT,
    temperature REAL,
    prompt TEXT,
    response TEXT,
    tokens_used INTEGER,
    timestamp INTEGER,
    duration_ms INTEGER
);

-- Graph topology snapshots
CREATE TABLE graph_snapshots (
    graph_run_id TEXT PRIMARY KEY,
    nodes TEXT,             -- JSON list of node names
    edges TEXT,             -- JSON list of edges
    start_node TEXT,
    end_nodes TEXT          -- JSON list of possible end nodes
);
```

## 3. User Integration

### Simple Decorator Pattern
```python
# Easy integration - user just decorates their graph compilation
@timemachine.record()
def create_my_agent():
    graph = StateGraph(MyState)
    graph.add_node("step1", first_step)
    graph.add_node("step2", second_step)
    graph.add_edge(START, "step1")
    graph.add_edge("step1", "step2")
    graph.add_edge("step2", END)
    return graph.compile()

# Or context manager approach
with timemachine.recording():
    agent = create_my_agent()
    result = agent.invoke({"messages": [], "topic": ""})
```

### Zero Code Changes Required
```python
# Original code (unchanged):
agent = create_my_agent()
result = agent.invoke({"messages": [], "topic": ""})

# With TimeMachine (just add one line):
agent = timemachine.record(create_my_agent())
result = agent.invoke({"messages": [], "topic": ""})
```

## 4. State Serialization

### Handling Complex LangGraph State
```python
class StateSerializer:
    def serialize_state(self, state):
        """Convert LangGraph state to JSON for storage"""
        if isinstance(state, dict):
            return self._serialize_dict(state)
        elif hasattr(state, '__dict__'):
            return self._serialize_object(state)
        else:
            return json.dumps(state, default=str)
    
    def _serialize_dict(self, state_dict):
        """Handle complex state with messages, etc."""
        serialized = {}
        for key, value in state_dict.items():
            if key == "messages":
                # Special handling for LangChain messages
                serialized[key] = [self._serialize_message(msg) for msg in value]
            else:
                serialized[key] = value
        return json.dumps(serialized)
    
    def _serialize_message(self, message):
        """Serialize LangChain message objects"""
        return {
            "type": message.__class__.__name__,
            "content": message.content,
            "additional_kwargs": getattr(message, 'additional_kwargs', {}),
        }
```

## 5. Replay Engine

### Node-Level Replay
```python
class NodeReplayEngine:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)
        
    def replay_node_execution(self, execution_id):
        """Replay a single node execution"""
        execution = self.load_execution(execution_id)
        
        # Reconstruct the node function
        node_func = self.reconstruct_node_function(execution)
        
        # Deserialize input state
        input_state = self.deserialize_state(execution['input_state'])
        
        # Execute with same input
        result = node_func(input_state)
        
        return {
            "original_output": self.deserialize_state(execution['output_state']),
            "replay_output": result,
            "match": self.compare_states(execution['output_state'], result)
        }
    
    def replay_graph_run(self, graph_run_id):
        """Replay entire graph execution"""
        executions = self.load_graph_executions(graph_run_id)
        
        # Reconstruct graph
        graph = self.reconstruct_graph(graph_run_id)
        
        # Get initial state from first execution
        initial_state = self.get_initial_state(executions[0])
        
        # Run entire graph
        result = graph.invoke(initial_state)
        
        return result
```

## 6. Counterfactual Testing

### Testing Alternative Scenarios
```python
class CounterfactualEngine:
    def test_node_with_different_params(self, execution_id, **modifications):
        """Test what would happen with modified node behavior"""
        execution = self.load_execution(execution_id)
        
        # Modify the node function based on parameters
        if 'model' in modifications:
            # Replace LLM calls in the node with different model
            modified_node = self.modify_node_llm(execution, modifications['model'])
        
        if 'temperature' in modifications:
            # Adjust temperature in LLM calls
            modified_node = self.modify_node_temperature(execution, modifications['temperature'])
        
        # Execute with same input state
        input_state = self.deserialize_state(execution['input_state'])
        result = modified_node(input_state)
        
        return result
```

## 7. LLM Call Detection

### Capturing LLM Calls Within Nodes
```python
class LLMCallRecorder:
    def __init__(self, execution_id):
        self.execution_id = execution_id
        self.calls = []
    
    def __enter__(self):
        # Patch ChatOpenAI, ChatAnthropic, etc.
        self.original_invoke = ChatOpenAI.invoke
        ChatOpenAI.invoke = self.wrapped_invoke
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original methods
        ChatOpenAI.invoke = self.original_invoke
        # Save recorded calls to database
        self.save_llm_calls()
    
    def wrapped_invoke(self, instance, messages, **kwargs):
        start_time = time.time()
        result = self.original_invoke(instance, messages, **kwargs)
        duration = time.time() - start_time
        
        self.calls.append({
            "model": instance.model_name,
            "temperature": getattr(instance, 'temperature', 0.7),
            "prompt": self.serialize_messages(messages),
            "response": result.content,
            "duration_ms": duration * 1000,
            "timestamp": start_time
        })
        
        return result
```

## 8. Sample Agent Recording Example

### What Gets Recorded
For the sample agent with 2 nodes:

```python
# Execution 1: first_step node
{
    "node_name": "step1",
    "input_state": {"messages": [], "topic": ""},
    "output_state": {"messages": [HumanMessage("python")], "topic": "python"},
    "llm_calls": []  # No LLM calls in this node
}

# Execution 2: second_step node  
{
    "node_name": "step2", 
    "input_state": {"messages": [HumanMessage("python")], "topic": "python"},
    "output_state": {"messages": [HumanMessage("python"), AIMessage("Python fact...")]},
    "llm_calls": [
        {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "prompt": "Tell me one fascinating fact about python",
            "response": "Python can sleep for months during brumation...",
            "tokens": 45
        }
    ]
}
```

## 9. Web UI Integration

### FastAPI Backend
- REST endpoints for listing recordings
- Replay functionality
- Counterfactual testing interface
- Real-time execution monitoring

### Simple Frontend
- List view of graph runs
- Node execution timeline
- State diff visualization
- Replay and branch testing buttons

## 10. Key Benefits

### For Developers
- **Minimal intrusion**: Just add a decorator or context manager
- **Complete context**: Captures full state transitions, not just LLM calls
- **Flexible replay**: Can replay individual nodes or full graphs
- **Natural boundaries**: Nodes are logical units developers understand

### For Debugging
- **Precise failure isolation**: Know exactly which node and why it failed
- **State flow visualization**: See how data transforms between nodes
- **Counterfactual testing**: Test different models/parameters on same inputs
- **Historical analysis**: Compare behavior across different runs

### For Production
- **Performance monitoring**: Track node execution times
- **Cost tracking**: Monitor token usage and API costs
- **Error patterns**: Identify common failure modes
- **A/B testing**: Compare different agent configurations

## Implementation Priority

### Phase 1: Core Recording
1. Node wrapper implementation
2. SQLite storage layer
3. Basic state serialization
4. Simple replay functionality

### Phase 2: LLM Integration
1. LLM call detection within nodes
2. Model parameter extraction
3. Token/cost tracking
4. Counterfactual engine

### Phase 3: User Interface (COMPLETE)
1. ✅ FastAPI backend with REST API endpoints
2. ✅ Next.js web application with TypeScript
3. ✅ Modern dark theme with glass morphism design system
4. ✅ Interactive graph runs browser with elegant card-based layout
5. ✅ Real-time statistics dashboard with animated counters
6. ✅ Framer Motion animations and smooth micro-interactions
7. ✅ Responsive design supporting desktop and mobile devices
8. ✅ Comprehensive style guide and design system documentation

### Design System Overview

The TimeMachine UI implements a sophisticated design system with:

**Dark Theme Foundation**: Professional dark interface using slate color palette optimized for long development sessions and reduced eye strain.

**Glass Morphism Effects**: Translucent elements with backdrop blur create visual depth and hierarchy throughout the interface.

**Animation Strategy**: Framer Motion powers smooth transitions, hover effects, and page animations that enhance usability without being distracting.

**Component Architecture**: Reusable glass card components, animated buttons, status indicators, and navigation elements following consistent patterns.

**Typography System**: Inter font family for UI text and JetBrains Mono for code, with carefully tuned hierarchy and contrast ratios for accessibility.

**Color Philosophy**: 
- Primary blues for interactive elements and highlights
- Secondary purples for accent colors and gradients  
- Semantic colors (green/red/yellow) for status indicators
- Glass transparency levels for different UI layers

This architecture provides the foundation for a production-ready TimeMachine system that integrates seamlessly with existing LangGraph agents while providing powerful debugging and analysis capabilities through a modern, professional interface.
