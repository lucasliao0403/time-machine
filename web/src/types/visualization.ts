/**
 * Type definitions for 2D execution flow visualization
 */

export interface FlowNode {
  id: string;
  name: string;
  type: 'start' | 'node' | 'end' | 'conditional';
  position: { x: number; y: number };
  executionCount: number;
  avgDuration: number;
  successRate: number;
  lastExecuted?: number;
  llmCalls?: Array<{
    model_name: string;
    prompt: string;
    response: string;
    tokens_used: number;
    temperature: number;
    duration_ms: number;
  }>;
  metadata?: {
    description?: string;
    category?: string;
  };
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  executionCount: number;
  frequency: number; // Percentage of times this path was taken
  avgDuration: number;
  conditions?: string[]; // Conditional logic if available
  metadata?: {
    description?: string;
    type?: 'always' | 'conditional' | 'error';
  };
}

export interface ExecutionPath {
  runId: string;
  timestamp: number;
  nodes: Array<{
    nodeId: string;
    executionId: string;
    timestamp: number;
    duration: number;
    status: 'success' | 'error';
    inputState?: Record<string, any>;
    outputState?: Record<string, any>;
  }>;
  edges: Array<{
    from: string;
    to: string;
    timestamp: number;
  }>;
}

export interface FlowStatistics {
  totalRuns: number;
  mostCommonPath: string[];
  branchingPoints: Array<{
    nodeId: string;
    branches: Array<{
      targetNode: string;
      frequency: number;
      conditions?: string;
    }>;
  }>;
  deadEnds: string[];
  averagePathLength: number;
  pathVariability: number; // 0-1 score of how much paths vary
}

export interface VisualizationConfig {
  layout: 'force' | 'hierarchical' | 'circular';
  showLabels: boolean;
  showStatistics: boolean;
  highlightMode: 'none' | 'frequency' | 'duration' | 'errors';
  timeRange?: {
    start: number;
    end: number;
  };
  filterRuns?: string[];
}

export interface GraphLayout {
  nodes: FlowNode[];
  edges: FlowEdge[];
  statistics: FlowStatistics;
  bounds: {
    minX: number;
    maxX: number;
    minY: number;
    maxY: number;
  };
}
