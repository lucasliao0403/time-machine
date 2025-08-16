import React from 'react';
import ExecutionFlowVisualization from './ExecutionFlowVisualization';
import { FlowNode, FlowEdge } from '@/types/visualization';

interface AggregateFlowVisualizationProps {
  onNodeSelect?: (node: FlowNode) => void;
  onEdgeSelect?: (edge: FlowEdge) => void;
}

/**
 * Aggregate Flow Visualization Component
 * Shows execution flow patterns across ALL graph runs
 * Displays branching frequencies and path analysis
 */
const AggregateFlowVisualization: React.FC<AggregateFlowVisualizationProps> = ({
  onNodeSelect,
  onEdgeSelect
}) => {
  return (
    <div className="space-y-6">
      <div className="apple-glass-card p-6">
        <h3 className="text-lg font-medium text-gray-100 mb-4">
          Aggregate Flow Analysis
        </h3>
        <p className="text-gray-300 mb-6">
          This view combines execution patterns from all recorded graph runs to show:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/40"></div>
              <span className="text-gray-300">Frequently used paths (thick edges)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-blue-500/20 border border-blue-500/40"></div>
              <span className="text-gray-300">Conditional branching points</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-gray-500/20 border border-gray-500/40"></div>
              <span className="text-gray-300">Node execution frequency (size)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/40"></div>
              <span className="text-gray-300">Rare/error paths (thin edges)</span>
            </div>
          </div>
        </div>
      </div>

      <ExecutionFlowVisualization 
        onNodeSelect={onNodeSelect}
        onEdgeSelect={onEdgeSelect}
      />
    </div>
  );
};

export default AggregateFlowVisualization;
