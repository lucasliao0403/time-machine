'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, Play, BarChart3, Settings, Database, Sparkles, ArrowRight, GitBranch } from 'lucide-react';
import { GraphRun, NodeExecution, CounterfactualAnalysis, Stats } from '@/types';
import GraphRunsList from '@/components/GraphRunsList';
import ExecutionDetails from '@/components/ExecutionDetails';
import CounterfactualPanel from '@/components/CounterfactualPanel';
import ResultsVisualization from '@/components/ResultsVisualization';
import StatsPanel from '@/components/StatsPanel';
import ExecutionFlowVisualization from '@/components/ExecutionFlowVisualization';
import AggregateFlowVisualization from '@/components/AggregateFlowVisualization';
import api from '@/lib/api';

type TabId = 'runs' | 'executions' | 'counterfactuals' | 'results' | 'stats' | 'flow' | 'aggregate-flow';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
  description: string;
}

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
      duration: 0.15,
    },
  },
};

const tabVariants = {
  hidden: { y: -10, opacity: 0 },
  visible: { y: 0, opacity: 1 },
  exit: { y: 10, opacity: 0 },
};

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabId>('runs');
  const [selectedRun, setSelectedRun] = useState<GraphRun | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<NodeExecution | null>(null);
  const [counterfactualResults, setCounterfactualResults] = useState<CounterfactualAnalysis | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const statsData = await api.getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleRunSelect = (run: GraphRun) => {
    setSelectedRun(run);
    setSelectedExecution(null);
    setCounterfactualResults(null);
    setActiveTab('executions');
  };

  const handleExecutionSelect = (execution: NodeExecution) => {
    setSelectedExecution(execution);
    setCounterfactualResults(null);
    setActiveTab('counterfactuals');
  };

  const handleCounterfactualResults = (results: CounterfactualAnalysis) => {
    setCounterfactualResults(results);
    setActiveTab('results');
  };

  const tabs: Tab[] = [
    { 
      id: 'runs', 
      label: 'Graph Runs', 
      icon: Database, 
      description: 'View recorded agent executions'
    },
    { 
      id: 'executions', 
      label: 'Executions', 
      icon: Clock, 
      disabled: !selectedRun,
      description: 'Analyze individual node executions'
    },
    { 
      id: 'counterfactuals', 
      label: 'Testing', 
      icon: Settings, 
      disabled: !selectedExecution,
      description: 'Run "what if" scenarios'
    },
    { 
      id: 'results', 
      label: 'Results', 
      icon: BarChart3, 
      disabled: !counterfactualResults,
      description: 'Compare and visualize outcomes'
    },
    { 
      id: 'flow', 
      label: 'Flow Graph', 
      icon: GitBranch,
      disabled: !selectedRun,
      description: 'Visualize execution flow and branching'
    },
    { 
      id: 'aggregate-flow', 
      label: 'All Flows', 
      icon: Sparkles,
      description: 'Aggregate flow patterns across all runs'
    },
    { 
      id: 'stats', 
      label: 'Statistics', 
      icon: Play,
      description: 'View database metrics and insights'
    },
  ];

  const currentTab = tabs.find(tab => tab.id === activeTab);

  return (
    <motion.div 
      className="min-h-screen"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {/* Animated Header */}
      <motion.header 
        className="sticky top-0 z-40"
        variants={itemVariants}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Clock className="h-10 w-10 text-gray-100" />
                <motion.div
                  className="absolute -inset-2  rounded-full blur-md"
                  animate={{ 
                    scale: [1, 1.1, 1],
                    opacity: [0.2, 0.4, 0.2] 
                  }}
                  transition={{ 
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              </div>
              <div>
                <h1 className="text-3xl font-medium bg-gradient-to-r from-gray-100 to-gray-300 bg-clip-text text-transparent">
                  TimeMachine
                </h1>
                <p className="text-gray-300 text-sm font-medium">
                  Branch Testing for LangGraph Agents
                </p>
              </div>
            </div>
            
            {stats && (
              <div className="px-5 py-3 text-sm">
                <div className="flex items-center space-x-5 text-gray-200">
                  <span className="flex items-center space-x-2">
                    <Database className="h-4 w-4 text-gray-300" />
                    <span className="font-semibold">{stats.total_graph_runs}</span>
                    <span className="text-gray-300 font-medium">runs</span>
                  </span>
                  <span className="text-gray-400">•</span>
                  <span className="flex items-center space-x-2">
                    <Play className="h-4 w-4 text-gray-300" />
                    <span className="font-semibold">{stats.total_executions}</span>
                    <span className="text-gray-300 font-medium">executions</span>
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.header>

      {/* Modern Navigation */}
      <motion.nav 
        className="sticky top-[88px] z-30"
        variants={itemVariants}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 py-2">
            {tabs.map((tab, index) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              const isDisabled = tab.disabled;
              
              return (
                <motion.button
                  key={tab.id}
                  onClick={() => !isDisabled && setActiveTab(tab.id)}
                  className={`
                    relative flex items-center space-x-2 px-5 py-3 rounded-2xl font-normal text-sm transition-all
                    ${isActive 
                      ? 'text-gray-100 bg-apple-glass shadow-frosted font-semibold' 
                      : isDisabled 
                        ? 'text-gray-500 cursor-not-allowed'
                        : 'text-gray-300 hover:text-gray-200 hover:bg-gray-300/10 font-medium'
                    }
                  `}
                  disabled={isDisabled}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 bg-apple-glass border border-gray-300/12 rounded-2xl"
                      transition={{ type: "tween", duration: 0.2, ease: "easeOut" }}
                    />
                  )}
                  <Icon className={`h-4 w-4 relative z-10 ${isDisabled ? 'opacity-50' : ''}`} />
                  <span className="relative z-10">{tab.label}</span>
                  {!isDisabled && isActive && (
                    <ArrowRight className="h-3 w-3 relative z-10" />
                  )}
                </motion.button>
              );
            })}
          </div>
          
          {/* Tab Description */}
          {currentTab && (
            <motion.div 
              className="pb-4 pt-2"
              key={activeTab}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <p className="text-gray-300 text-sm max-w-2xl font-medium">
                <Sparkles className="inline h-4 w-4 mr-2 text-gray-400" />
                {currentTab.description}
              </p>
            </motion.div>
          )}
        </div>
      </motion.nav>

      {/* Main Content with Smooth Transitions */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            variants={tabVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'runs' && (
              <GraphRunsList onRunSelect={handleRunSelect} selectedRun={selectedRun} />
            )}
            
            {activeTab === 'executions' && selectedRun && (
              <ExecutionDetails 
                graphRun={selectedRun} 
                onExecutionSelect={handleExecutionSelect}
                selectedExecution={selectedExecution}
              />
            )}
            
            {activeTab === 'counterfactuals' && selectedExecution && (
              <CounterfactualPanel 
                execution={selectedExecution}
                onResults={handleCounterfactualResults}
              />
            )}
            
            {activeTab === 'results' && counterfactualResults && (
              <ResultsVisualization results={counterfactualResults} />
            )}
            
            {activeTab === 'flow' && selectedRun && (
              <ExecutionFlowVisualization 
                graphRunId={selectedRun.graph_run_id}
                onNodeSelect={(node) => {
                  // TODO: Enhance with node selection functionality
                  console.log('Selected node:', node);
                }}
                onEdgeSelect={(edge) => {
                  // TODO: Enhance with edge selection functionality
                  console.log('Selected edge:', edge);
                }}
              />
            )}
            
            {activeTab === 'aggregate-flow' && (
              <AggregateFlowVisualization 
                onNodeSelect={(node) => {
                  // TODO: Could navigate to specific runs with this node
                  console.log('Selected aggregate node:', node);
                }}
                onEdgeSelect={(edge) => {
                  // TODO: Could filter runs by this edge pattern
                  console.log('Selected aggregate edge:', edge);
                }}
              />
            )}
            
            {activeTab === 'stats' && (
              <StatsPanel stats={stats} onRefresh={loadStats} />
            )}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Ambient Effects */}
      <div className="fixed bottom-8 right-8 pointer-events-none">
        <motion.div
          className="w-40 h-40  rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>
    </motion.div>
  );
}
