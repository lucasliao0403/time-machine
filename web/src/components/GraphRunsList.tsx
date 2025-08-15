import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, PlayCircle, CheckCircle, AlertCircle, RefreshCw, Clock, Zap } from 'lucide-react';
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
        return <CheckCircle className="h-5 w-5 text-success" />;
      case 'running':
        return <PlayCircle className="h-5 w-5 text-info" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-error" />;
      default:
        return <CheckCircle className="h-5 w-5 text-glass-500" />;
    }
  };

  if (loading) {
    return (
      <motion.div 
        className="flex items-center justify-center py-16"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="apple-glass-card px-8 py-6 text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-gray-200 mx-auto mb-3" />
          <span className="text-gray-100 font-medium loading-dots">Loading graph runs</span>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <div className="apple-glass-card border border-gray-300/20 p-6">
        <div className="flex items-center mb-4">
          <AlertCircle className="h-6 w-6 text-gray-400" />
          <span className="ml-3 text-gray-100 font-medium">{error}</span>
        </div>
        <button
          onClick={loadGraphRuns}
          className="px-4 py-2 apple-glass-card text-gray-200 rounded-2xl transition-all border border-gray-300/20 hover:bg-gray-300/10"
        >
          Try again
        </button>
      </div>
    );
  }

  if (runs.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="apple-glass-card p-12 max-w-md mx-auto">
          <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-100 mb-3">No Graph Runs Found</h3>
          <p className="text-gray-300 mb-6 leading-relaxed font-medium">
            Run a TimeMachine-recorded agent to see execution data here.
          </p>
          <button
            onClick={loadGraphRuns}
            className="inline-flex items-center px-6 py-3 apple-glass-card text-gray-200 rounded-2xl transition-all border border-gray-300/20 hover:bg-gray-300/10"
          >
          <RefreshCw className="h-5 w-5 mr-2" />
            Refresh
          </button>
        </div>
      </div>
    );
  }



  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-100 mb-1">Graph Runs</h2>
          <p className="text-gray-300 font-medium">Recorded agent execution sessions</p>
        </div>
        <button
          onClick={loadGraphRuns}
          className="inline-flex items-center px-4 py-2 apple-glass-card text-sm font-medium text-gray-200 transition-all border border-gray-300/20 hover:bg-gray-300/10"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        {runs.map((run, index) => (
          <div key={run.graph_run_id}>
            <button
              onClick={() => onRunSelect(run)}
              className="w-full text-left apple-glass-card px-6 py-5 focus:outline-none transition-all relative hover:bg-gray-300/10"
              >
                {selectedRun?.graph_run_id === run.graph_run_id && (
                  <div className="absolute left-0 top-0 bottom-0 w-1"></div>
                )}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div>
                      {getStatusIcon(run.status)}
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-gray-100 mb-1">
                        {run.graph_run_id}
                      </div>
                      <div className="text-xs text-gray-300 flex items-center font-medium">
                        <Clock className="h-3 w-3 mr-1" />
                        {formatDate(run.start_time)}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-gray-100 flex items-center justify-end">
                      <Zap className="h-4 w-4 mr-1 text-gray-200" />
                      {run.execution_count} executions
                    </div>
                    <div className={`
                      text-xs capitalize px-3 py-1 rounded-full mt-1 font-medium
                      ${run.status === 'completed' ? ' text-gray-200 border border-gray-400/40' :
                        run.status === 'running' ? ' text-gray-200 border border-gray-500/40' :
                        run.status === 'error' ? ' text-gray-200 border border-gray-600/40' :
                        ' text-gray-200 border border-gray-400/30'
                      }
                    `}>
                      {run.status}
                    </div>
                  </div>
                </div>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GraphRunsList;
