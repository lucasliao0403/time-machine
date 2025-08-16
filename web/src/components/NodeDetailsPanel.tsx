import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Clock,
  CheckCircle,
  AlertCircle,
  X,
  Play,
  BarChart3,
  Settings,
  ChevronRight,
} from "lucide-react";
import { FlowNode } from "@/types/visualization";
import { NodeExecution, CounterfactualAnalysis } from "@/types";
import CounterfactualPanel from "./CounterfactualPanel";
import ResultsVisualization from "./ResultsVisualization";

interface NodeDetailsPanelProps {
  selectedNode: FlowNode | null;
  executions: NodeExecution[];
  selectedExecution: NodeExecution | null;
  testResults: CounterfactualAnalysis | null;
  onExecutionSelect: (execution: NodeExecution) => void;
  onTestResults: (results: CounterfactualAnalysis) => void;
  onClearSelection: () => void;
}

type TabId = "info" | "llm-calls" | "testing" | "results";

interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<any>;
  disabled?: boolean;
}

const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({
  selectedNode,
  executions,
  selectedExecution,
  testResults,
  onExecutionSelect,
  onTestResults,
  onClearSelection,
}) => {
  const [activeTab, setActiveTab] = useState<TabId>("info");

  if (!selectedNode) return null;

  const formatDuration = (durationMs: number): string => {
    if (durationMs < 1000) {
      return `${Math.round(durationMs)}ms`;
    }
    return `${(durationMs / 1000).toFixed(1)}s`;
  };

  const formatTimestamp = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  const getStatusIcon = (status: NodeExecution["status"]) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const tabs: Tab[] = [
    { id: "info", label: "Basic Info", icon: BarChart3 },
    {
      id: "llm-calls",
      label: "LLM Calls",
      icon: Play,
      disabled: !selectedExecution,
    },
    {
      id: "testing",
      label: "Testing",
      icon: Settings,
      disabled: !selectedExecution,
    },
    {
      id: "results",
      label: "Results",
      icon: CheckCircle,
      disabled: !testResults,
    },
  ];

  // Calculate node statistics
  const successCount = executions.filter((e) => e.status === "success").length;
  const errorCount = executions.filter((e) => e.status === "error").length;
  const successRate =
    executions.length > 0 ? (successCount / executions.length) * 100 : 0;
  const avgDuration =
    executions.length > 0
      ? executions.reduce((sum, e) => sum + e.duration_ms, 0) /
        executions.length
      : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="apple-glass-card p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-100">
            {selectedNode.name}
          </h2>
          <p className="text-gray-300 font-medium mt-1">
            {executions.length} execution{executions.length !== 1 ? "s" : ""} •{" "}
            {successRate.toFixed(1)}% success rate
          </p>
        </div>
        <button
          onClick={onClearSelection}
          className="p-2 rounded-lg text-gray-400 hover:text-gray-300 hover:bg-gray-300/10 transition-all"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6 border-b border-gray-300/20">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          const isDisabled = tab.disabled;

          return (
            <button
              key={tab.id}
              onClick={() => !isDisabled && setActiveTab(tab.id)}
              disabled={isDisabled}
              className={`
                relative flex items-center space-x-2 px-4 py-2 text-sm font-medium transition-all
                ${
                  isActive
                    ? "text-gray-100 border-b-2 border-gray-300"
                    : isDisabled
                    ? "text-gray-500 cursor-not-allowed"
                    : "text-gray-300 hover:text-gray-200"
                }
              `}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === "info" && (
          <div className="space-y-6">
            {/* Node Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="apple-glass-card p-4 text-center">
                <div className="text-2xl font-semibold text-gray-100">
                  {executions.length}
                </div>
                <div className="text-sm text-gray-300 font-medium">
                  Executions
                </div>
              </div>
              <div className="apple-glass-card p-4 text-center">
                <div className="text-2xl font-semibold text-green-400">
                  {successCount}
                </div>
                <div className="text-sm text-gray-300 font-medium">Success</div>
              </div>
              <div className="apple-glass-card p-4 text-center">
                <div className="text-2xl font-semibold text-red-400">
                  {errorCount}
                </div>
                <div className="text-sm text-gray-300 font-medium">Errors</div>
              </div>
              <div className="apple-glass-card p-4 text-center">
                <div className="text-2xl font-semibold text-gray-100">
                  {formatDuration(avgDuration)}
                </div>
                <div className="text-sm text-gray-300 font-medium">
                  Avg Duration
                </div>
              </div>
            </div>

            {/* Executions List */}
            <div>
              <h3 className="text-lg font-semibold text-gray-100 mb-4">
                All Executions
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {executions.map((execution, index) => (
                  <button
                    key={execution.id}
                    onClick={() => onExecutionSelect(execution)}
                    className={`
                      w-full text-left apple-glass-card px-4 py-3 transition-all hover:bg-gray-300/10
                      ${
                        selectedExecution?.id === execution.id
                          ? "ring-2 ring-gray-300/30"
                          : ""
                      }
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center justify-center w-6 h-6 bg-gray-300/10 rounded-full text-xs font-medium text-gray-300">
                          {index + 1}
                        </div>
                        {getStatusIcon(execution.status)}
                        <div>
                          <div className="text-sm text-gray-300 font-medium">
                            {formatTimestamp(execution.timestamp)}
                          </div>
                          <div className="text-xs text-gray-400">
                            {formatDuration(execution.duration_ms)}
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-gray-400" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "llm-calls" && selectedExecution && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-100 mb-4">
                Execution Details
              </h3>

              {/* Basic Metadata */}
              <div className="grid grid-cols-2 gap-4 text-sm mb-6 apple-glass-card p-4">
                <div>
                  <span className="text-gray-300">Status:</span>
                  <span className="ml-2 font-medium text-gray-100 capitalize">
                    {selectedExecution.status}
                  </span>
                </div>
                <div>
                  <span className="text-gray-300">Duration:</span>
                  <span className="ml-2 font-medium text-gray-100">
                    {formatDuration(selectedExecution.duration_ms)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-300">Timestamp:</span>
                  <span className="ml-2 font-medium text-gray-100">
                    {formatTimestamp(selectedExecution.timestamp)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-300">Node:</span>
                  <span className="ml-2 font-medium text-gray-100">
                    {selectedExecution.node_name}
                  </span>
                </div>
              </div>

              {/* State Information */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-medium text-gray-100 mb-3">
                    Input State
                  </h5>
                  <pre className="apple-glass-card p-3 rounded-lg overflow-x-auto text-gray-300 text-xs max-h-64 overflow-y-auto">
                    {JSON.stringify(selectedExecution.input_state, null, 2)}
                  </pre>
                </div>
                <div>
                  <h5 className="font-medium text-gray-100 mb-3">
                    Output State
                  </h5>
                  <pre className="apple-glass-card p-3 rounded-lg overflow-x-auto text-gray-300 text-xs max-h-64 overflow-y-auto">
                    {JSON.stringify(selectedExecution.output_state, null, 2)}
                  </pre>
                </div>
              </div>

              {selectedExecution.error_message && (
                <div className="mt-4">
                  <h5 className="font-medium text-gray-100 mb-3">
                    Error Message
                  </h5>
                  <div className="apple-glass-card border border-red-500/20 p-3 rounded-lg">
                    <pre className="text-red-400 text-sm">
                      {selectedExecution.error_message}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "testing" && selectedExecution && (
          <CounterfactualPanel
            execution={selectedExecution}
            onResults={onTestResults}
          />
        )}

        {activeTab === "results" && testResults && (
          <ResultsVisualization results={testResults} />
        )}
      </div>
    </motion.div>
  );
};

export default NodeDetailsPanel;
