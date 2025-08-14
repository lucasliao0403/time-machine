import React, { useState } from 'react';
import { Play, Settings, Thermometer, Cpu, Type, Loader2 } from 'lucide-react';
import { NodeExecution, CounterfactualAnalysis } from '@/types';
import api from '@/lib/api';

interface CounterfactualPanelProps {
  execution: NodeExecution;
  onResults: (results: CounterfactualAnalysis) => void;
}

type AnalysisType = 'temperature' | 'model' | 'custom';

interface AnalysisConfig {
  type: AnalysisType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const CounterfactualPanel: React.FC<CounterfactualPanelProps> = ({
  execution,
  onResults
}) => {
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisType>('temperature');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Configuration options
  const [temperatureValues, setTemperatureValues] = useState<string>('0.1, 0.5, 0.9');
  const [modelNames, setModelNames] = useState<string>('gpt-3.5-turbo, gpt-4o-mini');
  const [customModifications, setCustomModifications] = useState<string>('{"temperature": 0.8}');

  const analysisTypes: AnalysisConfig[] = [
    {
      type: 'temperature',
      label: 'Temperature Sensitivity',
      icon: Thermometer,
      description: 'Test how different temperature values affect creativity and consistency'
    },
    {
      type: 'model',
      label: 'Model Comparison',
      icon: Cpu,
      description: 'Compare outputs across different AI models'
    },
    {
      type: 'custom',
      label: 'Custom Parameters',
      icon: Settings,
      description: 'Test arbitrary parameter modifications'
    }
  ];

  const runAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      let results: CounterfactualAnalysis;

      switch (selectedAnalysis) {
        case 'temperature':
          const temps = temperatureValues.split(',').map(t => parseFloat(t.trim())).filter(t => !isNaN(t));
          results = await api.analyzeTemperatureSensitivity(execution.id, temps);
          break;

        case 'model':
          const models = modelNames.split(',').map(m => m.trim()).filter(m => m.length > 0);
          results = await api.analyzeModelAlternatives(execution.id, models);
          break;

        case 'custom':
          const modifications = JSON.parse(customModifications);
          const customResult = await api.runCustomCounterfactual(execution.id, modifications, 'custom');
          // Convert single result to analysis format
          results = {
            scenarios: [{
              scenario: {
                name: 'Custom Modification',
                modifications
              },
              replay_result: customResult
            }],
            insights: customResult.success ? ['Custom modification executed successfully'] : ['Custom modification failed'],
            recommendations: []
          };
          break;

        default:
          throw new Error('Unknown analysis type');
      }

      onResults(results);
    } catch (err) {
      setError('Analysis failed: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const renderConfigSection = () => {
    switch (selectedAnalysis) {
      case 'temperature':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Temperature Values (comma-separated)
            </label>
            <input
              type="text"
              value={temperatureValues}
              onChange={(e) => setTemperatureValues(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="0.1, 0.5, 0.9"
            />
            <p className="mt-1 text-xs text-gray-500">
              Values between 0.0 (deterministic) and 1.0 (creative)
            </p>
          </div>
        );

      case 'model':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Model Names (comma-separated)
            </label>
            <input
              type="text"
              value={modelNames}
              onChange={(e) => setModelNames(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="gpt-3.5-turbo, gpt-4o-mini"
            />
            <p className="mt-1 text-xs text-gray-500">
              OpenAI model names (e.g., gpt-3.5-turbo, gpt-4, gpt-4o-mini)
            </p>
          </div>
        );

      case 'custom':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Modifications (JSON)
            </label>
            <textarea
              value={customModifications}
              onChange={(e) => setCustomModifications(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-mono text-sm"
              placeholder='{"temperature": 0.8, "max_tokens": 100}'
            />
            <p className="mt-1 text-xs text-gray-500">
              JSON object with parameter modifications
            </p>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">What If Analysis</h2>
        <p className="text-sm text-gray-600">
          Selected execution: <span className="font-medium">{execution.node_name}</span> • 
          Run counterfactual experiments to see how different parameters affect the output
        </p>
      </div>

      {/* Analysis Type Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {analysisTypes.map((analysis) => {
          const Icon = analysis.icon;
          const isSelected = selectedAnalysis === analysis.type;
          
          return (
            <button
              key={analysis.type}
              onClick={() => setSelectedAnalysis(analysis.type)}
              className={`
                p-4 border-2 rounded-lg text-left transition-all
                ${isSelected 
                  ? 'border-primary-500 bg-primary-50' 
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }
              `}
            >
              <div className="flex items-center space-x-3 mb-2">
                <Icon className={`h-5 w-5 ${isSelected ? 'text-primary-600' : 'text-gray-400'}`} />
                <h3 className={`font-medium ${isSelected ? 'text-primary-900' : 'text-gray-900'}`}>
                  {analysis.label}
                </h3>
              </div>
              <p className="text-sm text-gray-600">
                {analysis.description}
              </p>
            </button>
          );
        })}
      </div>

      {/* Configuration Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Configure {analysisTypes.find(a => a.type === selectedAnalysis)?.label}
        </h3>
        
        {renderConfigSection()}

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="mt-6">
          <button
            onClick={runAnalysis}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {loading ? 'Running Analysis...' : 'Run Analysis'}
          </button>
        </div>
      </div>

      {/* Execution Details */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Execution Details</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Node:</span>
            <span className="ml-2 font-medium">{execution.node_name}</span>
          </div>
          <div>
            <span className="text-gray-600">Status:</span>
            <span className="ml-2 font-medium capitalize">{execution.status}</span>
          </div>
          <div>
            <span className="text-gray-600">Duration:</span>
            <span className="ml-2 font-medium">{Math.round(execution.duration_ms)}ms</span>
          </div>
          <div>
            <span className="text-gray-600">Timestamp:</span>
            <span className="ml-2 font-medium">
              {new Date(execution.timestamp * 1000).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CounterfactualPanel;
