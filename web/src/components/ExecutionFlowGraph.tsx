import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, Clock, Zap } from 'lucide-react';
import { NodeExecution } from '@/types';

interface ExecutionFlowGraphProps {
  executions: NodeExecution[];
}

interface GraphNode {
  id: string;
  name: string;
  x: number;
  y: number;
  status: 'success' | 'error' | 'running';
  duration: number;
  execution: NodeExecution;
}

interface GraphEdge {
  from: string;
  to: string;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
}

const ExecutionFlowGraph: React.FC<ExecutionFlowGraphProps> = ({ executions }) => {
  const { nodes, edges } = useMemo(() => {
    if (!executions.length) return { nodes: [], edges: [] };

    // Sort executions by timestamp to get execution order
    const sortedExecutions = [...executions].sort((a, b) => a.timestamp - b.timestamp);
    
    // Create nodes with positions
    const graphNodes: GraphNode[] = sortedExecutions.map((execution, index) => {
      // Arrange nodes in a flowing layout
      const columns = Math.ceil(Math.sqrt(sortedExecutions.length));
      const row = Math.floor(index / columns);
      const col = index % columns;
      
      return {
        id: execution.id,
        name: execution.node_name,
        x: col * 200 + 100,
        y: row * 120 + 60,
        status: execution.status,
        duration: execution.duration_ms,
        execution
      };
    });

    // Create edges based on execution order and data flow
    const graphEdges: GraphEdge[] = [];
    for (let i = 0; i < graphNodes.length - 1; i++) {
      const fromNode = graphNodes[i];
      const toNode = graphNodes[i + 1];
      
      graphEdges.push({
        from: fromNode.id,
        to: toNode.id,
        fromX: fromNode.x,
        fromY: fromNode.y,
        toX: toNode.x,
        toY: toNode.y
      });
    }

    return { nodes: graphNodes, edges: graphEdges };
  }, [executions]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      case 'running':
        return <Clock className="h-4 w-4 text-blue-400" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'ring-green-400/40 bg-green-400/10';
      case 'error':
        return 'ring-red-400/40 bg-red-400/10';
      case 'running':
        return 'ring-blue-400/40 bg-blue-400/10';
      default:
        return 'ring-gray-400/40 bg-gray-400/10';
    }
  };

  if (!executions.length) {
    return (
      <div className="apple-glass-card p-12 text-center">
        <Zap className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-200 mb-2">No Execution Flow</h3>
        <p className="text-gray-400">Select a graph run to see its execution flow</p>
      </div>
    );
  }

  // Calculate SVG dimensions
  const maxX = Math.max(...nodes.map(n => n.x)) + 100;
  const maxY = Math.max(...nodes.map(n => n.y)) + 60;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-100 mb-1">Execution Flow</h2>
        <p className="text-gray-300 font-medium">Visual representation of node execution sequence</p>
      </div>

      <div className="apple-glass-card p-6 overflow-auto">
        <svg
          width={Math.max(800, maxX)}
          height={Math.max(400, maxY)}
          viewBox={`0 0 ${Math.max(800, maxX)} ${Math.max(400, maxY)}`}
          className="w-full h-auto"
        >
          {/* Edges */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                className="fill-gray-400"
              />
            </marker>
          </defs>

          {edges.map((edge, index) => (
            <motion.line
              key={`${edge.from}-${edge.to}`}
              x1={edge.fromX + 40}
              y1={edge.fromY}
              x2={edge.toX - 40}
              y2={edge.toY}
              stroke="rgba(156, 163, 175, 0.4)"
              strokeWidth="2"
              markerEnd="url(#arrowhead)"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: index * 0.2, duration: 0.5 }}
            />
          ))}

          {/* Nodes */}
          {nodes.map((node, index) => (
            <motion.g
              key={node.id}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: index * 0.1, type: "spring", stiffness: 200 }}
            >
              {/* Node background circle */}
              <circle
                cx={node.x}
                cy={node.y}
                r="35"
                className={`${getStatusColor(node.status)} ring-2 transition-all duration-300`}
              />
              
              {/* Node label */}
              <text
                x={node.x}
                y={node.y - 50}
                textAnchor="middle"
                className="fill-gray-200 text-sm font-medium"
              >
                {node.name}
              </text>
              
              {/* Duration label */}
              <text
                x={node.x}
                y={node.y + 55}
                textAnchor="middle"
                className="fill-gray-400 text-xs"
              >
                {node.duration}ms
              </text>
            </motion.g>
          ))}
        </svg>
      </div>

      {/* Legend */}
      <div className="apple-glass-card p-4">
        <h3 className="text-lg font-medium text-gray-200 mb-3">Legend</h3>
        <div className="flex flex-wrap gap-6">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-400" />
            <span className="text-sm text-gray-300">Success</span>
          </div>
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <span className="text-sm text-gray-300">Error</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-blue-400" />
            <span className="text-sm text-gray-300">Running</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-0.5 bg-gray-400"></div>
            <span className="text-sm text-gray-300">Execution Flow</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutionFlowGraph;
