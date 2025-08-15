import React from 'react';
import { motion } from 'framer-motion';
import { Database, Activity, Clock, RefreshCw, TrendingUp, BarChart3, Zap, Code2 } from 'lucide-react';
import { Stats } from '@/types';

interface StatsPanelProps {
  stats: Stats | null;
  onRefresh: () => void;
}

const StatsPanel: React.FC<StatsPanelProps> = ({ stats, onRefresh }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
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

  const cardVariants = {
    hidden: { scale: 0.8, opacity: 0 },
    visible: {
      scale: 1,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 100,
        damping: 15,
      },
    },
  };

  if (!stats) {
    return (
      <motion.div 
        className="flex items-center justify-center py-16"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="apple-glass-card p-12 text-center max-w-md">
          <motion.div
            animate={{ 
              rotateY: [0, 180, 360],
              scale: [1, 1.05, 1]
            }}
            transition={{ 
              duration: 3, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <Database className="h-16 w-16 text-gray-1000 mx-auto mb-6" />
          </motion.div>
          <h3 className="text-xl font-semibold text-gray-300 mb-3">No Stats Available</h3>
          <p className="text-glass-400 mb-6 leading-relaxed font-semibold">
            Unable to load database statistics. Please check your connection.
          </p>
          <motion.button
            onClick={onRefresh}
            className="inline-flex items-center px-6 py-3  text-gray-400 rounded-2xl hover: transition-all border border-accent-400/20 hover-minimal"
            whileHover={{}}
            whileTap={{ scale: 0.98 }}
          >
            <RefreshCw className="h-5 w-5 mr-2" />
            Retry
          </motion.button>
        </div>
      </motion.div>
    );
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <motion.div 
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div 
        className="flex items-center justify-between"
        variants={itemVariants}
      >
        <div>
          <h2 className="text-2xl font-semibold text-gray-100 mb-1">Database Statistics</h2>
          <p className="text-gray-300 font-medium">Real-time metrics and insights</p>
        </div>
        <motion.button
          onClick={onRefresh}
          className="inline-flex items-center px-4 py-2 apple-glass-card text-sm font-medium text-gray-200 hover:text-gray-100 transition-all hover-minimal"
          whileTap={{ scale: 0.98 }}
          transition={{ type: "tween", duration: 0.15 }}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </motion.button>
      </motion.div>

      {/* Stats Cards */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
        variants={itemVariants}
      >
        <motion.div 
          className="apple-glass-card p-6 hover-minimal"
          variants={cardVariants}
          whileHover={{}}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <motion.div
                className="p-3 rounded-2xl "
                whileHover={{}}
                transition={{ type: "spring" as const, stiffness: 400, damping: 17 }}
              >
                <Activity className="h-6 w-6 text-gray-200" />
              </motion.div>
            </div>
            <TrendingUp className="h-5 w-5 text-success" />
          </div>
          <h3 className="text-sm font-medium text-gray-300 mb-1">Graph Runs</h3>
          <motion.p 
            className="text-3xl font-semibold text-gray-100 mb-2"
            initial={{ scale: 0.5 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: "spring" as const, stiffness: 200 }}
          >
            {stats.total_graph_runs}
          </motion.p>
          <p className="text-xs text-gray-400 font-semibold">
            Total agent executions recorded
          </p>
        </motion.div>

        <motion.div 
          className="apple-glass-card p-6 hover-minimal"
          variants={cardVariants}
          whileHover={{}}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <motion.div
                className="p-3 rounded-2xl "
                whileHover={{}}
                transition={{ type: "spring" as const, stiffness: 400, damping: 17 }}
              >
                <Clock className="h-6 w-6 text-gray-400" />
              </motion.div>
            </div>
            <Zap className="h-5 w-5 text-warning" />
          </div>
          <h3 className="text-sm font-medium text-gray-300 mb-1">Node Executions</h3>
          <motion.p 
            className="text-3xl font-semibold text-gray-100 mb-2"
            initial={{ scale: 0.5 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.4, type: "spring" as const, stiffness: 200 }}
          >
            {stats.total_executions}
          </motion.p>
          <p className="text-xs text-gray-300 font-semibold">
            Individual node recordings
          </p>
        </motion.div>

        <motion.div 
          className="apple-glass-card p-6 hover-minimal"
          variants={cardVariants}
          whileHover={{}}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <motion.div
                className="p-3 rounded-2xl "
                whileHover={{}}
                transition={{ type: "spring" as const, stiffness: 400, damping: 17 }}
              >
                <BarChart3 className="h-6 w-6 text-gray-400" />
              </motion.div>
            </div>
            <TrendingUp className="h-5 w-5 text-accent-400" />
          </div>
          <h3 className="text-sm font-medium text-gray-1000 mb-1">Average per Run</h3>
          <motion.p 
            className="text-3xl font-semibold text-gray-200 mb-2"
            initial={{ scale: 0.5 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: "spring" as const, stiffness: 200 }}
          >
            {stats.total_graph_runs > 0 
              ? Math.round(stats.total_executions / stats.total_graph_runs)
              : 0
            }
          </motion.p>
          <p className="text-xs text-gray-300 font-semibold">
            Nodes per graph execution
          </p>
        </motion.div>
      </motion.div>

      {/* Database Info */}
      <motion.div 
        className="apple-glass-card p-6"
        variants={itemVariants}
      >
        <h3 className="text-lg font-semibold text-gray-300 mb-6 flex items-center">
          <Database className="h-5 w-5 mr-2 text-glass-400" />
          Database Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <dt className="text-sm font-medium text-gray-1000 mb-2">Database Path</dt>
            <dd className="text-sm text-gray-300 font-mono  px-3 py-2 rounded-xl border border-glass-700/30">
              {stats.database_path}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-1000 mb-2">Status</dt>
            <dd className="mt-1">
              <motion.span 
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium  text-success border border-success/20"
                whileHover={{}}
              >
                <motion.div
                  className="w-2 h-2  rounded-full mr-2"
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                Active
              </motion.span>
            </dd>
          </div>
        </div>
      </motion.div>

      {/* Latest Run Info */}
      {stats.latest_run && (
        <motion.div 
          className="apple-glass-card p-6"
          variants={itemVariants}
        >
          <h3 className="text-lg font-semibold text-gray-300 mb-6 flex items-center">
            <Clock className="h-5 w-5 mr-2 text-glass-400" />
            Latest Graph Run
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <dt className="text-sm font-medium text-gray-1000 mb-2">Run ID</dt>
              <dd className="text-sm text-gray-300 font-mono  px-3 py-2 rounded-xl border border-glass-700/30">
                {stats.latest_run.graph_run_id}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-1000 mb-2">Start Time</dt>
              <dd className="text-sm text-gray-300  px-3 py-2 rounded-xl border border-glass-700/30">
                {formatDate(stats.latest_run.start_time)}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-1000 mb-2">Executions</dt>
              <dd className="text-sm text-gray-300  px-3 py-2 rounded-xl border border-glass-700/30 flex items-center">
                <Zap className="h-4 w-4 mr-2 text-glass-400" />
                {stats.latest_run.execution_count}
              </dd>
            </div>
          </div>
        </motion.div>
      )}

      {/* Usage Tips - only show if no executions */}
      {stats.total_executions === 0 && (
        <motion.div 
          className="apple-glass-card border-accent-400/15  p-6"
          variants={itemVariants}
        >
        <h3 className="text-lg font-semibold text-gray-300 mb-4 flex items-center">
          <Code2 className="h-5 w-5 mr-2 text-accent-400" />
          Getting Started
        </h3>
        <div className="text-sm text-gray-400 space-y-3 font-semibold">
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2  rounded-full mt-2 flex-shrink-0" />
            <p><strong className="text-gray-300 font-medium">Record agents:</strong> Use <code className=" px-2 py-1 rounded text-gray-400 border border-glass-700/30 font-mono">@timemachine.record()</code> decorator</p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2  rounded-full mt-2 flex-shrink-0" />
            <p><strong className="text-gray-300 font-medium">Browse executions:</strong> Click on any graph run to see node details</p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2  rounded-full mt-2 flex-shrink-0" />
            <p><strong className="text-gray-300 font-medium">Run experiments:</strong> Select an execution and try "What If" scenarios</p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2  rounded-full mt-2 flex-shrink-0" />
            <p><strong className="text-gray-300 font-medium">Compare results:</strong> Visualize differences between original and modified outputs</p>
          </div>
        </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default StatsPanel;
