import React, { useState } from "react";
import { Play, Settings, Thermometer, Cpu, Type, Loader2 } from "lucide-react";
import { NodeExecution, CounterfactualAnalysis } from "@/types";
import api from "@/lib/api";

interface CounterfactualPanelProps {
  execution: NodeExecution;
  onResults: (results: CounterfactualAnalysis) => void;
}

type AnalysisType = "temperature" | "model" | "custom";

interface AnalysisConfig {
  type: AnalysisType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const CounterfactualPanel: React.FC<CounterfactualPanelProps> = ({
  execution,
  onResults,
}) => {
  const [selectedAnalysis, setSelectedAnalysis] =
    useState<AnalysisType>("temperature");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Configuration options
  const [temperatureValues, setTemperatureValues] =
    useState<string>("0.1, 0.5, 0.9");
  const [modelNames, setModelNames] = useState<string>(
    "gpt-3.5-turbo, gpt-4o-mini"
  );
  const [customModifications, setCustomModifications] = useState<string>(
    '{"temperature": 0.8}'
  );

  const analysisTypes: AnalysisConfig[] = [
    {
      type: "temperature",
      label: "Temperature Sensitivity",
      icon: Thermometer,
      description:
        "Test how different temperature values affect creativity and consistency",
    },
    {
      type: "model",
      label: "Change Models",
      icon: Cpu,
      description: "Compare outputs across different AI models",
    },
    {
      type: "custom",
      label: "Custom Parameters",
      icon: Settings,
      description: "Test arbitrary parameter modifications",
    },
  ];

  const runAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      let results: CounterfactualAnalysis;

      switch (selectedAnalysis) {
        case "temperature":
          const temps = temperatureValues
            .split(",")
            .map((t) => parseFloat(t.trim()))
            .filter((t) => !isNaN(t));
          results = await api.analyzeTemperatureSensitivity(
            execution.id,
            temps
          );
          break;

        case "model":
          const models = modelNames
            .split(",")
            .map((m) => m.trim())
            .filter((m) => m.length > 0);
          results = await api.analyzeModelAlternatives(execution.id, models);
          break;

        case "custom":
          const modifications = JSON.parse(customModifications);
          const customResult = await api.runCustomCounterfactual(
            execution.id,
            modifications,
            "custom"
          );
          // Convert single result to analysis format
          results = {
            scenarios: [
              {
                scenario: {
                  name: "Custom Modification",
                  modifications,
                },
                replay_result: customResult,
              },
            ],
            recommendations: [],
          };
          break;

        default:
          throw new Error("Unknown analysis type");
      }

      onResults(results);
    } catch (err) {
      setError("Analysis failed: " + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const renderConfigSection = () => {
    switch (selectedAnalysis) {
      case "temperature":
        return (
          <div>
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Temperature Values (comma-separated)
            </label>
            <input
              type="text"
              value={temperatureValues}
              onChange={(e) => setTemperatureValues(e.target.value)}
              className="w-full px-3 py-2 apple-glass-card border border-gray-300/20 rounded-md text-gray-200 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-300/30 focus:border-gray-300/40"
              placeholder="0.1, 0.5, 0.9"
            />
            <p className="mt-1 text-xs text-gray-400">
              Values between 0.0 (deterministic) and 1.0 (creative)
            </p>
          </div>
        );

      case "model":
        return (
          <div>
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Model Names (comma-separated)
            </label>
            <input
              type="text"
              value={modelNames}
              onChange={(e) => setModelNames(e.target.value)}
              className="w-full px-3 py-2 apple-glass-card border border-gray-300/20 rounded-md text-gray-200 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-300/30 focus:border-gray-300/40"
              placeholder="gpt-3.5-turbo, gpt-4o-mini"
            />
            <p className="mt-1 text-xs text-gray-400">
              OpenAI model names (e.g., gpt-3.5-turbo, gpt-4, gpt-4o-mini)
            </p>
          </div>
        );

      case "custom":
        return (
          <div>
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Custom Modifications (JSON)
            </label>
            <textarea
              value={customModifications}
              onChange={(e) => setCustomModifications(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 apple-glass-card border border-gray-300/20 rounded-md text-gray-200 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-300/30 focus:border-gray-300/40 font-mono text-sm"
              placeholder='{"temperature": 0.8, "max_tokens": 100}'
            />
            <p className="mt-1 text-xs text-gray-400">
              JSON object with parameter modifications
            </p>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-100 mb-2">
          What If Analysis
        </h2>
        <p className="text-sm text-gray-300">
          Selected execution:{" "}
          <span className="font-medium">{execution.node_name}</span> • Run
          counterfactual experiments to see how different parameters affect the
          output
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
                apple-glass-card p-4 text-left transition-all
                ${
                  isSelected
                    ? "ring-2 ring-gray-300/30"
                    : "hover:bg-gray-300/10 hover:ring-1 hover:ring-gray-300/20"
                }
              `}
            >
              <div className="flex items-center space-x-3 mb-2">
                <Icon
                  className={`h-5 w-5 ${
                    isSelected ? "text-gray-200" : "text-gray-400"
                  }`}
                />
                <h3
                  className={`font-medium ${
                    isSelected ? "text-gray-100" : "text-gray-100"
                  }`}
                >
                  {analysis.label}
                </h3>
              </div>
              <p className="text-sm text-gray-300">{analysis.description}</p>
            </button>
          );
        })}
      </div>

      {/* Configuration Section */}
      <div className="apple-glass-card p-6">
        <h3 className="text-lg font-medium text-gray-100 mb-4">
          Configure{" "}
          {analysisTypes.find((a) => a.type === selectedAnalysis)?.label}
        </h3>

        {renderConfigSection()}

        {error && (
          <div className="mt-4 apple-glass-card border border-gray-300/20 rounded-lg p-4">
            <p className="text-sm text-gray-200">{error}</p>
          </div>
        )}

        <div className="mt-6">
          <button
            onClick={runAnalysis}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 apple-glass-card text-gray-200 rounded-2xl transition-all border border-gray-300/20 hover:bg-gray-300/10 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {loading ? "Running Analysis..." : "Run Analysis"}
          </button>
        </div>
      </div>

      {/* Execution Details */}
      <div className="apple-glass-card p-6">
        <h4 className="font-medium text-gray-100 mb-4">Execution Details</h4>

        {/* Basic Metadata */}
        <div className="grid grid-cols-2 gap-4 text-sm mb-6">
          <div>
            <span className="text-gray-300">Node:</span>
            <span className="ml-2 font-medium">{execution.node_name}</span>
          </div>
          <div>
            <span className="text-gray-300">Status:</span>
            <span className="ml-2 font-medium capitalize">
              {execution.status}
            </span>
          </div>
          <div>
            <span className="text-gray-300">Duration:</span>
            <span className="ml-2 font-medium">
              {Math.round(execution.duration_ms)}ms
            </span>
          </div>
          <div>
            <span className="text-gray-300">Timestamp:</span>
            <span className="ml-2 font-medium">
              {new Date(execution.timestamp * 1000).toLocaleString()}
            </span>
          </div>
        </div>

        {/* State Information */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h5 className="font-medium text-gray-100 mb-3">Input State</h5>
            <pre className="apple-glass-card p-3 rounded-lg overflow-x-auto text-gray-300 text-xs max-h-64 overflow-y-auto">
              {JSON.stringify(execution.input_state, null, 2)}
            </pre>
          </div>
          <div>
            <h5 className="font-medium text-gray-100 mb-3">Output State</h5>
            <pre className="apple-glass-card p-3 rounded-lg overflow-x-auto text-gray-300 text-xs max-h-64 overflow-y-auto">
              {JSON.stringify(execution.output_state, null, 2)}
            </pre>
          </div>
        </div>

        {execution.error_message && (
          <div className="mt-4">
            <h5 className="font-medium text-gray-100 mb-2">Error Details</h5>
            <div className="apple-glass-card p-3 rounded-lg border border-red-500/20">
              <p className="text-sm text-red-400">{execution.error_message}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CounterfactualPanel;
