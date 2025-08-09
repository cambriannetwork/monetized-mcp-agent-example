# Monetized MCP Agent Example - Cambrian Trading Agent

A production-ready example demonstrating how to build autonomous AI agents that interact with monetized APIs through the MCP (Model Context Protocol) using the Fluora MCP server. This agent makes REAL purchases from the Cambrian API to access Solana DeFi data.

## 🎯 Overview

This repository provides a complete, working implementation of:
- **MCP Integration**: Using Claude's Model Context Protocol with monetized APIs
- **Real Blockchain Transactions**: Making actual USDC payments for API access
- **Autonomous Agent**: Self-directed research agent that builds knowledge over time
- **Production Ready**: Complete with error handling, state persistence, and monitoring

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Anthropic API key
- Wallet with USDC (testnet or mainnet)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/cambriannetwork/monetized-mcp-agent-example.git
cd monetized-mcp-agent-example

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Fluora MCP server
npm install -g fluora-mcp

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Configure wallet
mkdir -p ~/.fluora
cat > ~/.fluora/wallets.json << 'EOF'
{
  "USDC_BASE_SEPOLIA": {
    "privateKey": "your-private-key-here"
  }
}
EOF
```

### Test Installation

```bash
# Test that MCP tools are available
python3 test_mcp_tools.py

# Run a simple example
python3 simple_mcp_example.py
```

## 💰 Cost Warning

**IMPORTANT**: This agent makes REAL purchases that cost money!
- Each API call costs 0.001 USDC
- Transactions are real and visible on the blockchain
- Monitor at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3

## 🚀 Usage

### Simple Example
Make a single API call to get SOL price:

```bash
python3 simple_mcp_example.py
```

### Autonomous Agent
Run the full autonomous research agent:

```bash
python3 cambrian_agent.py
```

The agent will:
- Make real purchases every 15 seconds
- Analyze price trends and market conditions
- Generate trading insights
- Save findings to `knowledge/research/findings/`

### Testing MCP Setup
Verify your MCP configuration:

```bash
python3 test_mcp_tools.py
```

## 🏗️ Architecture

### MCP (Model Context Protocol)
MCP enables Claude to interact with external tools and services. This example uses:
- **Fluora MCP Server**: Bridge between Claude and monetized APIs
- **Cambrian API**: Solana DeFi data provider (monetized)
- **Claude SDK**: Python interface for programmatic Claude access

### How It Works

1. **MCP Server Connection**: The Fluora MCP server runs as a subprocess
2. **Service Discovery**: Agent uses `exploreServices` to find available APIs
3. **Authentication**: Wallet credentials enable blockchain payments
4. **Real Purchases**: Agent calls `make-purchase` to buy data access
5. **Data Processing**: Claude analyzes the purchased data
6. **Knowledge Persistence**: Findings are saved for future use

### Project Structure

```
monetized-mcp-agent-example/
├── cambrian_agent.py         # Main autonomous agent
├── simple_mcp_example.py     # Simple example for getting started
├── test_mcp_tools.py         # MCP configuration tester
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
│   │   └── state_manager.py  # State persistence
│   └── data/                 # Data utilities
├── docs/                     # Documentation
│   ├── SETUP.md              # Detailed setup guide
│   ├── MCP_REFERENCE.md      # MCP documentation
│   └── API_GUIDE.md          # Cambrian API guide
├── tests/                    # Test files
├── LICENSE                   # GPL-3.0
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── .gitignore                # Git exclusions
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional
AGENT_LOOP_INTERVAL=15  # Seconds between cycles (default: 15)
LOG_LEVEL=INFO          # Logging level (default: INFO)
```

### MCP Configuration (config/mcp_config.json)
```json
{
  "mcpServers": {
    "fluora": {
      "command": "/usr/bin/node",
      "args": [
        "--experimental-global-webcrypto",
        "/path/to/fluora-mcp"
      ],
      "env": {
        "FLUORA_API_URL": "https://2bwsfmjzdd.us-west-2.awsapprunner.com/api",
        "NODE_OPTIONS": "--experimental-global-webcrypto"
      }
    }
  }
}
```

### Wallet Configuration (~/.fluora/wallets.json)
```json
{
  "USDC_BASE_SEPOLIA": {
    "privateKey": "your-private-key-here"
  },
  "USDC_BASE_MAINNET": {
    "privateKey": "your-private-key-here"
  }
}
```

## 📚 Examples

### 1. Basic Price Query
```python
from claude_code_sdk import query, ClaudeCodeOptions

async def get_price():
    options = ClaudeCodeOptions(
        mcp_servers=mcp_config['mcpServers'],
        allowed_tools=[
            "mcp__fluora__exploreServices",
            "mcp__fluora__callServiceTool"
        ]
    )
    
    prompt = "Get the current SOL price using the Cambrian API"
    async for message in query(prompt=prompt, options=options):
        # Process response
        pass
```

### 2. Automated Trading Research
```python
agent = CambrianMCPAgent()
await agent.initialize()
await agent.execute_cycle()  # Runs one research cycle
```

### 3. Continuous Monitoring
```python
agent = CambrianMCPAgent()
await agent.run_forever()  # Runs continuously until stopped
```

## 🛠️ Development

### Running Tests
```bash
# Test MCP configuration
python3 test_mcp_tools.py

# Run all tests
python3 -m pytest tests/
```

### Adding New Features
1. Create new research methods in `cambrian_agent.py`
2. Add goal types in `src/agent/goals.py`
3. Implement data processors in `src/data/`

### Debugging
- Check MCP server logs: `fluora-mcp` runs in verbose mode
- View agent state: `cat knowledge/state.json`
- Monitor findings: `ls -la knowledge/research/findings/`

## 🔒 Security

### Best Practices
- **Never commit private keys**: Keep wallets.json secure
- **Use testnet first**: Test on Base Sepolia before mainnet
- **Monitor spending**: Track wallet balance and transactions
- **Rotate keys regularly**: Update wallet keys periodically

### Wallet Safety
- Agent can only spend what's in the configured wallet
- Each purchase requires explicit confirmation in code
- All transactions are logged and traceable

## 📊 Monitoring

### Transaction Monitoring
- Base Sepolia: https://sepolia.basescan.org/address/[YOUR_WALLET]
- Base Mainnet: https://basescan.org/address/[YOUR_WALLET]

### Agent Metrics
- Cycles completed: `knowledge/state.json`
- Research findings: `knowledge/research/findings/`
- Performance metrics: `knowledge/metrics/`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## 🙋 Support

### Common Issues

**MCP tools not available**
- Ensure fluora-mcp is installed: `npm list -g fluora-mcp`
- Check MCP config paths are correct
- Verify ANTHROPIC_API_KEY is set

**Purchase failures**
- Check wallet has USDC balance
- Verify wallet.json has correct private key
- Ensure using correct network (testnet/mainnet)

**Agent not finding patterns**
- Let it run for multiple cycles to build knowledge
- Check `knowledge/research/findings/` for saved data

### Getting Help
- GitHub Issues: [Report bugs or request features](https://github.com/cambriannetwork/monetized-mcp-agent-example/issues)
- Documentation: Check `docs/` folder for detailed guides
- MCP Reference: [Claude MCP Documentation](https://docs.anthropic.com/claude/docs/mcp)

## 🔗 Resources

- [Fluora MCP](https://www.fluora.ai) - Monetized MCP marketplace
- [Cambrian API](https://www.cambrian.org) - Solana DeFi data provider
- [Claude SDK](https://github.com/anthropics/claude-sdk-python) - Python SDK for Claude
- [MCP Specification](https://modelcontextprotocol.io) - Model Context Protocol docs

## 🎯 Roadmap

- [ ] Add support for multiple data providers
- [ ] Implement advanced trading strategies
- [ ] Add backtesting capabilities
- [ ] Create web dashboard for monitoring
- [ ] Support for more blockchain networks
- [ ] Integration with trading platforms

---

Built with ❤️ by the Cambrian Network team. Making AI agents economically autonomous, one transaction at a time.