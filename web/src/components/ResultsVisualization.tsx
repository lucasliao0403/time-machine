import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Target, AlertCircle, CheckCircle } from 'lucide-react';
import { CounterfactualAnalysis } from '@/types';

interface ResultsVisualizationProps {
  results: CounterfactualAnalysis;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

const ResultsVisualization: React.FC<ResultsVisualizationProps> = ({ results }) => {
  // Prepare data for charts
  const scenarioData = results.scenarios.map((scenario, index) => {
    // Handle different scenario name formats
    let scenarioName = 'Unknown';
    if (scenario.scenario_name) {
      scenarioName = scenario.scenario_name;
    } else if (scenario.scenario?.name) {
      scenarioName = scenario.scenario.name;
    } else if (scenario.scenario?.modifications) {
      // Generate name from modifications
      const mods = scenario.scenario.modifications;
      if (mods.temperature) scenarioName = `Temperature ${mods.temperature}`;
      else if (mods.model_name) scenarioName = `Model ${mods.model_name}`;
      else scenarioName = `Scenario ${index + 1}`;
    } else {
      scenarioName = `Scenario ${index + 1}`;
    }

    return {
      name: scenarioName,
      difference_score: scenario.replay_result?.difference_score || scenario.difference_score || 0,
      success: scenario.replay_result?.success ?? scenario.success ?? false,
      color: COLORS[index % COLORS.length]
    };
  });

  const successData = [
    { name: 'Successful', value: results.scenarios.filter(s => s.replay_result?.success || s.success).length },
    { name: 'Failed', value: results.scenarios.filter(s => !(s.replay_result?.success || s.success)).length }
  ];

  const truncateText = (text: string, maxLength: number = 100): string => {
    if (typeof text !== 'string') return String(text);
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const formatOutput = (output: any): string => {
    if (!output) return 'No output';
    
    if (typeof output === 'object') {
      // Try to extract meaningful content from messages or other structures
      if (output.messages && Array.isArray(output.messages)) {
        const lastMessage = output.messages[output.messages.length - 1];
        if (lastMessage && lastMessage.content) {
          return truncateText(lastMessage.content, 200);
        }
      }
      return truncateText(JSON.stringify(output, null, 2), 200);
    }
    
    return truncateText(String(output), 200);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Analysis Results</h2>
        <p className="text-sm text-gray-600">
          Counterfactual analysis completed • {results.scenarios.length} scenarios tested
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center">
            <Target className="h-5 w-5 text-blue-500" />
            <h3 className="ml-2 text-sm font-medium text-gray-900">Total Scenarios</h3>
          </div>
          <p className="mt-2 text-2xl font-bold text-gray-900">{results.scenarios.length}</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <h3 className="ml-2 text-sm font-medium text-gray-900">Successful</h3>
          </div>
          <p className="mt-2 text-2xl font-bold text-green-600">
            {results.scenarios.filter(s => s.replay_result?.success || s.success).length}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <h3 className="ml-2 text-sm font-medium text-gray-900">Failed</h3>
          </div>
          <p className="mt-2 text-2xl font-bold text-red-600">
            {results.scenarios.filter(s => !(s.replay_result?.success || s.success)).length}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-purple-500" />
            <h3 className="ml-2 text-sm font-medium text-gray-900">Avg. Difference</h3>
          </div>
          <p className="mt-2 text-2xl font-bold text-purple-600">
            {(results.scenarios.reduce((sum, s) => sum + (s.replay_result?.difference_score || s.difference_score || 0), 0) / results.scenarios.length).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Difference Scores Chart */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Output Difference Scores</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={scenarioData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={60}
                interval={0}
              />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [value.toFixed(3), 'Difference Score']}
                labelFormatter={(label) => `Scenario: ${label}`}
              />
              <Bar 
                dataKey="difference_score" 
                fill="#3b82f6"
                name="Difference Score"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Success Rate Pie Chart */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Success Rate</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={successData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value, percent }) => `${name}: ${value} (${(percent || 0).toFixed(0)}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {successData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={index === 0 ? '#10b981' : '#ef4444'} 
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Best Scenario */}
      {results.best_scenario && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-green-900 mb-2">Best Scenario</h3>
          <p className="text-green-800">
            <span className="font-medium">
              {results.best_scenario.scenario?.name || 
               results.best_scenario.scenario_name || 
               'Best performing scenario'}
            </span>
          </p>
          {results.best_scenario.scenario?.modifications && (
            <div className="mt-2 text-sm text-green-700">
              Modifications: {JSON.stringify(results.best_scenario.scenario.modifications, null, 2)}
            </div>
          )}
        </div>
      )}

      {/* Detailed Results */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Detailed Results</h3>
        <div className="space-y-4">
          {results.scenarios.map((scenario, index) => {
            // Get scenario name using same logic as scenarioData
            let scenarioName = 'Unknown';
            if (scenario.scenario_name) {
              scenarioName = scenario.scenario_name;
            } else if (scenario.scenario?.name) {
              scenarioName = scenario.scenario.name;
            } else if (scenario.scenario?.modifications) {
              const mods = scenario.scenario.modifications;
              if (mods.temperature) scenarioName = `Temperature ${mods.temperature}`;
              else if (mods.model_name) scenarioName = `Model ${mods.model_name}`;
              else scenarioName = `Scenario ${index + 1}`;
            } else {
              scenarioName = `Scenario ${index + 1}`;
            }

            const replayResult = scenario.replay_result || scenario;
            const isSuccess = replayResult.success;

            return (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{scenarioName}</h4>
                  <div className="flex items-center space-x-2">
                    {isSuccess ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-sm text-gray-600">
                      Difference: {(replayResult.difference_score || 0).toFixed(3)}
                    </span>
                  </div>
                </div>

                {isSuccess ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Original Output</h5>
                      <div className="bg-gray-50 p-3 rounded text-xs text-gray-600 font-mono overflow-x-auto">
                        {formatOutput(replayResult.original_output)}
                      </div>
                    </div>
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Replayed Output</h5>
                      <div className="bg-blue-50 p-3 rounded text-xs text-gray-600 font-mono overflow-x-auto">
                        {formatOutput(replayResult.replayed_output)}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-red-50 p-3 rounded">
                    <p className="text-sm text-red-800">
                      Error: {replayResult.error || 'Unknown error'}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Insights and Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {results.insights && results.insights.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-3">Insights</h3>
            <ul className="space-y-2">
              {results.insights.map((insight, index) => (
                <li key={index} className="text-sm text-blue-800">
                  • {insight}
                </li>
              ))}
            </ul>
          </div>
        )}

        {results.recommendations && results.recommendations.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-yellow-900 mb-3">Recommendations</h3>
            <ul className="space-y-2">
              {results.recommendations.map((recommendation, index) => (
                <li key={index} className="text-sm text-yellow-800">
                  • {recommendation}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsVisualization;