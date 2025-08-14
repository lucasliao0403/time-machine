import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, AlertCircle, RefreshCw, ChevronRight } from 'lucide-react';
import { GraphRun, NodeExecution } from '@/types';
import api from '@/lib/api';

interface ExecutionDetailsProps {
  graphRun: GraphRun;
  onExecutionSelect: (execution: NodeExecution) => void;
  selectedExecution: NodeExecution | null;
}

const ExecutionDetails: React.FC<ExecutionDetailsProps> = ({
  graphRun,
  onExecutionSelect,
  selectedExecution
}) => {
  const [executions, setExecutions] = useState<NodeExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadExecutions();
  }, [graphRun.graph_run_id]);

  const loadExecutions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getGraphExecutions(graphRun.graph_run_id);
      setExecutions(data);
    } catch (err) {
      setError('Failed to load executions: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (durationMs: number): string => {
    if (durationMs < 1000) {
      return `${Math.round(durationMs)}ms`;
    }
    return `${(durationMs / 1000).toFixed(1)}s`;
  };

  const formatTimestamp = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  const getStatusIcon = (status: NodeExecution['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const truncateJson = (obj: Record<string, any>, maxLength: number = 100): string => {
    const str = JSON.stringify(obj, null, 2);
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-600">Loading executions...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <span className="ml-2 text-red-800">{error}</span>
        </div>
        <button
          onClick={loadExecutions}
          className="mt-2 text-sm text-red-600 hover:text-red-800 transition-colors"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Executions</h2>
          <p className="text-sm text-gray-600">
            Graph Run: {graphRun.graph_run_id} • {executions.length} executions
          </p>
        </div>
        <button
          onClick={loadExecutions}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {executions.map((execution, index) => (
            <li key={execution.id}>
              <button
                onClick={() => onExecutionSelect(execution)}
                className={`
                  w-full text-left px-6 py-4 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 transition-colors
                  ${selectedExecution?.id === execution.id ? 'bg-primary-50 border-l-4 border-primary-500' : ''}
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full text-sm font-medium text-gray-600">
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(execution.status)}
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {execution.node_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatTimestamp(execution.timestamp)} • {formatDuration(execution.duration_ms)}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right text-xs text-gray-500">
                      <div>Input: {Object.keys(execution.input_state).length} fields</div>
                      <div>Output: {Object.keys(execution.output_state).length} fields</div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-400" />
                  </div>
                </div>

                {execution.error_message && (
                  <div className="mt-2 text-sm text-red-600 bg-red-50 rounded p-2">
                    Error: {execution.error_message}
                  </div>
                )}

                {selectedExecution?.id === execution.id && (
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Input State</h4>
                      <pre className="bg-gray-50 p-2 rounded overflow-x-auto text-gray-600">
                        {truncateJson(execution.input_state, 200)}
                      </pre>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Output State</h4>
                      <pre className="bg-gray-50 p-2 rounded overflow-x-auto text-gray-600">
                        {truncateJson(execution.output_state, 200)}
                      </pre>
                    </div>
                  </div>
                )}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ExecutionDetails;
