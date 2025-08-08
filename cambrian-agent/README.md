# Cambrian Trading Agent

A production-ready autonomous agent that leverages the Cambrian API to research and develop profitable trading strategies using real Solana blockchain data.

## Architecture Overview

### Core Components

1. **Agent Core** (`src/agent/`)
   - Main agent loop and orchestration
   - Goal management and prioritization
   - Progress tracking and resumption

2. **Data Module** (`src/data/`)
   - Cambrian API client integration
   - Data fetching and caching
   - Real-time price monitoring

3. **Strategy Module** (`src/strategies/`)
   - Strategy research and development
   - Backtesting framework
   - Performance metrics calculation

4. **Persistence Layer** (`src/persistence/`)
   - Goal and progress tracking
   - Research notes and findings
   - Strategy performance history

5. **Analysis Module** (`src/analysis/`)
   - Market analysis tools
   - Pattern recognition
   - Opportunity identification

## Folder Structure

```
cambrian-agent/
├── README.md
├── requirements.txt
├── config/
│   ├── agent_config.yaml
│   └── mcp_config.json
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── goals.py
│   │   └── orchestrator.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── cambrian_client.py
│   │   └── data_manager.py
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py
│   │   ├── research.py
│   │   └── backtest.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── state_manager.py
│   │   └── file_handler.py
│   └── analysis/
│       ├── __init__.py
│       ├── market_analysis.py
│       └── metrics.py
├── knowledge/
│   ├── goals/
│   │   └── current_goals.md
│   ├── research/
│   │   └── findings/
│   ├── strategies/
│   │   ├── active/
│   │   └── archived/
│   └── metrics/
│       └── performance.md
├── logs/
└── tests/
```

## Key Features

- **Autonomous Operation**: Runs continuously, researching and developing strategies
- **Real Data Only**: Uses exclusively Cambrian API data, no mock data
- **Progress Persistence**: Can resume from where it left off
- **Goal-Driven**: Maintains and prioritizes research goals
- **Metrics-Focused**: Tracks quantifiable performance metrics
- **Production Ready**: Error handling, logging, and monitoring

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the MCP configuration to `config/mcp_config.json`
2. Update `config/agent_config.yaml` with your preferences

## Usage

```bash
python -m src.agent.core
```

The agent will:
1. Load previous state and goals
2. Analyze current market conditions
3. Research new trading opportunities
4. Develop and test strategies
5. Track performance metrics
6. Persist findings and progress