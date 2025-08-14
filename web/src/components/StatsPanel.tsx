import React from 'react';
import { Database, Activity, Clock, RefreshCw } from 'lucide-react';
import { Stats } from '@/types';

interface StatsPanelProps {
  stats: Stats | null;
  onRefresh: () => void;
}

const StatsPanel: React.FC<StatsPanelProps> = ({ stats, onRefresh }) => {
  if (!stats) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Stats Available</h3>
          <p className="text-gray-600 mb-4">Unable to load database statistics.</p>
          <button
            onClick={onRefresh}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Database Statistics</h2>
        <button
          onClick={onRefresh}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Graph Runs</h3>
              <p className="text-3xl font-bold text-blue-600">{stats.total_graph_runs}</p>
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Total agent executions recorded
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Node Executions</h3>
              <p className="text-3xl font-bold text-green-600">{stats.total_executions}</p>
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Individual node recordings
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center">
            <Database className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Average per Run</h3>
              <p className="text-3xl font-bold text-purple-600">
                {stats.total_graph_runs > 0 
                  ? Math.round(stats.total_executions / stats.total_graph_runs)
                  : 0
                }
              </p>
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Nodes per graph execution
          </p>
        </div>
      </div>

      {/* Database Info */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Database Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Database Path</dt>
            <dd className="mt-1 text-sm text-gray-900 font-mono">{stats.database_path}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Status</dt>
            <dd className="mt-1">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Active
              </span>
            </dd>
          </div>
        </div>
      </div>

      {/* Latest Run Info */}
      {stats.latest_run && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Latest Graph Run</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Run ID</dt>
              <dd className="mt-1 text-sm text-gray-900 font-mono">
                {stats.latest_run.graph_run_id}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Start Time</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {formatDate(stats.latest_run.start_time)}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Executions</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {stats.latest_run.execution_count}
              </dd>
            </div>
          </div>
        </div>
      )}

      {/* Usage Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">Getting Started</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>• <strong>Record agents:</strong> Use <code className="bg-blue-100 px-1 rounded">@timemachine.record()</code> decorator</p>
          <p>• <strong>Browse executions:</strong> Click on any graph run to see node details</p>
          <p>• <strong>Run experiments:</strong> Select an execution and try "What If" scenarios</p>
          <p>• <strong>Compare results:</strong> Visualize differences between original and modified outputs</p>
        </div>
      </div>
    </div>
  );
};

export default StatsPanel;
