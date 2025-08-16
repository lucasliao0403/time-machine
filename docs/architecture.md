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

- REST endpoints for listing recordings and executions
- Replay functionality with ReplayEngine integration
- Counterfactual testing interface (temperature, model, custom)
- Flow visualization data with D3.js compatibility
- Fixed API response format matching TypeScript interfaces

### Modern Frontend Architecture

- **Unified Flow Interface**: Single cohesive interface combining flow visualization, execution details, and testing
- **Interactive Node Selection**: Click any node to view all executions and run tests immediately
- **Multi-Execution Support**: Handles circular flows by displaying all executions per node
- **Real-time Testing**: Seamless workflow from node selection to counterfactual analysis
- **Modal Content Viewing**: JsonModal component for viewing full JSON content with copy functionality
- **Professional UI**: Glass morphism design system with Framer Motion animations

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

### Phase 3.5: Unified Flow Interface (COMPLETE)

1. ✅ **UnifiedFlowInterface Component**: Single cohesive interface combining flow visualization, node details, and testing
2. ✅ **NodeDetailsPanel**: Tabbed interface (Basic Info, LLM Calls, Testing, Results) with execution browsing
3. ✅ **Interactive Node Selection**: Click any node to view all executions, supports circular flows
4. ✅ **Seamless Testing Workflow**: Direct flow from node selection to counterfactual analysis
5. ✅ **JsonModal Component**: Full-screen modal for viewing JSON content with copy functionality
6. ✅ **Enhanced ResultsVisualization**: Clickable outputs with visual expansion indicators
7. ✅ **API Format Fixes**: Backend responses now match TypeScript interfaces correctly
8. ✅ **Tab Consolidation**: Removed fragmented tabs, unified into single Flow Graph interface

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

## 11. 2D Execution Flow Visualization

### Overview

TimeMachine includes a comprehensive 2D visualization system for analyzing execution flow patterns and conditional branching in LangGraph agents. The system supports both single-run analysis and aggregate pattern detection across multiple executions.

### Conditional Branching Support

✅ **CONFIRMED**: TimeMachine fully supports conditional branching visualization

- Tracks actual execution paths: Node 1 → Node 2 (sometimes) or Node 1 → Node 3 (other times)
- Preserves conditional edge mappings from original LangGraph structure
- Records execution sequences with timestamps for flow reconstruction
- Calculates branching frequencies and path statistics

### Visualization Architecture

#### Data Flow Pipeline

```
Raw Executions (SQLite) → Flow Analysis (Python) → Graph Data (JSON) → D3.js Visualization (React)
```

#### Type System (`/types/visualization.ts`)

```typescript
interface FlowNode {
  id: string;
  name: string;
  type: "start" | "node" | "end" | "conditional";
  position: { x: number; y: number };
  executionCount: number;
  avgDuration: number;
  successRate: number;
  lastExecuted?: number;
}

interface FlowEdge {
  id: string;
  source: string;
  target: string;
  executionCount: number;
  frequency: number; // Percentage of times this path was taken
  avgDuration: number;
  conditions?: string[];
  metadata?: {
    type?: "always" | "conditional" | "error";
  };
}

interface GraphLayout {
  nodes: FlowNode[];
  edges: FlowEdge[];
  statistics: FlowStatistics;
  bounds: { minX: number; maxX: number; minY: number; maxY: number };
}
```

#### Backend Flow Analysis (`/backend.py`)

**Single Run Visualization (`/api/flow-visualization/{graph_run_id}`)**:

```python
def get_flow_visualization(graph_run_id: str):
    # Get all executions for this specific run
    executions = recorder.get_graph_executions(graph_run_id)
    sorted_executions = sorted(executions, key=lambda x: x['timestamp'])

    # Build nodes with statistics
    for execution in sorted_executions:
        node_stats[node_name]['count'] += 1
        node_stats[node_name]['durations'].append(execution['duration_ms'])
        if execution['status'] == 'success':
            node_stats[node_name]['successes'] += 1

    # Build edges from execution sequence
    for i in range(len(sorted_executions) - 1):
        current = sorted_executions[i]
        next_exec = sorted_executions[i + 1]
        edge_key = f"{current['node_name']}->{next_exec['node_name']}"
        edge_stats[edge_key]['count'] += 1
```

**Aggregate Visualization (`/api/aggregate-flow-visualization`)**:

```python
def get_aggregate_flow_visualization():
    # Combine data across ALL graph runs
    for run in graph_runs:
        executions = recorder.get_graph_executions(run['graph_run_id'])
        path = [e['node_name'] for e in sorted_executions]
        all_paths.append(path)

    # Calculate branching points
    for source, targets in edge_sources.items():
        if len(targets) > 1:  # Multiple outgoing edges = branching
            branching_points.append({
                'nodeId': source,
                'branches': targets
            })

    # Path variability analysis
    unique_paths = len(set([tuple(path) for path in all_paths]))
    path_variability = (unique_paths - 1) / max(1, total_runs)
```

#### Frontend Visualization (`ExecutionFlowVisualization.tsx`)

**Technology Stack**:

- **React + TypeScript**: Component architecture and type safety
- **D3.js v7**: High-performance SVG rendering and interaction
- **Framer Motion**: Smooth animations and transitions
- **TimeMachine Design System**: Glass morphism styling

**Core Features**:

```typescript
// Interactive D3.js visualization with zoom/pan
const zoom = d3
  .zoom<SVGSVGElement, unknown>()
  .scaleExtent([0.1, 5])
  .on("zoom", (event) => {
    g.attr("transform", event.transform);
  });

// Dynamic visual encoding
nodes
  .append("circle")
  .attr("r", (d) => Math.max(20, Math.min(50, d.executionCount * 5))) // Size = frequency
  .attr("fill", (d) => {
    if (d.type === "start") return "rgba(34, 197, 94, 0.2)";
    if (d.type === "conditional") return "rgba(59, 130, 246, 0.2)";
    return "rgba(156, 163, 175, 0.2)";
  });

// Edge thickness represents frequency
edges
  .attr("stroke-width", (d) => Math.max(1, d.frequency / 20))
  .attr(
    "stroke",
    (d) => `rgba(156, 163, 175, ${Math.max(0.3, d.frequency / 100)})`
  );
```

**Visual Encoding System**:

_Node Representations_:

- **Size**: Proportional to execution frequency (larger = more executions)
- **Color**: Type-based (green=start, red=end, blue=conditional, gray=regular)
- **Badges**: Show execution count numbers
- **Glow**: Hover and selection feedback

_Edge Representations_:

- **Thickness**: Path frequency (thick = common path, thin = rare path)
- **Opacity**: Usage intensity (solid = always used, faded = sometimes used)
- **Labels**: Show percentage frequency ("80%", "20%")
- **Arrows**: Indicate execution direction

_Interactive Elements_:

- **Zoom/Pan Controls**: Navigate large graphs
- **Click Selection**: View detailed node/edge statistics
- **Hover Effects**: Highlight elements with glow
- **Reset View**: Auto-center and optimal zoom

#### Integration Points

**Navigation Tabs**:

- **"Flow Graph"**: Single run visualization (requires selected run)
- **"All Flows"**: Aggregate pattern analysis (always available)

**UI Integration** (`/app/page.tsx`):

```typescript
{
  activeTab === "flow" && selectedRun && (
    <ExecutionFlowVisualization
      graphRunId={selectedRun.graph_run_id}
      onNodeSelect={(node) => console.log("Selected node:", node)}
      onEdgeSelect={(edge) => console.log("Selected edge:", edge)}
    />
  );
}

{
  activeTab === "aggregate-flow" && (
    <AggregateFlowVisualization
      onNodeSelect={(node) => console.log("Selected aggregate node:", node)}
      onEdgeSelect={(edge) => console.log("Selected aggregate edge:", edge)}
    />
  );
}
```

### Statistical Analysis

**Flow Statistics Computed**:

```typescript
interface FlowStatistics {
  totalRuns: number;
  mostCommonPath: string[]; // Most frequently executed sequence
  branchingPoints: Array<{
    // Nodes with multiple output paths
    nodeId: string;
    branches: Array<{
      targetNode: string;
      frequency: number; // % of time this branch is taken
    }>;
  }>;
  deadEnds: string[]; // Nodes that don't lead anywhere
  averagePathLength: number; // Mean number of nodes per execution
  pathVariability: number; // 0-1 score of execution diversity
}
```

**Branching Analysis Example**:

```
Node "router" has 3 branches:
├─ "process_text" (60% frequency)    ← Most common path
├─ "process_image" (30% frequency)   ← Secondary path
└─ "error_handler" (10% frequency)   ← Error path
```

### Conditional Branching Visualization

**How Branching is Detected and Visualized**:

1. **Execution Tracking**: Each node execution is timestamped
2. **Sequence Analysis**: Backend reconstructs flow from execution order
3. **Pattern Detection**: Multiple paths from same node = conditional branching
4. **Frequency Calculation**: "Node A → Node B" occurs in X% of runs
5. **Visual Representation**: Edge thickness and labels show frequencies

**Example Conditional Flow**:

```
          ┌─────────────┐
          │    Input    │
          │   Analyzer  │
          └──────┬──────┘
                 │
        ┌────────▼────────┐
        │   Conditional   │ ◄─── Branching Point
        │     Router      │
        └─────────────────┘
         │        │        │
    80%  │   15%  │   5%   │
         ▼        ▼        ▼
   ┌─────────┐ ┌──────┐ ┌──────┐
   │  Main   │ │ Alt  │ │Error │
   │Process  │ │Path  │ │ Path │
   └─────────┘ └──────┘ └──────┘
```

### Performance Optimizations

**Backend Optimizations**:

- Efficient SQL queries for execution sequence analysis
- Caching of aggregate statistics for large datasets
- Optimized JSON serialization for complex graph structures

**Frontend Optimizations**:

- D3.js for 60fps smooth interactions
- Virtualization for large graphs (planned)
- Debounced zoom/pan operations
- Efficient React re-rendering with useMemo/useCallback

### Future Extensions

**Planned Enhancements**:

- **Force-directed layout**: Automatic optimal node positioning
- **Time-based filtering**: Analyze patterns within specific timeframes
- **Error path highlighting**: Visually emphasize failure patterns
- **Interactive filtering**: Filter by success rate, duration, node type
- **Export capabilities**: Save visualizations as SVG/PNG
- **Animation playback**: Replay execution sequences step-by-step
- **Comparative analysis**: Side-by-side flow comparison between different configurations

### Installation and Usage

**Dependencies** (`package.json`):

```json
{
  "dependencies": {
    "d3": "^7.8.5"
    // ... other deps
  },
  "devDependencies": {
    "@types/d3": "^7.4.3"
    // ... other dev deps
  }
}
```

**Quick Start**:

```bash
cd web
npm install          # Installs D3.js and TypeScript definitions
npm run dev          # Start development server
python backend.py    # Start FastAPI backend (separate terminal)
```

**Navigation**:

1. Record agent executions using TimeMachine decorators
2. Open web interface at http://localhost:3000
3. Select a graph run → "Flow Graph" tab shows individual execution flow
4. "All Flows" tab shows aggregate patterns across all runs
5. Click nodes/edges for detailed statistics and analysis
6. Use zoom controls for navigation of complex graphs

The 2D visualization system provides comprehensive analysis of both individual execution patterns and aggregate behavior across multiple runs, making it easy to understand conditional branching, identify bottlenecks, and optimize agent performance.
