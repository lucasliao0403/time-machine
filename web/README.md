# TimeMachine Web UI

A Next.js web interface for TimeMachine counterfactual analysis of LangGraph agents.

## Features

- **Graph Runs Browser**: View all recorded agent executions
- **Execution Timeline**: Drill down into individual node executions
- **What If Analysis**: Run counterfactual experiments with different parameters
- **Results Visualization**: Charts and graphs showing output differences
- **Real-time Stats**: Database statistics and system status

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python TimeMachine backend running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend Setup

The web UI requires the TimeMachine FastAPI backend to be running:

```bash
# From the project root
cd web
python backend.py
```

This starts the API server on [http://localhost:8000](http://localhost:8000).

## Usage

1. **Record Executions**: Use the TimeMachine Python library to record LangGraph agent runs
2. **Browse Data**: View recorded runs in the "Graph Runs" tab
3. **Select Execution**: Click on any execution to see details
4. **Run Experiments**: Use "What If?" tab to test different parameters
5. **View Results**: Analyze output differences in the "Results" tab

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **Lucide React** - Icon library
- **Axios** - HTTP client

## API Integration

The frontend communicates with the FastAPI backend via REST endpoints:

- `GET /api/graph-runs` - List all recorded runs
- `GET /api/graph-runs/{id}/executions` - Get executions for a run
- `POST /api/counterfactuals/temperature` - Temperature sensitivity analysis
- `POST /api/counterfactuals/models` - Model comparison analysis
- `POST /api/counterfactuals/custom` - Custom parameter modifications

## Development

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```
