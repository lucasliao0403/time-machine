import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Clock,
  CheckCircle,
  AlertCircle,
  X,
  Play,
  Settings,
  ChevronDown,
} from "lucide-react";
import { FlowNode } from "@/types/visualization";
import { NodeExecution, CounterfactualAnalysis } from "@/types";
import CounterfactualPanel from "./CounterfactualPanel";
import ResultsVisualization from "./ResultsVisualization";
import JsonModal from "./JsonModal";

interface NodeDetailsPanelProps {
  selectedNode: FlowNode | null;
  currentExecution: NodeExecution | null;
  testResults: CounterfactualAnalysis | null;
  onTestResults: (results: CounterfactualAnalysis) => void;
  onClearSelection: () => void;
}

type TabId = "info" | "testing" | "results";

interface Tab {
  id: TabId;
  label: string;
  icon: React.ComponentType<any>;
  disabled?: boolean;
}

const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({
  selectedNode,
  currentExecution,
  testResults,
  onTestResults,
  onClearSelection,
}) => {
  const [activeTab, setActiveTab] = useState<TabId>("info");

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
    setModalTitle("");
    setModalSubtitle("");
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  if (!selectedNode) {
    return null;
  }

  const tabs: Tab[] = [
    {
      id: "info",
      label: "Execution Details",
      icon: CheckCircle,
    },
    {
      id: "testing",
      label: "Testing",
      icon: Settings,
      disabled: !currentExecution,
    },
    {
      id: "results",
      label: "Results",
      icon: CheckCircle,
      disabled: !testResults,
    },
  ];

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
            Most recent execution details
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
                flex items-center px-4 py-2 text-sm font-medium transition-all
                ${
                  isActive
                    ? "text-gray-100 border-b-2 border-gray-300"
                    : "text-gray-400 border-b-2 border-transparent"
                }
                ${
                  isDisabled
                    ? "opacity-50 cursor-not-allowed"
                    : "hover:text-gray-200 hover:bg-gray-300/10"
                }
              `}
            >
              <Icon className="h-4 w-4 mr-2" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === "info" && (
          <div className="space-y-6">
            {currentExecution ? (
              <>
                {/* Execution Summary */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="apple-glass-card p-4 text-center">
                    <div className="text-lg font-semibold text-gray-100">
                      {currentExecution.status === "success" ? (
                        <CheckCircle className="h-6 w-6 text-green-400 mx-auto" />
                      ) : (
                        <AlertCircle className="h-6 w-6 text-red-400 mx-auto" />
                      )}
                    </div>
                    <div className="text-sm text-gray-300 font-medium">
                      Status
                    </div>
                  </div>
                  <div className="apple-glass-card p-4 text-center">
                    <div className="text-lg font-semibold text-gray-100">
                      {formatDuration(currentExecution.duration_ms)}
                    </div>
                    <div className="text-sm text-gray-300 font-medium">
                      Duration
                    </div>
                  </div>
                  <div className="apple-glass-card p-4 text-center">
                    <div className="text-lg font-semibold text-gray-100">
                      {new Date(
                        currentExecution.timestamp
                      ).toLocaleTimeString()}
                    </div>
                    <div className="text-sm text-gray-300 font-medium">
                      Time
                    </div>
                  </div>
                  <div className="apple-glass-card p-4 text-center">
                    <div className="text-lg font-semibold text-gray-100">
                      {currentExecution.llm_calls?.length || 0}
                    </div>
                    <div className="text-sm text-gray-300 font-medium">
                      LLM Calls
                    </div>
                  </div>
                </div>

                {/* Input/Output State */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="font-medium text-gray-100 mb-3">
                      Input State
                    </h5>
                    <button
                      onClick={() =>
                        openModal(
                          "Input State",
                          currentExecution.input_state,
                          `${selectedNode.name} execution`
                        )
                      }
                      className="relative group w-full apple-glass-card p-4 rounded-lg border border-gray-300/10 hover:bg-gray-300/10 transition-all text-left"
                    >
                      <pre className="max-h-32 overflow-hidden font-mono pr-8">
                        {JSON.stringify(currentExecution.input_state, null, 2)}
                      </pre>
                      <ChevronDown className="absolute top-3 right-3 h-4 w-4 text-gray-400 opacity-60 group-hover:opacity-100 transition-opacity" />
                    </button>
                  </div>
                  <div>
                    <h5 className="font-medium text-gray-100 mb-3">
                      Output State
                    </h5>
                    <button
                      onClick={() =>
                        openModal(
                          "Output State",
                          currentExecution.output_state,
                          `${selectedNode.name} execution`
                        )
                      }
                      className="relative group w-full apple-glass-card p-4 rounded-lg border border-gray-300/10 hover:bg-gray-300/10 transition-all text-left"
                    >
                      <pre className="max-h-32 overflow-hidden font-mono pr-8">
                        {JSON.stringify(currentExecution.output_state, null, 2)}
                      </pre>
                      <ChevronDown className="absolute top-3 right-3 h-4 w-4 text-gray-400 opacity-60 group-hover:opacity-100 transition-opacity" />
                    </button>
                  </div>
                </div>

                {/* Error Message */}
                {currentExecution.error_message && (
                  <div className="mt-4">
                    <h5 className="font-medium text-gray-100 mb-3">
                      Error Message
                    </h5>
                    <div className="apple-glass-card border border-red-500/20 p-4 rounded-lg">
                      <p className="text-red-400 font-medium text-sm">
                        {currentExecution.error_message}
                      </p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-300 font-medium">
                  Loading execution details...
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === "testing" && currentExecution && (
          <CounterfactualPanel
            execution={currentExecution}
            onResults={onTestResults}
          />
        )}

        {activeTab === "results" && testResults && (
          <ResultsVisualization results={testResults} />
        )}
      </div>

      {/* Modal */}
      <JsonModal
        isOpen={modalOpen}
        onClose={closeModal}
        title={modalTitle}
        content={modalContent}
        subtitle={modalSubtitle}
      />
    </motion.div>
  );
};

export default NodeDetailsPanel;
