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

### 🎯 First Time Setup

When you run the agent for the first time, it will automatically launch an **interactive setup wizard** to help you configure:

- **Trading Objectives**: What you want the agent to focus on (profit maximization, arbitrage, research, etc.)
- **Risk Profile**: Your risk tolerance and position limits
- **Data Sources**: Which tokens and DEXs to monitor
- **Agent Behavior**: How often to run cycles and whether to auto-purchase data

### 🔄 Reset and Reconfigure

To reset your configuration and start fresh:

```bash
python cambrian_agent.py --reset
```

This will:
- Backup your existing data
- Clear all findings and state
- Run the setup wizard again

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
- Run the setup wizard on first launch
- Make real purchases based on your configured interval
- Analyze price trends
- Generate trading insights
- Save all findings to `knowledge/research/findings/`

### Model Training
Train ML models using MCP data:
```bash
python train_model.py
```

Options:
1. Train new model - Collects data via MCP and trains a price predictor
2. Make prediction - Uses existing model to predict next price
3. Run scheduler - Automatically retrains models on schedule

### Python Scripts
Use the MCP client in your own scripts:
```python
from src.mcp_client import PythonMCPClient

async def example():
    client = PythonMCPClient()
    price = await client.get_solana_price()
    print(f"Current SOL price: ${price}")
```

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