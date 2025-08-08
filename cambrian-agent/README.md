# Cambrian Trading Agent - Monetized MCP Example

An autonomous trading research agent that makes REAL purchases from the Cambrian API using the monetized MCP (Model Context Protocol) server. This agent analyzes Solana market conditions and develops trading strategies using real blockchain data.

## 🚀 Features

- **Real Blockchain Data**: Makes actual purchases from Cambrian API (0.001 USDC per call)
- **Autonomous Research**: Runs continuously, building knowledge over time
- **Persistent State**: Saves all findings and resumes from where it left off
- **Trading Insights**: Analyzes price trends and generates actionable trading strategies
- **MCP Integration**: Uses Claude's MCP protocol for secure API access

## 💰 Cost Warning

**IMPORTANT**: This agent makes REAL purchases that cost money!
- Each API call costs 0.001 USDC on Base Sepolia testnet
- Monitor transactions at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3

## 📁 Project Structure

```
cambrian-agent/
├── cambrian_agent.py       # Main autonomous agent
├── simple_mcp_example.py   # Simple example for getting started
├── config/
│   └── mcp_config.json     # MCP server configuration
├── knowledge/              # Persistent knowledge base
│   ├── goals/              # Research goals
│   ├── research/           # Research findings
│   │   └── findings/       # JSON files with analysis
│   └── state.json          # Agent state
└── src/                    # Core modules
    ├── agent/              # Agent logic
    ├── persistence/        # State management
    └── strategies/         # Trading strategies
```

## 🛠️ Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment**:
Create a `.env` file with:
```
ANTHROPIC_API_KEY=your_api_key_here
```

3. **Configure MCP**:
The `config/mcp_config.json` is already configured for the fluora MCP server.

## 🎯 Usage

### Simple Example
To make a single purchase and get SOL price:
```bash
python simple_mcp_example.py
```

### Full Autonomous Agent
To run the continuous research agent:
```bash
python cambrian_agent.py
```

The agent will:
- Make a real purchase every 15 seconds
- Analyze price trends
- Generate trading insights
- Save all findings to `knowledge/research/findings/`

## 📊 What the Agent Does

1. **Market Analysis**: Purchases real-time SOL price data
2. **Trend Detection**: Identifies patterns across multiple cycles
3. **Strategy Development**: Suggests trading opportunities
4. **Knowledge Building**: Each cycle builds on previous findings

## 🔧 How It Works

1. **MCP Connection**: Uses fluora server to access Cambrian API
2. **Real Purchases**: Each cycle makes an actual blockchain transaction
3. **Data Analysis**: Claude analyzes the data and generates insights
4. **Persistence**: All findings are saved as JSON files

## 📈 Example Output

```json
{
  "cycle": 5,
  "timestamp": "2025-08-08T17:30:00",
  "price": 183.51,
  "change_percent": 0.5,
  "trend": "upward",
  "market_condition": "stable",
  "insights": "SOL showing consistent growth...",
  "trading_opportunity": "Consider long position..."
}
```

## ⚠️ Important Notes

- Requires ANTHROPIC_API_KEY
- Each run costs real money (USDC)
- Agent runs continuously until stopped (Ctrl+C)
- All data is from real blockchain, not simulated

## 🤝 Contributing

This is an example project demonstrating monetized MCP integration. Feel free to fork and extend!

## 📄 License

MIT License - Use at your own risk and cost!