# Cambrian Trading Agent - Monetized MCP Example

An autonomous trading research agent that makes REAL purchases from the Cambrian API using the monetized MCP (Model Context Protocol) server. This agent analyzes Solana market conditions and develops trading strategies using real blockchain data.

## 🎯 What This Is

This is a **production-ready example** of how to:
- Use Claude's MCP (Model Context Protocol) with monetized APIs
- Integrate with the Cambrian API for Solana market data
- Create persistent, self-improving AI systems

**Key Point**: This uses the `claude-code-sdk` Python package, NOT Claude Desktop app.

## 📚 Documentation

- **[Installation Guide](docs/SETUP.md)** - Complete setup instructions
- **[MCP Reference](docs/MCP_REFERENCE.md)** - Understanding MCP and Fluora
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history

## 🚀 Features

- **Real Blockchain Data**: Makes actual purchases from Cambrian API (0.001 USDC per call)
- **Autonomous Research**: Runs continuously, building knowledge over time
- **Persistent State**: Saves all findings and resumes from where it left off
- **Trading Insights**: Analyzes price trends and generates actionable trading strategies
- **MCP Integration**: Uses Claude's MCP protocol for secure API access

## 💡 What You'll Build

Running this agent will:
1. Connect to the Cambrian API via Fluora MCP
2. Purchase real-time Solana price data (0.001 USDC per call)
3. Analyze market trends over multiple cycles
4. Generate trading insights and opportunities
5. Save findings for continuous learning

## 💰 Cost Warning

**IMPORTANT**: This agent makes REAL purchases that cost money!
- Each API call costs 0.001 USDC on Base Sepolia testnet
- Transactions are real and visible on the blockchain
- Monitor at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3

## 📁 Project Structure

```
.
├── cambrian_agent.py         # Main autonomous agent
├── simple_mcp_example.py     # Simple example for getting started
├── config/
│   ├── agent_config.yaml     # Agent configuration
│   └── mcp_config.json       # MCP server configuration
├── knowledge/                # Persistent knowledge base
│   ├── goals/                # Research goals
│   ├── research/
│   │   └── findings/         # JSON analysis results
│   ├── strategies/           # Trading strategies
│   ├── metrics/              # Performance metrics
│   └── state.json            # Agent state
├── src/                      # Core modules
│   ├── agent/                # Agent logic
│   │   ├── core.py           # Main agent class
│   │   └── goals.py          # Goal management
│   ├── persistence/          # State management
│   └── data/                 # Data utilities
├── docs/
│   ├── SETUP.md              # Installation guide
│   ├── MCP_REFERENCE.md      # MCP documentation
│   └── CONTRIBUTING.md       # Contribution guidelines
├── LICENSE                   # GPL-3.0
├── README.md                 # This file
├── CHANGELOG.md              # Version history
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── .gitignore                # Git exclusions
```

## 🚀 Quick Start

For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md).

```bash
# 1. Clone the repository
git clone https://github.com/your-username/monetized-mcp-agent-example.git
cd monetized-mcp-agent-example

# 2. Install dependencies
pip install -r requirements.txt
npm install -g fluora-mcp

# 3. Set up wallet and API key (see SETUP.md for details)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 4. Run the agent
python cambrian_agent.py
```

## 📝 Important Notes

### Claude Desktop vs claude-code-sdk

This project uses **claude-code-sdk** (Python SDK), NOT Claude Desktop:

- **Claude Desktop**: GUI app with `claude_desktop_config.json`
- **This project**: Python SDK with `config/mcp_config.json`

The MCP configuration format is the same, but the location differs:
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)
- This project: `config/mcp_config.json` in the project directory

### Wallet Configuration

Your wallet private key goes in `~/.fluora/wallets.json` (same for both Claude Desktop and SDK):

```json
{
  "USDC_BASE_SEPOLIA": {
    "privateKey": "your-private-key-here"
  }
}
```

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

## 📋 Requirements

- Python 3.8+
- Node.js 16+
- Anthropic API key
- Funded wallet (testnet or mainnet USDC)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## 🔒 Security

- **Private Keys**: Never commit wallet private keys
- **API Keys**: Keep your `.env` file private
- **Wallet Safety**: Agent can only spend what's in the wallet
- **Testnet First**: Always test on Base Sepolia before mainnet

## 📄 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

For more information, visit: https://www.gnu.org/licenses/gpl-3.0.html