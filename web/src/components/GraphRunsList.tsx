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
        <div className="frosted-card px-8 py-6 text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-glass-200 mx-auto mb-3" />
          <span className="text-glass-100 font-normal loading-dots">Loading graph runs</span>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div 
        className="apple-glass-card border-error/20 p-6"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <div className="flex items-center mb-4">
          <AlertCircle className="h-6 w-6 text-error" />
          <span className="ml-3 text-glass-200 font-normal">{error}</span>
        </div>
        <motion.button
          onClick={loadGraphRuns}
          className="px-4 py-2 apple-glass-card text-gray-300 rounded-2xl transition-all"
          whileHover={{}}
          whileTap={{ scale: 0.98 }}
        >
          Try again
        </motion.button>
      </motion.div>
    );
  }

  if (runs.length === 0) {
    return (
      <motion.div 
        className="text-center py-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="frosted-card p-12 max-w-md mx-auto">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          >
            <Calendar className="h-16 w-16 text-glass-500 mx-auto mb-6" />
          </motion.div>
          <h3 className="text-xl font-light text-glass-200 mb-3">No Graph Runs Found</h3>
          <p className="text-glass-400 mb-6 leading-relaxed font-light">
            Run a TimeMachine-recorded agent to see execution data here.
          </p>
          <motion.button
            onClick={loadGraphRuns}
            className="inline-flex items-center px-6 py-3  text-glass-300 rounded-2xl  transition-all border border-accent-400/20 hover-glass"
            whileHover={{}}
            whileTap={{ scale: 0.98 }}
          >
          <RefreshCw className="h-5 w-5 mr-2" />
            Refresh
          </motion.button>
        </div>
      </motion.div>
    );
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 100,
        damping: 12,
      },
    },
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-100 mb-1">Graph Runs</h2>
          <p className="text-gray-300 font-medium">Recorded agent execution sessions</p>
        </div>
        <motion.button
          onClick={loadGraphRuns}
          className="inline-flex items-center px-4 py-2 apple-glass-card text-sm font-medium text-gray-200 hover:text-gray-100 transition-all hover-minimal"
          whileTap={{ scale: 0.98 }}
          transition={{ type: "tween", duration: 0.15 }}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </motion.button>
      </div>

      {/* Animated Runs List - only this re-animates */}
      <motion.div 
        className="space-y-3"
        key={runs.length} // Force re-animation only when runs change
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {runs.map((run, index) => (
          <motion.div
            key={run.graph_run_id}
            variants={itemVariants}
            custom={index}
          >
            <motion.button
              onClick={() => onRunSelect(run)}
              className="w-full text-left apple-glass-card px-6 py-5 focus:outline-none transition-all relative"
                whileHover={{}}
                whileTap={{ scale: 0.998 }}
              >
                {selectedRun?.graph_run_id === run.graph_run_id && (
                  <div className="absolute left-0 top-0 bottom-0 w-1"></div>
                )}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <motion.div
                      whileHover={{}}
                      transition={{ type: "spring" as const, stiffness: 400, damping: 17 }}
                    >
                      {getStatusIcon(run.status)}
                    </motion.div>
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
            </motion.button>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};

export default GraphRunsList;
