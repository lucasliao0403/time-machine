import axios, { AxiosInstance } from 'axios';
import {
  GraphRun,
  NodeExecution,
  CounterfactualAnalysis,
  Stats,
  CounterfactualRequest,
  CounterfactualResult
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class TimeMachineAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
  }

  async getGraphRuns(): Promise<GraphRun[]> {
    const response = await this.client.get<GraphRun[]>('/api/graph-runs');
    return response.data;
  }

  async getGraphExecutions(graphRunId: string): Promise<NodeExecution[]> {
    const response = await this.client.get<NodeExecution[]>(`/api/graph-runs/${graphRunId}/executions`);
    return response.data;
  }

  async getExecution(executionId: string): Promise<NodeExecution> {
    const response = await this.client.get<NodeExecution>(`/api/executions/${executionId}`);
    return response.data;
  }

  async analyzeTemperatureSensitivity(
    executionId: string, 
    temperatures: number[] = [0.1, 0.5, 0.9]
  ): Promise<CounterfactualAnalysis> {
    const response = await this.client.post<CounterfactualAnalysis>('/api/counterfactuals/temperature', {
      execution_id: executionId,
      modifications: { temperatures },
      modification_type: 'temperature'
    });
    return response.data;
  }

  async analyzeModelAlternatives(
    executionId: string, 
    models: string[] = ['gpt-3.5-turbo', 'gpt-4o-mini']
  ): Promise<CounterfactualAnalysis> {
    const response = await this.client.post<CounterfactualAnalysis>('/api/counterfactuals/models', {
      execution_id: executionId,
      modifications: { models },
      modification_type: 'model'
    });
    return response.data;
  }

  async runCustomCounterfactual(
    executionId: string, 
    modifications: Record<string, any>, 
    modificationType: string
  ): Promise<CounterfactualResult> {
    const response = await this.client.post<CounterfactualResult>('/api/counterfactuals/custom', {
      execution_id: executionId,
      modifications,
      modification_type: modificationType
    });
    return response.data;
  }

  async getStats(): Promise<Stats> {
    const response = await this.client.get<Stats>('/api/stats');
    return response.data;
  }
}

const api = new TimeMachineAPI();
export default api;
