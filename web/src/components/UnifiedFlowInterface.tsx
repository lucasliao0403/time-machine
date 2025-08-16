import React, { useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FlowNode, FlowEdge } from "@/types/visualization";
import { NodeExecution, CounterfactualAnalysis } from "@/types";
import ExecutionFlowVisualization from "./ExecutionFlowVisualization";
import NodeDetailsPanel from "./NodeDetailsPanel";
import api from "@/lib/api";

interface UnifiedFlowInterfaceProps {
  graphRunId: string;
}

interface UnifiedFlowState {
  selectedNode: FlowNode | null;
  selectedEdge: FlowEdge | null;
  nodeExecutions: NodeExecution[];
  selectedExecution: NodeExecution | null;
  testResults: CounterfactualAnalysis | null;
  loadingExecutions: boolean;
  error: string | null;
}

const UnifiedFlowInterface: React.FC<UnifiedFlowInterfaceProps> = ({
  graphRunId,
}) => {
  const [state, setState] = useState<UnifiedFlowState>({
    selectedNode: null,
    selectedEdge: null,
    nodeExecutions: [],
    selectedExecution: null,
    testResults: null,
    loadingExecutions: false,
    error: null,
  });

  // Load executions for a selected node
  const loadNodeExecutions = useCallback(
    async (nodeId: string) => {
      setState((prev) => ({ ...prev, loadingExecutions: true, error: null }));

      try {
        // Use existing API to get all executions for the graph run, then filter by node
        const allExecutions = await api.getGraphExecutions(graphRunId);
        const nodeExecutions = allExecutions.filter(
          (exec) => exec.node_name === nodeId
        );

        setState((prev) => ({
          ...prev,
          nodeExecutions,
          selectedExecution: nodeExecutions[0] || null, // Default to first execution
          loadingExecutions: false,
        }));
      } catch (error) {
        setState((prev) => ({
          ...prev,
          error: `Failed to load executions: ${(error as Error).message}`,
          loadingExecutions: false,
        }));
      }
    },
    [graphRunId]
  );

  // Handle node selection from flow visualization
  const handleNodeSelect = useCallback(
    (node: FlowNode) => {
      setState((prev) => ({
        ...prev,
        selectedNode: node,
        selectedEdge: null,
        testResults: null, // Clear previous test results
      }));

      // Load executions for this node
      loadNodeExecutions(node.id);
    },
    [loadNodeExecutions]
  );

  // Handle edge selection from flow visualization
  const handleEdgeSelect = useCallback((edge: FlowEdge) => {
    setState((prev) => ({
      ...prev,
      selectedEdge: edge,
      selectedNode: null,
      nodeExecutions: [],
      selectedExecution: null,
      testResults: null,
    }));
  }, []);

  // Handle execution selection within node details
  const handleExecutionSelect = useCallback((execution: NodeExecution) => {
    setState((prev) => ({
      ...prev,
      selectedExecution: execution,
      testResults: null, // Clear previous test results when switching executions
    }));
  }, []);

  // Handle test results from testing interface
  const handleTestResults = useCallback((results: CounterfactualAnalysis) => {
    setState((prev) => ({
      ...prev,
      testResults: results,
    }));
  }, []);

  // Clear selection
  const clearSelection = useCallback(() => {
    setState((prev) => ({
      ...prev,
      selectedNode: null,
      selectedEdge: null,
      nodeExecutions: [],
      selectedExecution: null,
      testResults: null,
      error: null,
    }));
  }, []);

  const showNodeDetails = state.selectedNode && !state.loadingExecutions;

  return (
    <div className="space-y-6">
      {/* Flow Visualization - Always visible */}
      <div>
        <ExecutionFlowVisualization
          graphRunId={graphRunId}
          onNodeSelect={handleNodeSelect}
          onEdgeSelect={handleEdgeSelect}
        />
      </div>

      {/* Node Details Panel - Shows when node is selected */}
      <AnimatePresence mode="wait">
        {showNodeDetails && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.15 }}
          >
            <NodeDetailsPanel
              selectedNode={state.selectedNode}
              executions={state.nodeExecutions}
              selectedExecution={state.selectedExecution}
              testResults={state.testResults}
              onExecutionSelect={handleExecutionSelect}
              onTestResults={handleTestResults}
              onClearSelection={clearSelection}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading state for executions */}
      {state.selectedNode && state.loadingExecutions && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="apple-glass-card p-6 text-center"
        >
          <div className="flex items-center justify-center space-x-3">
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-gray-100"></div>
            <span className="text-gray-300 font-medium">
              Loading node executions...
            </span>
          </div>
        </motion.div>
      )}

      {/* Error state */}
      {state.error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="apple-glass-card border border-red-500/20 p-4"
        >
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="h-5 w-5 rounded-full bg-red-500/20 flex items-center justify-center">
                <span className="text-red-400 text-xs">!</span>
              </div>
            </div>
            <div>
              <p className="text-gray-100 font-medium">Error</p>
              <p className="text-gray-300 text-sm">{state.error}</p>
            </div>
            <button
              onClick={() => setState((prev) => ({ ...prev, error: null }))}
              className="ml-auto text-gray-400 hover:text-gray-300 transition-colors"
            >
              ×
            </button>
          </div>
        </motion.div>
      )}

      {/* Helper text when no node is selected */}
      {!state.selectedNode && !state.selectedEdge && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="apple-glass-card p-8 text-center"
        >
          <div className="max-w-md mx-auto">
            <div className="h-12 w-12 rounded-full bg-gray-300/10 flex items-center justify-center mx-auto mb-4">
              <svg
                className="h-6 w-6 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-100 mb-2">
              Select a Node
            </h3>
            <p className="text-gray-300 font-medium">
              Click on any node in the flow graph above to view its execution
              details and run tests.
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default UnifiedFlowInterface;
