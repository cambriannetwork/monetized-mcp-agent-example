# Monetized MCP Agent Example - Cambrian Trading Agent

This repository contains a production-ready autonomous trading agent that uses the Cambrian API through a monetized MCP (Model Context Protocol) server to research and develop trading strategies on the Solana blockchain.

## Overview

The Cambrian Trading Agent is an autonomous system that:
- Continuously researches trading opportunities using real Cambrian API data
- Maintains persistent state and can resume from where it left off
- Tracks goals and progress through a structured knowledge base
- Develops and evaluates trading strategies based on quantifiable metrics
- Uses ONLY real data from the Cambrian API - no mock data

## Architecture

```
cambrian-agent/
├── config/                 # Configuration files
│   ├── agent_config.yaml  # Agent settings
│   └── mcp_config.json    # MCP server configuration
├── src/                   # Source code
│   ├── agent/            # Core agent logic
│   ├── data/             # Data management
│   ├── strategies/       # Strategy modules
│   ├── persistence/      # State persistence
│   └── analysis/         # Analysis tools
├── knowledge/            # Agent's knowledge base
│   ├── goals/           # Current and completed goals
│   ├── research/        # Research findings
│   ├── strategies/      # Trading strategies
│   └── metrics/         # Performance metrics
└── logs/                # Agent logs
```

## Key Features

### 1. Autonomous Operation
The agent runs continuously, making decisions based on its current goals and market conditions.

### 2. Real Data Integration
Uses the monetized MCP server to access Cambrian API endpoints:
- Current token prices
- Historical price data
- Trading volumes
- Pool information
- Market trends

### 3. Goal-Driven Research
Maintains a prioritized list of research goals:
- Market analysis
- Arbitrage opportunity detection
- Momentum pattern recognition
- Liquidity dynamics

### 4. Persistent State
All progress is saved and can be resumed:
- Current goals and status
- Research findings
- Strategy performance
- Market insights

### 5. Claude Integration
Uses Claude Code SDK for intelligent analysis and decision-making.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd monetized-mcp-agent-example-claude-code
```

2. Install dependencies:
```bash
cd cambrian-agent
pip install -r requirements.txt
```

3. Verify MCP configuration:
The `config/mcp_config.json` contains the working monetized MCP configuration.

## Usage

### Running the Agent

**Production Mode (FULLY WORKING):**
```bash
cd cambrian-agent
python run_agent_production.py
```
OR
```bash
cd cambrian-agent
python run_agent.py
```

**Demo Mode (simplified for testing):**
```bash
cd cambrian-agent
python run_agent_demo.py
```

The agent will:
1. Initialize and load previous state
2. Review current goals
3. Use the Cambrian API to gather data (via monetized MCP)
4. Analyze findings and develop strategies
5. Save progress and insights

Note: The production mode uses Claude SDK which may take time to initialize. The demo mode shows the agent architecture working without the Claude SDK calls.

### Testing

Run the test script to verify functionality:
```bash
python test_agent.py
```

## Configuration

### Agent Configuration (`config/agent_config.yaml`)
- `loop_interval`: Time between agent cycles (default: 300 seconds)
- `max_concurrent_research`: Maximum parallel research tasks
- `cache_ttl`: Data cache duration
- `confidence_threshold`: Minimum confidence for strategies

### MCP Configuration (`config/mcp_config.json`)
Contains the monetized MCP server settings for accessing Cambrian API.

## How It Works

### 1. Goal Management
The agent maintains goals in `knowledge/goals/current_goals.md`:
- Primary goals (high priority)
- Secondary goals (medium/low priority)
- Completed goals with findings

### 2. Research Process
For each active goal, the agent:
1. Queries relevant Cambrian API endpoints via MCP
2. Analyzes the data using Claude
3. Documents findings in markdown files
4. Updates goal progress

### 3. Data Access
The agent accesses Cambrian data through the monetized MCP:
```python
# Example MCP request structure
{
  "itemId": "solanapricecurrent",
  "params": {
    "token_address": "So11111111111111111111111111111111111111112"
  },
  "paymentMethod": "USDC_BASE_SEPOLIA",
  "itemPrice": 0.001,
  "serverWalletAddress": "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"
}
```

### 4. Strategy Development
The agent develops strategies based on:
- Price movements and patterns
- Volume analysis
- Cross-DEX arbitrage opportunities
- Market momentum indicators

## Monitoring

### Logs
Structured logs are output to console and can be redirected to files.

### Metrics
Performance metrics are tracked in `knowledge/metrics/`.

### State
Current state is saved in `knowledge/state.json`.

## Production Deployment

For production use:
1. Set appropriate environment variables
2. Configure logging to files
3. Set up monitoring/alerting
4. Ensure proper error handling
5. Configure backup of knowledge base

## Security

- API keys are stored securely in environment/config
- No sensitive data is logged
- All findings are saved locally

## Future Enhancements

Potential improvements:
- Real-time strategy execution
- Advanced backtesting framework
- Multi-agent collaboration
- Enhanced risk management
- Dashboard for monitoring

## License

[Your License Here]

## Support

For issues or questions:
- Check logs for error messages
- Review agent state and goals
- Ensure MCP server is accessible
- Verify Cambrian API connectivity