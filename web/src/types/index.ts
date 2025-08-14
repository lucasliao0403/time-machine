export interface GraphRun {
  graph_run_id: string;
  start_time: string;
  execution_count: number;
  status: 'completed' | 'running' | 'error';
}

export interface NodeExecution {
  id: string;
  node_name: string;
  timestamp: number;
  duration_ms: number;
  status: 'success' | 'error' | 'running';
  input_state: Record<string, any>;
  output_state: Record<string, any>;
  error_message?: string;
}

export interface CounterfactualRequest {
  execution_id: string;
  modifications: Record<string, any>;
  modification_type: 'model' | 'temperature' | 'prompt' | 'custom';
}

export interface CounterfactualResult {
  scenario_name: string;
  success: boolean;
  original_output: Record<string, any>;
  replayed_output: Record<string, any>;
  difference_score: number;
  error?: string;
}

export interface CounterfactualAnalysis {
  scenarios: Array<{
    scenario: {
      name: string;
      modifications: Record<string, any>;
    };
    replay_result: CounterfactualResult;
  }>;
  best_scenario?: {
    scenario: {
      name: string;
      modifications: Record<string, any>;
    };
  };
  insights: string[];
  recommendations: string[];
}

export interface Stats {
  total_graph_runs: number;
  total_executions: number;
  database_path: string;
  latest_run?: GraphRun;
}

export interface TemperatureConfig {
  temperatures: number[];
}

export interface ModelConfig {
  models: string[];
}

export interface CustomModification {
  [key: string]: any;
}
