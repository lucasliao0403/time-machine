import React from "react";

import {
  Database,
  Activity,
  Clock,
  RefreshCw,
  TrendingUp,
  BarChart3,
  Zap,
  Code2,
} from "lucide-react";
import { Stats } from "@/types";

interface StatsPanelProps {
  stats: Stats | null;
  onRefresh: () => void;
}

const StatsPanel: React.FC<StatsPanelProps> = ({ stats, onRefresh }) => {
  if (!stats) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="apple-glass-card p-12 text-center max-w-md">
          <Database className="h-16 w-16 text-gray-400 mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-100 mb-3">
            No Stats Available
          </h3>
          <p className="text-gray-300 mb-6 leading-relaxed font-medium">
            Unable to load database statistics. Please check your connection.
          </p>
          <button
            onClick={onRefresh}
            className="inline-flex items-center px-6 py-3 apple-glass-card text-gray-200 rounded-2xl transition-all border border-gray-300/20 hover:bg-gray-300/10"
          >
            <RefreshCw className="h-5 w-5 mr-2" />
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-100 mb-1">
            Database Statistics
          </h2>
          <p className="text-gray-300 font-medium">
            Real-time metrics and analytics
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="inline-flex items-center px-4 py-2 apple-glass-card text-sm font-medium text-gray-200 transition-all border border-gray-300/20 hover:bg-gray-300/10"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="apple-glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="p-3 rounded-2xl">
                <Activity className="h-6 w-6 text-gray-300" />
              </div>
            </div>
            <TrendingUp className="h-5 w-5 text-gray-400" />
          </div>
          <h3 className="text-sm font-medium text-gray-300 mb-1">Graph Runs</h3>
          <p className="text-3xl font-semibold text-gray-100 mb-2">
            {stats.total_graph_runs}
          </p>
          <p className="text-xs text-gray-400 font-medium">
            Total agent executions recorded
          </p>
        </div>

        <div className="apple-glass-card p-6 ">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="p-3 rounded-2xl ">
                <Clock className="h-6 w-6 text-gray-400" />
              </div>
            </div>
            <Zap className="h-5 w-5 text-gray-400" />
          </div>
          <h3 className="text-sm font-medium text-gray-300 mb-1">
            Node Executions
          </h3>
          <p className="text-3xl font-semibold text-gray-100 mb-2">
            {stats.total_executions}
          </p>
          <p className="text-xs text-gray-400 font-medium">
            Individual node recordings
          </p>
        </div>

        <div className="apple-glass-card p-6 ">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="p-3 rounded-2xl ">
                <BarChart3 className="h-6 w-6 text-gray-400" />
              </div>
            </div>
            <TrendingUp className="h-5 w-5 text-gray-400" />
          </div>
          <h3 className="text-sm font-medium text-gray-300 mb-1">
            Average per Run
          </h3>
          <p className="text-3xl font-semibold text-gray-100 mb-2">
            {stats.total_graph_runs > 0
              ? Math.round(stats.total_executions / stats.total_graph_runs)
              : 0}
          </p>
          <p className="text-xs text-gray-400 font-medium">
            Nodes per graph execution
          </p>
        </div>
      </div>

      {/* Database Info */}
      <div className="apple-glass-card p-6">
        <h3 className="text-lg font-semibold text-gray-300 mb-6 flex items-center">
          <Database className="h-5 w-5 mr-2 text-gray-400" />
          Database Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <dt className="text-sm font-medium text-gray-300 mb-2">
              Database Path
            </dt>
            <dd className="text-sm text-gray-300 font-mono  px-3 py-2 rounded-xl border border-gray-300/20">
              {stats.database_path}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-300 mb-2">Status</dt>
            <dd className="mt-1">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium text-gray-400 border border-gray-300/20">
                <div className="w-2 h-2 bg-gray-400 rounded-full mr-2" />
                Active
              </span>
            </dd>
          </div>
        </div>
      </div>

      {/* Latest Run Info */}
      {stats.latest_run && (
        <div className="apple-glass-card p-6">
          <h3 className="text-lg font-semibold text-gray-300 mb-6 flex items-center">
            <Clock className="h-5 w-5 mr-2 text-gray-400" />
            Latest Graph Run
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <dt className="text-sm font-medium text-gray-300 mb-2">Run ID</dt>
              <dd className="text-sm text-gray-300 font-mono  px-3 py-2 rounded-xl border border-gray-300/20">
                {stats.latest_run.graph_run_id}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-300 mb-2">
                Start Time
              </dt>
              <dd className="text-sm text-gray-300  px-3 py-2 rounded-xl border border-gray-300/20">
                {formatDate(stats.latest_run.start_time)}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-300 mb-2">
                Executions
              </dt>
              <dd className="text-sm text-gray-300  px-3 py-2 rounded-xl border border-gray-300/20 flex items-center">
                <Zap className="h-4 w-4 mr-2 text-gray-400" />
                {stats.latest_run.execution_count}
              </dd>
            </div>
          </div>
        </div>
      )}

      {/* Usage Tips - only show if no executions */}
      {stats.total_executions === 0 && (
        <div className="apple-glass-card border border-gray-300/20 p-6">
          <h3 className="text-lg font-semibold text-gray-300 mb-4 flex items-center">
            <Code2 className="h-5 w-5 mr-2 text-gray-400" />
            Getting Started
          </h3>
          <div className="text-sm text-gray-400 space-y-3 font-medium">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-gray-400 rounded-full mt-2 flex-shrink-0" />
              <p>
                <strong className="text-gray-300 font-medium">
                  Record agents:
                </strong>{" "}
                Use{" "}
                <code className=" px-2 py-1 rounded text-gray-400 border border-gray-300/20 font-mono">
                  @timemachine.record()
                </code>{" "}
                decorator
              </p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-gray-400 rounded-full mt-2 flex-shrink-0" />
              <p>
                <strong className="text-gray-300 font-medium">
                  Browse executions:
                </strong>{" "}
                Click on any graph run to see node details
              </p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-gray-400 rounded-full mt-2 flex-shrink-0" />
              <p>
                <strong className="text-gray-300 font-medium">
                  Run experiments:
                </strong>{" "}
                Select an execution and try "What If" scenarios
              </p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-gray-400 rounded-full mt-2 flex-shrink-0" />
              <p>
                <strong className="text-gray-300 font-medium">
                  Compare results:
                </strong>{" "}
                Visualize differences between original and modified outputs
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsPanel;
