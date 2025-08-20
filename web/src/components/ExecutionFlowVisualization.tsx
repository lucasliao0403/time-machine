import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import * as d3 from "d3";
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Settings,
  Play,
  AlertCircle,
  Loader2,
  GitBranch,
  Clock,
  TrendingUp,
} from "lucide-react";
import {
  GraphLayout,
  FlowNode,
  FlowEdge,
  VisualizationConfig,
} from "@/types/visualization";
import api from "@/lib/api";

interface ExecutionFlowVisualizationProps {
  graphRunId?: string; // If provided, shows single run; otherwise shows aggregate
  onNodeSelect?: (node: FlowNode) => void;
  onEdgeSelect?: (edge: FlowEdge) => void;
}

const ExecutionFlowVisualization: React.FC<ExecutionFlowVisualizationProps> = ({
  graphRunId,
  onNodeSelect,
  onEdgeSelect,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [graphData, setGraphData] = useState<GraphLayout | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<FlowEdge | null>(null);

  const [config, setConfig] = useState<VisualizationConfig>({
    layout: "force",
    showLabels: true,
    showStatistics: true,
    highlightMode: "frequency",
  });

  // D3 zoom behavior
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown>>();

  const loadData = useCallback(async () => {
    console.log("[FlowViz] Starting loadData", {
      graphRunId,
      mode: graphRunId ? "single-run" : "aggregate",
      timestamp: new Date().toISOString(),
    });

    try {
      setLoading(true);
      setError(null);

      console.log("[FlowViz] Calling API...", { graphRunId });

      const data = graphRunId
        ? await api.getFlowVisualization(graphRunId)
        : await api.getAggregateFlowVisualization();

      console.log("[FlowViz] API call successful", {
        graphRunId,
        dataReceived: !!data,
        nodeCount: data?.nodes?.length || 0,
        edgeCount: data?.edges?.length || 0,
        statisticsKeys: data?.statistics ? Object.keys(data.statistics) : [],
        boundsKeys: data?.bounds ? Object.keys(data.bounds) : [],
      });

      setGraphData(data);
    } catch (err: any) {
      console.error("[FlowViz] loadData failed", {
        graphRunId,
        error: err,
        errorMessage: err.message,
        errorStack: err.stack,
        errorResponse: err.response,
        errorConfig: err.config,
      });

      let errorMessage = "Failed to load flow visualization: ";

      if (err.response?.status === 404) {
        errorMessage += `Endpoint not found (404). Check if backend is running and endpoint exists. URL: ${
          err.config?.url || "unknown"
        }`;
      } else if (err.response?.status === 500) {
        errorMessage += `Server error (500). Backend processing failed: ${
          err.response?.data?.detail || err.message
        }`;
      } else if (
        err.code === "ECONNREFUSED" ||
        err.message.includes("Network Error")
      ) {
        errorMessage += `Cannot connect to backend server. Is it running on ${
          err.config?.baseURL || "http://localhost:8000"
        }?`;
      } else {
        errorMessage += `${err.message} (Status: ${
          err.response?.status || "unknown"
        })`;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
      console.log("[FlowViz] loadData completed", {
        graphRunId,
        loading: false,
      });
    }
  }, [graphRunId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const initializeD3Visualization = useCallback(() => {
    if (!svgRef.current || !graphData || !containerRef.current) return;

    const svg = d3.select(svgRef.current);
    const container = containerRef.current;
    const { width, height } = container.getBoundingClientRect();

    // Clear previous content
    svg.selectAll("*").remove();

    // Create main group for zooming/panning
    const g = svg.append("g").attr("class", "main-group");

    // Create zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 5])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);
    zoomRef.current = zoom;

    // Create scales
    const xScale = d3
      .scaleLinear()
      .domain([graphData.bounds.minX, graphData.bounds.maxX])
      .range([50, width - 50]);

    const yScale = d3
      .scaleLinear()
      .domain([graphData.bounds.minY, graphData.bounds.maxY])
      .range([50, height - 50]);

    // Create arrow markers for edges
    const defs = svg.append("defs");

    defs
      .append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "-0 -5 10 10")
      .attr("refX", 18)
      .attr("refY", 0)
      .attr("orient", "auto")
      .attr("markerWidth", 8)
      .attr("markerHeight", 8)
      .attr("xoverflow", "visible")
      .append("svg:path")
      .attr("d", "M 0,-5 L 10 ,0 L 0,5")
      .attr("fill", "rgba(156, 163, 175, 0.6)")
      .style("stroke", "none");

    // Draw edges first (so they appear behind nodes)
    const edges = g
      .selectAll(".edge")
      .data(graphData.edges)
      .enter()
      .append("g")
      .attr("class", "edge")
      .style("cursor", "pointer");

    // Edge lines
    edges
      .append("line")
      .attr("x1", (d) =>
        xScale(graphData.nodes.find((n) => n.id === d.source)?.position.x || 0)
      )
      .attr("y1", (d) =>
        yScale(graphData.nodes.find((n) => n.id === d.source)?.position.y || 0)
      )
      .attr("x2", (d) =>
        xScale(graphData.nodes.find((n) => n.id === d.target)?.position.x || 0)
      )
      .attr("y2", (d) =>
        yScale(graphData.nodes.find((n) => n.id === d.target)?.position.y || 0)
      )
      .attr("stroke", (d) => {
        if (config.highlightMode === "frequency") {
          const opacity = Math.max(0.4, d.frequency / 100);
          return `rgba(100, 200, 255, ${opacity})`;
        }
        return "rgba(100, 200, 255, 0.7)";
      })
      .attr("stroke-width", (d) => {
        if (config.highlightMode === "frequency") {
          return Math.max(1, d.frequency / 20);
        }
        return 2;
      })

      .on("click", (event, d) => {
        setSelectedEdge(d);
        onEdgeSelect?.(d);
      })
      .on("mouseover", function (event, d) {
        d3.select(this).attr("stroke", "rgba(100, 200, 255, 1)");
      })
      .on("mouseout", function (event, d) {
        if (selectedEdge?.id !== d.id) {
          d3.select(this).attr("stroke", "rgba(100, 200, 255, 0.7)");
        }
      });



    // Draw nodes
    const nodes = g
      .selectAll(".node")
      .data(graphData.nodes)
      .enter()
      .append("g")
      .attr("class", "node")
      .attr(
        "transform",
        (d) => `translate(${xScale(d.position.x)}, ${yScale(d.position.y)})`
      )
      .style("cursor", "pointer");

    // Node circles
    nodes
      .append("circle")
      .attr("r", (d) => {
        if (config.highlightMode === "frequency") {
          return Math.max(60, Math.min(100, d.executionCount * 8));
        }
        return 50;
      })
      .attr("fill", (d) => {
        if (d.type === "start") return "rgb(28, 167, 79)";
        if (d.type === "end") return "rgb(197, 94, 21)";
        if (d.type === "conditional") return "rgb(168, 85, 247)";
        return "rgb(14, 113, 158)";
      })
      .attr("stroke", (d) => {
        if (d.type === "start") return "rgba(34, 197, 94, 0.8)";
        if (d.type === "end") return "rgba(249, 115, 22, 0.8)";
        if (d.type === "conditional") return "rgba(168, 85, 247, 0.8)";
        return "rgba(14, 165, 233, 0.8)";
      })
      .attr("stroke-width", 2)
      .on("click", (event, d) => {
        setSelectedNode(d);
        onNodeSelect?.(d);
      })
      .on("mouseover", function (event, d) {
        d3.select(this)
          .attr("stroke-width", 3)
          .attr("filter", "drop-shadow(0 0 10px rgba(156, 163, 175, 0.5))");
      })
      .on("mouseout", function (event, d) {
        if (selectedNode?.id !== d.id) {
          d3.select(this).attr("stroke-width", 2).attr("filter", "none");
        }
      });

    // Node labels
    if (config.showLabels) {
      nodes
        .append("text")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("font-size", "14px")
        .attr("font-weight", "600")
        .attr("fill", "white")
        .text((d) =>
          d.name.length > 10 ? d.name.substring(0, 8) + "..." : d.name
        )
        .style("pointer-events", "none");


    }

    // Center the view
    const centerX = (graphData.bounds.minX + graphData.bounds.maxX) / 2;
    const centerY = (graphData.bounds.minY + graphData.bounds.maxY) / 2;
    const scale = Math.min(
      width / (graphData.bounds.maxX - graphData.bounds.minX + 200),
      height / (graphData.bounds.maxY - graphData.bounds.minY + 200)
    );

    svg.call(
      zoom.transform,
      d3.zoomIdentity
        .translate(width / 2, height / 2)
        .scale(Math.min(scale, 1))
        .translate(-xScale(centerX), -yScale(centerY))
    );
  }, [
    graphData,
    config,
    selectedNode,
    selectedEdge,
    onNodeSelect,
    onEdgeSelect,
  ]);

  useEffect(() => {
    if (graphData) {
      initializeD3Visualization();
    }
  }, [initializeD3Visualization, graphData]);

  const resetZoom = () => {
    if (zoomRef.current && svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg
        .transition()
        .duration(750)
        .call(zoomRef.current.transform, d3.zoomIdentity);
    }
  };

  const zoomIn = () => {
    if (zoomRef.current && svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.transition().duration(200).call(zoomRef.current.scaleBy, 1.5);
    }
  };

  const zoomOut = () => {
    if (zoomRef.current && svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg
        .transition()
        .duration(200)
        .call(zoomRef.current.scaleBy, 1 / 1.5);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="apple-glass-card p-8 text-center">
          <Loader2 className="h-8 w-8 animate-spin text-gray-200 mx-auto mb-3" />
          <span className="text-gray-100 font-medium">
            Loading flow visualization...
          </span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="apple-glass-card border border-gray-300/20 p-6">
        <div className="flex items-center mb-4">
          <AlertCircle className="h-6 w-6 text-gray-400" />
          <span className="ml-3 text-gray-100 font-medium">{error}</span>
        </div>
        <button
          onClick={loadData}
          className="px-4 py-2 apple-glass-card text-gray-200 rounded-2xl transition-all border border-gray-300/20 hover:bg-gray-300/10"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-100 mb-1">
            {graphRunId ? "Execution Flow" : "Aggregate Flow Analysis"}
          </h2>
          <p className="text-gray-300 font-medium">
            {graphRunId
              ? "Node execution sequence for this run"
              : `Flow patterns across ${
                  graphData?.statistics.totalRuns || 0
                } runs`}
          </p>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={zoomIn}
            className="p-2 apple-glass-card text-gray-200 rounded-xl transition-all border border-gray-300/20 hover:bg-gray-300/10"
            title="Zoom In"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={zoomOut}
            className="p-2 apple-glass-card text-gray-200 rounded-xl transition-all border border-gray-300/20 hover:bg-gray-300/10"
            title="Zoom Out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <button
            onClick={resetZoom}
            className="p-2 apple-glass-card text-gray-200 rounded-xl transition-all border border-gray-300/20 hover:bg-gray-300/10"
            title="Reset View"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Statistics Panel */}
      {config.showStatistics && graphData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="apple-glass-card p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Play className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-300">
                Total Runs
              </span>
            </div>
            <span className="text-2xl font-semibold text-gray-100">
              {graphData.statistics.totalRuns}
            </span>
          </div>

          <div className="apple-glass-card p-4">
            <div className="flex items-center space-x-2 mb-2">
              <GitBranch className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-300">
                Branching Points
              </span>
            </div>
            <span className="text-2xl font-semibold text-gray-100">
              {graphData.statistics.branchingPoints.length}
            </span>
          </div>

          <div className="apple-glass-card p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-300">
                Avg Path Length
              </span>
            </div>
            <span className="text-2xl font-semibold text-gray-100">
              {graphData.statistics.averagePathLength.toFixed(1)}
            </span>
          </div>

          <div className="apple-glass-card p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-300">
                Path Variability
              </span>
            </div>
            <span className="text-2xl font-semibold text-gray-100">
              {(graphData.statistics.pathVariability * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      )}

      {/* Main Visualization */}
      <div className="apple-glass-card p-6">
        <div
          ref={containerRef}
          className="w-full h-96 relative overflow-hidden rounded-lg border border-gray-300/10"
        >
          <svg
            ref={svgRef}
            width="100%"
            height="100%"
            style={{ background: "rgba(0, 0, 0, 0.1)" }}
          />
        </div>
      </div>
    </div>
  );
};

export default ExecutionFlowVisualization;
