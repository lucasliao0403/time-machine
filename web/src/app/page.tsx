'use client';

import React, { useState, useEffect } from 'react';
import { Clock, Play, BarChart3, Settings, Database } from 'lucide-react';
import { GraphRun, NodeExecution, CounterfactualAnalysis, Stats } from '@/types';
import GraphRunsList from '@/components/GraphRunsList';
import ExecutionDetails from '@/components/ExecutionDetails';
import CounterfactualPanel from '@/components/CounterfactualPanel';
import ResultsVisualization from '@/components/ResultsVisualization';
import StatsPanel from '@/components/StatsPanel';
import api from '@/lib/api';

type TabId = 'runs' | 'executions' | 'counterfactuals' | 'results' | 'stats';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
}

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
    { id: 'runs', label: 'Graph Runs', icon: Database },
    { id: 'executions', label: 'Executions', icon: Clock, disabled: !selectedRun },
    { id: 'counterfactuals', label: 'What If?', icon: Settings, disabled: !selectedExecution },
    { id: 'results', label: 'Results', icon: BarChart3, disabled: !counterfactualResults },
    { id: 'stats', label: 'Stats', icon: Play },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Clock className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">TimeMachine</h1>
                <p className="text-sm text-gray-500">What If Games for LangGraph Agents</p>
              </div>
            </div>
            {stats && (
              <div className="text-sm text-gray-600">
                {stats.total_graph_runs} runs • {stats.total_executions} executions
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              const isDisabled = tab.disabled;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => !isDisabled && setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                    ${isActive 
                      ? 'border-primary-500 text-primary-600' 
                      : isDisabled 
                        ? 'border-transparent text-gray-400 cursor-not-allowed'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                  disabled={isDisabled}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
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
        
        {activeTab === 'stats' && (
          <StatsPanel stats={stats} onRefresh={loadStats} />
        )}
      </main>
    </div>
  );
}
