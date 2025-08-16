# Unified Flow Interface Design

## Overview

This document outlines the design for a unified flow visualization interface that combines:

- 2D flow graph visualization
- Node execution details
- Counterfactual testing capabilities
- All in a single, cohesive interface

## Current State Problems

### Current Interface Issues

1. **Fragmented Experience**: Users must switch between multiple tabs (Executions, Flow Graph, Testing)
2. **Context Loss**: Testing requires remembering execution IDs from other tabs
3. **Poor Discoverability**: Users may not realize testing capabilities exist
4. **Inefficient Workflow**: Click node → remember ID → switch tab → paste ID → test

### User Experience Goals

- **Single Source of Truth**: One interface for all flow-related activities
- **Contextual Actions**: Testing options appear when relevant (node selection)
- **Seamless Workflow**: Click node → see details → test immediately
- **Visual Feedback**: Testing results integrated into the flow visualization

## Implementation Clarifications (Updated)

### Confirmed Requirements

1. **Complete Tab Removal**: Remove "Executions" and "Testing" tabs entirely, keep only unified "Flow Graph" tab
2. **API Strategy**: Use existing endpoints where possible, only implement new ones if absolutely necessary
3. **Single-Run Focus**: Only implement single-run mode, no aggregate mode support
4. **Node Selection**: Show ALL executions of selected node across the graph run, allow user selection to handle circular flows
5. **Testing Integration**: Show testing controls and results within the same unified interface
6. **Flow Visualization**: Keep existing flow graph appearance and behavior, enhance with selection integration

## Proposed Architecture

### Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Flow Graph Controls (zoom, pan, layout, filters)           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │     Node A      │────│     Node B      │                │
│  │   (selected)    │    │                 │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│                     Flow Visualization                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                   Node Details Panel                        │
│ ┌─────────────────┬─────────────────┬─────────────────────┐ │
│ │   Basic Info    │   LLM Calls     │   Testing Actions   │ │
│ │                 │                 │                     │ │
│ │ • Name          │ • Prompts       │ • Temperature Test  │ │
│ │ • Executions    │ • Responses     │ • Model Test        │ │
│ │ • Success Rate  │ • Tokens        │ • Custom Test       │ │
│ │ • Duration      │ • Model Used    │ • View Results      │ │
│ └─────────────────┴─────────────────┴─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. UnifiedFlowInterface.tsx (Main Component)

```typescript
interface UnifiedFlowInterfaceProps {
  graphRunId?: string; // Single run or aggregate
  mode: "single-run" | "aggregate";
}

interface UnifiedFlowState {
  // Flow data
  flowData: GraphLayout | null;
  selectedNode: FlowNode | null;
  selectedEdge: FlowEdge | null;

  // Node details
  nodeExecutions: NodeExecution[];
  selectedExecution: NodeExecution | null;

  // Testing state
  activeTest: CounterfactualTest | null;
  testResults: CounterfactualResult[];
  testHistory: CounterfactualTest[];
}
```

#### 2. FlowVisualization.tsx (D3 Component)

- **Purpose**: Renders the 2D flow graph
- **Responsibilities**:
  - Node/edge rendering with D3.js
  - Zoom, pan, selection handling
  - Visual indicators for testing states
  - Animation support for test results

#### 3. NodeDetailsPanel.tsx (Unified Details)

```typescript
interface NodeDetailsPanelProps {
  selectedNode: FlowNode | null;
  executions: NodeExecution[];
  onTestInitiated: (test: CounterfactualTest) => void;
  onExecutionSelected: (execution: NodeExecution) => void;
}
```

**Panel Sections**:

- **Basic Info Tab**: Node stats, execution count, performance metrics
- **LLM Calls Tab**: Prompts, responses, model details for all executions
- **Testing Tab**: Counterfactual testing interface with results

#### 4. Testing Integration Components

##### TestingControls.tsx

```typescript
interface TestingControlsProps {
  selectedExecution: NodeExecution | null;
  onTestRun: (test: CounterfactualRequest) => void;
  disabled: boolean;
}
```

##### TestResults.tsx

```typescript
interface TestResultsProps {
  results: CounterfactualResult[];
  onResultSelected: (result: CounterfactualResult) => void;
}
```

## Implementation Strategy

### Phase 1: Core Integration

#### 1.1 Merge Existing Components

```typescript
// Remove separate tabs from page.tsx
const tabs = [
  { id: "overview", label: "Overview", icon: BarChart3 },
  { id: "flow", label: "Flow Graph", icon: GitBranch }, // Only this remains
  // Remove 'executions' and 'testing' tabs
];
```

#### 1.2 Enhanced Node Selection

```typescript
// In FlowVisualization.tsx
const handleNodeClick = (node: FlowNode) => {
  setSelectedNode(node);

  // Fetch all executions for this node across all relevant runs
  const executions = await api.getNodeExecutions({
    nodeId: node.id,
    graphRunId: mode === "single-run" ? graphRunId : undefined,
  });

  setNodeExecutions(executions);
  setSelectedExecution(executions[0]); // Default to most recent
};
```

#### 1.3 Contextual Testing Interface

```typescript
// Only show testing controls when:
// 1. A node is selected
// 2. The node has LLM calls
// 3. An execution is selected

const showTesting =
  selectedNode && selectedExecution && selectedExecution.llm_calls?.length > 0;
```

### Phase 2: Enhanced Interactions

#### 2.1 Visual Test Feedback

```typescript
// Show testing state in the flow visualization
interface FlowNode {
  // ... existing properties
  testingState?: "idle" | "running" | "completed" | "failed";
  testResults?: CounterfactualResult[];
}

// Visual indicators:
// - Pulsing border during testing
// - Color coding for test results
// - Badges showing improvement/degradation
```

#### 2.2 Execution Comparison

```typescript
// When multiple executions exist for a node
interface ExecutionComparison {
  executions: NodeExecution[];
  selectedExecutions: string[]; // Allow multi-select
  comparisonMetrics: {
    averageTokens: number;
    responseVariability: number;
    commonPatterns: string[];
  };
}
```

#### 2.3 Test Result Integration

```typescript
// Show test results in context
const visualizeTestResults = (results: CounterfactualResult[]) => {
  // 1. Highlight nodes with test improvements
  // 2. Show comparison overlay
  // 3. Update node statistics temporarily
  // 4. Provide "apply changes" option
};
```

### Phase 3: Advanced Features

#### 3.1 Batch Testing

```typescript
// Test multiple nodes or entire paths
interface BatchTest {
  nodeIds: string[];
  testType: "temperature" | "model" | "custom";
  configurations: TestConfiguration[];
}
```

#### 3.2 Test History & Comparison

```typescript
// Track and compare test runs
interface TestHistory {
  tests: CounterfactualTest[];
  comparisons: TestComparison[];
}
```

#### 3.3 Smart Recommendations

```typescript
// AI-powered testing suggestions
interface TestRecommendation {
  nodeId: string;
  testType: "temperature" | "model" | "prompt";
  reasoning: string;
  expectedImprovement: number;
  confidence: number;
}
```

## API Changes Required

### New Endpoints

#### Get Node Executions

```typescript
GET /api/nodes/{nodeId}/executions?graphRunId={id}
// Returns all executions for a specific node
// Optionally filtered by graph run
```

#### Batch Testing

```typescript
POST /api/testing/batch
{
  "nodeIds": ["node1", "node2"],
  "testType": "temperature",
  "configurations": [...]
}
```

### Enhanced Existing Endpoints

#### Flow Visualization Enhancement

```typescript
// Include testing metadata in flow data
interface FlowNode {
  // ... existing
  recentTests?: CounterfactualTest[];
  testingCapabilities: {
    supportsTemperature: boolean;
    supportsModel: boolean;
    supportsCustom: boolean;
  };
}
```

## Data Flow

### Selection to Testing Flow

```
1. User clicks node in visualization
   ↓
2. FlowVisualization emits node selection
   ↓
3. UnifiedFlowInterface fetches node executions
   ↓
4. NodeDetailsPanel displays execution details
   ↓
5. User selects specific execution
   ↓
6. TestingControls become available
   ↓
7. User initiates test
   ↓
8. Results displayed in TestResults component
   ↓
9. Visual feedback shown in FlowVisualization
```

### State Management

```typescript
// Use React Context for cross-component state
interface FlowInterfaceContext {
  // Selection state
  selectedNode: FlowNode | null;
  selectedExecution: NodeExecution | null;

  // Testing state
  activeTests: Map<string, CounterfactualTest>;
  testResults: Map<string, CounterfactualResult[]>;

  // Actions
  selectNode: (node: FlowNode) => void;
  runTest: (test: CounterfactualRequest) => Promise<void>;
  clearSelection: () => void;
}
```

## User Experience Scenarios

### Scenario 1: Debugging Node Performance

```
1. User sees node with low success rate in visualization
2. Clicks node → details panel opens
3. Reviews LLM calls and identifies problematic prompts
4. Clicks "Test Temperature" → runs 0.1, 0.5, 0.9
5. Sees 0.1 improves success rate by 15%
6. Applies change or saves recommendation
```

### Scenario 2: Model Comparison

```
1. User selects high-cost node (many tokens)
2. Reviews current model (gpt-4) in LLM calls
3. Clicks "Test Models" → tests gpt-3.5-turbo, claude
4. Sees gpt-3.5-turbo maintains quality with 60% cost reduction
5. Applies model change with confidence
```

### Scenario 3: Flow Optimization

```
1. User sees branching node with variable performance
2. Selects node → reviews multiple execution examples
3. Identifies pattern in successful vs failed executions
4. Tests custom prompt modifications
5. Validates improvements across execution samples
```

## Implementation Priority

### High Priority (MVP) - ✅ COMPLETED

1. ✅ **IMPLEMENTED**: Merge tabs into single Flow Graph interface
2. ✅ **IMPLEMENTED**: Enhanced node selection with execution fetching
3. ✅ **IMPLEMENTED**: Unified NodeDetailsPanel with testing integration
4. ✅ **IMPLEMENTED**: Basic testing workflow (temperature, model)
5. ✅ **IMPLEMENTED**: Test result display and comparison

## Implementation Status

### ✅ Completed Features

**UnifiedFlowInterface Component**:

- Main component that combines flow visualization, node selection, and details panel
- Handles state management for selected nodes, executions, and test results
- Uses existing API endpoints efficiently (getGraphExecutions filtered by node)

**NodeDetailsPanel Component**:

- Tabbed interface with Basic Info, LLM Calls, Testing, and Results sections
- Shows all executions for selected node (handles circular flows)
- Allows execution selection and seamless testing workflow
- Integrated CounterfactualPanel and ResultsVisualization

**Updated Page Structure**:

- Removed separate "Executions" and "Testing" tabs
- Simplified to: Graph Runs → Flow Graph → Statistics
- Direct navigation from run selection to unified flow interface

**User Experience Improvements**:

- Click node → see all executions → select execution → test immediately
- No context switching between tabs
- All testing capabilities accessible from node selection
- Visual feedback with loading states and error handling

### Medium Priority

1. Visual test feedback in flow graph
2. Execution comparison and selection
3. Test history and recommendations
4. Batch testing capabilities

### Low Priority (Future)

1. AI-powered test recommendations
2. Advanced analytics and visualizations
3. Test automation and scheduling
4. Cross-run comparison and analysis

## Benefits

### For Users

- **Reduced Cognitive Load**: Everything in one place
- **Faster Workflows**: No context switching between tabs
- **Better Discoverability**: Testing options visible when relevant
- **Visual Context**: See testing impact on flow structure

### For Development

- **Simplified Architecture**: Fewer top-level components
- **Better State Management**: Centralized selection and testing state
- **Reusable Components**: Testing components can be used elsewhere
- **Cleaner APIs**: More focused endpoints with clear responsibilities

## Success Metrics

### Usability Metrics

- Time from node selection to test initiation
- Number of tabs/clicks required for common workflows
- User satisfaction with testing discoverability

### Technical Metrics

- Component reusability score
- API call efficiency
- Bundle size impact
- Performance of unified interface

This unified interface will transform TimeMachine from a debugging tool into a comprehensive AI agent optimization platform, where users can seamlessly move from observation to experimentation to improvement.
