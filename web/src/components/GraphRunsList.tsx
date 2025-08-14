import React, { useState, useEffect } from 'react';
import { Calendar, PlayCircle, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { GraphRun } from '@/types';
import api from '@/lib/api';

interface GraphRunsListProps {
  onRunSelect: (run: GraphRun) => void;
  selectedRun: GraphRun | null;
}

const GraphRunsList: React.FC<GraphRunsListProps> = ({ onRunSelect, selectedRun }) => {
  const [runs, setRuns] = useState<GraphRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadGraphRuns();
  }, []);

  const loadGraphRuns = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getGraphRuns();
      setRuns(data);
    } catch (err) {
      setError('Failed to load graph runs: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusIcon = (status: GraphRun['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'running':
        return <PlayCircle className="h-5 w-5 text-blue-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <CheckCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-600">Loading graph runs...</span>
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
          onClick={loadGraphRuns}
          className="mt-2 text-sm text-red-600 hover:text-red-800 transition-colors"
        >
          Try again
        </button>
      </div>
    );
  }

  if (runs.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Graph Runs Found</h3>
        <p className="text-gray-600 mb-4">
          Run a TimeMachine-recorded agent to see execution data here.
        </p>
        <button
          onClick={loadGraphRuns}
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Graph Runs</h2>
        <button
          onClick={loadGraphRuns}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {runs.map((run) => (
            <li key={run.graph_run_id}>
              <button
                onClick={() => onRunSelect(run)}
                className={`
                  w-full text-left px-6 py-4 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 transition-colors
                  ${selectedRun?.graph_run_id === run.graph_run_id ? 'bg-primary-50 border-l-4 border-primary-500' : ''}
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(run.status)}
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {run.graph_run_id}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatDate(run.start_time)}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {run.execution_count} executions
                    </div>
                    <div className="text-sm text-gray-500 capitalize">
                      {run.status}
                    </div>
                  </div>
                </div>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default GraphRunsList;
