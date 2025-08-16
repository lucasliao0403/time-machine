import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  TrendingUp,
  Target,
  AlertCircle,
  CheckCircle,
  ChevronDown,
} from "lucide-react";
import { CounterfactualAnalysis } from "@/types";
import JsonModal from "./JsonModal";

interface ResultsVisualizationProps {
  results: CounterfactualAnalysis;
}

const COLORS = [
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
];

const ResultsVisualization: React.FC<ResultsVisualizationProps> = ({
  results,
}) => {
  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState<any>(null);
  const [modalTitle, setModalTitle] = useState("");
  const [modalSubtitle, setModalSubtitle] = useState("");

  const openModal = (title: string, content: any, subtitle?: string) => {
    setModalTitle(title);
    setModalContent(content);
    setModalSubtitle(subtitle || "");
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalContent(null);
  };

  // Prepare data for charts
  const scenarioData = results.scenarios.map((scenario, index) => {
    // Handle different scenario name formats
    let scenarioName = "Unknown";
    if (scenario.scenario?.name) {
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
      difference_score: scenario.replay_result?.difference_score || 0,
      success: scenario.replay_result?.success ?? false,
      color: COLORS[index % COLORS.length],
    };
  });

  const successData = [
    {
      name: "Successful",
      value: results.scenarios.filter((s) => s.replay_result?.success).length,
    },
    {
      name: "Failed",
      value: results.scenarios.filter((s) => !s.replay_result?.success).length,
    },
  ];

  const truncateText = (text: string, maxLength: number = 100): string => {
    if (typeof text !== "string") return String(text);
    return text.length > maxLength
      ? text.substring(0, maxLength) + "..."
      : text;
  };

  const formatOutput = (output: any): string => {
    if (!output) return "No output";

    if (typeof output === "object") {
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
        <h2 className="text-lg font-semibold text-gray-100 mb-2">
          Analysis Results
        </h2>
        <p className="text-sm text-gray-300">
          Counterfactual analysis completed • {results.scenarios.length}{" "}
          scenarios tested
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="apple-glass-card border border-gray-300/10 rounded-lg p-4">
          <div className="flex items-center">
            <Target className="h-5 w-5 text-blue-500" />
            <h3 className="ml-2 text-sm font-medium text-gray-100">
              Total Scenarios
            </h3>
          </div>
          <p className="mt-2 text-2xl font-bold text-gray-100">
            {results.scenarios.length}
          </p>
        </div>

        <div className="apple-glass-card border border-gray-300/10 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <h3 className="ml-2 text-sm font-medium text-gray-100">
              Successful
            </h3>
          </div>
          <p className="mt-2 text-2xl font-bold text-green-600">
            {results.scenarios.filter((s) => s.replay_result?.success).length}
          </p>
        </div>

        <div className="apple-glass-card border border-gray-300/10 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <h3 className="ml-2 text-sm font-medium text-gray-100">Failed</h3>
          </div>
          <p className="mt-2 text-2xl font-bold text-red-600">
            {results.scenarios.filter((s) => !s.replay_result?.success).length}
          </p>
        </div>

        <div className="apple-glass-card border border-gray-300/10 rounded-lg p-4">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-purple-500" />
            <h3 className="ml-2 text-sm font-medium text-gray-100">
              Avg. Difference
            </h3>
          </div>
          <p className="mt-2 text-2xl font-bold text-purple-600">
            {(
              results.scenarios.reduce(
                (sum, s) => sum + (s.replay_result?.difference_score || 0),
                0
              ) / results.scenarios.length
            ).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Difference Scores Chart */}
        <div className="apple-glass-card border border-gray-300/10 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-100 mb-4">
            Output Difference Scores
          </h3>
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
                formatter={(value: number) => [
                  value.toFixed(3),
                  "Difference Score",
                ]}
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
        <div className="apple-glass-card border border-gray-300/10 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-100 mb-4">
            Success Rate
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={successData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value, percent }) =>
                  `${name}: ${value} (${(percent || 0).toFixed(0)}%)`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {successData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={index === 0 ? "#10b981" : "#ef4444"}
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
        <div className="apple-glass-card border border-gray-300/20 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-100 mb-2">
            Best Scenario
          </h3>
          <p className="text-gray-200">
            <span className="font-medium">
              {results.best_scenario.scenario?.name ||
                "Best performing scenario"}
            </span>
          </p>
          {results.best_scenario.scenario?.modifications && (
            <div className="mt-2 text-sm text-gray-300">
              Modifications:{" "}
              {JSON.stringify(
                results.best_scenario.scenario.modifications,
                null,
                2
              )}
            </div>
          )}
        </div>
      )}

      {/* Detailed Results */}
      <div className="apple-glass-card border border-gray-300/10 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-100 mb-4">
          Detailed Results
        </h3>
        <div className="space-y-4">
          {results.scenarios.map((scenario, index) => {
            // Get scenario name using same logic as scenarioData
            let scenarioName = "Unknown";
            if (scenario.scenario?.name) {
              scenarioName = scenario.scenario.name;
            } else if (scenario.scenario?.modifications) {
              const mods = scenario.scenario.modifications;
              if (mods.temperature)
                scenarioName = `Temperature ${mods.temperature}`;
              else if (mods.model_name)
                scenarioName = `Model ${mods.model_name}`;
              else scenarioName = `Scenario ${index + 1}`;
            } else {
              scenarioName = `Scenario ${index + 1}`;
            }

            const replayResult = scenario.replay_result || scenario;
            const isSuccess = replayResult.success;

            return (
              <div
                key={index}
                className="border border-gray-300/10 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-100">{scenarioName}</h4>
                  <div className="flex items-center space-x-2">
                    {isSuccess ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-sm text-gray-300">
                      Difference:{" "}
                      {(replayResult.difference_score || 0).toFixed(3)}
                    </span>
                  </div>
                </div>

                {isSuccess ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="text-sm font-medium text-gray-200 mb-2">
                        Original Output
                      </h5>
                      <button
                        onClick={() =>
                          openModal(
                            "Original Output",
                            replayResult.original_output,
                            `${scenarioName} - Click to view full content`
                          )
                        }
                        className="w-full text-left apple-glass-card p-3 rounded text-xs text-gray-300 font-mono overflow-x-auto hover:bg-gray-300/10 transition-all cursor-pointer border border-gray-300/10 hover:border-gray-300/30 relative group"
                      >
                        <div className="max-h-16 overflow-hidden pr-8">
                          {formatOutput(replayResult.original_output)}
                        </div>
                        <ChevronDown className="absolute top-3 right-3 h-4 w-4 text-gray-400 opacity-60 group-hover:opacity-100 transition-opacity" />
                      </button>
                    </div>
                    <div>
                      <h5 className="text-sm font-medium text-gray-200 mb-2">
                        Replayed Output
                      </h5>
                      <button
                        onClick={() =>
                          openModal(
                            "Replayed Output",
                            replayResult.replayed_output,
                            `${scenarioName} - Click to view full content`
                          )
                        }
                        className="w-full text-left apple-glass-card p-3 rounded text-xs text-gray-300 font-mono overflow-x-auto hover:bg-gray-300/10 transition-all cursor-pointer border border-gray-300/10 hover:border-gray-300/30 relative group"
                      >
                        <div className="max-h-16 overflow-hidden pr-8">
                          {formatOutput(replayResult.replayed_output)}
                        </div>
                        <ChevronDown className="absolute top-3 right-3 h-4 w-4 text-gray-400 opacity-60 group-hover:opacity-100 transition-opacity" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="apple-glass-card p-3 rounded border border-gray-300/20">
                    <p className="text-sm text-gray-200">
                      Error: {replayResult.error || "Unknown error"}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Recommendations */}
      {results.recommendations && results.recommendations.length > 0 && (
        <div className="apple-glass-card border border-gray-300/20 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-100 mb-3">
            Recommendations
          </h3>
          <ul className="space-y-2">
            {results.recommendations.map((recommendation, index) => (
              <li key={index} className="text-sm text-gray-300">
                • {recommendation}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Modal for viewing full content */}
      <JsonModal
        isOpen={modalOpen}
        onClose={closeModal}
        title={modalTitle}
        content={modalContent}
        subtitle={modalSubtitle}
      />
    </div>
  );
};

export default ResultsVisualization;
