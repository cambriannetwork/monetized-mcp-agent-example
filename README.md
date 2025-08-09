# MonetizedMCP Agent Template

A template and examples for building AI agents that use MonetizedMCP through Fluora to access monetized APIs.

## Overview

This repository provides:
1. **Template** (`template_example.py`) - Integration pattern for any agent framework
2. **Simple Example** (`simple_mcp_example.py`) - Basic example using Claude SDK
3. **Full Agent Example** (`examples/cambrian-claude-agent/`) - Complete autonomous agent

The key is understanding how to integrate Fluora MCP server calls into your agent's workflow, regardless of which framework you use.

**Note**: Currently FREE on Base Sepolia testnet until August 15, 2025. After that, switches to Base mainnet with 0.001 USDC per API call.

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Wallet with private key (testnet for now)

### Installation

```bash
# 1. Clone and setup
git clone https://github.com/cambriannetwork/monetized-mcp-agent-example.git
cd monetized-mcp-agent-example
./setup.sh

# 2. Configure wallet (use any test private key for Sepolia)
cat > ~/.fluora/wallets.json << 'EOF'
{
  "USDC_BASE_SEPOLIA": {
    "privateKey": "your-test-private-key"
  }
}
EOF

# 3. For Claude SDK examples, add API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# 4. Test the setup
python3 test_mcp_tools.py  # If using Claude SDK
# OR implement your own connection test
```

## Usage

### For Any Agent Framework

Start with `template_example.py` which shows the integration pattern:

```python
# Key components to integrate:
1. Start Fluora MCP server (subprocess)
2. Discover services (exploreServices)
3. Make API calls (callServiceTool)
4. Process responses in your agent
```

### For Claude SDK Users

```bash
# Test MCP connection
python3 test_mcp_tools.py

# Run simple example
python3 simple_mcp_example.py

# See full agent example
cd examples/cambrian-claude-agent/
python3 cambrian_agent.py
```

## How It Works

1. The Fluora MCP server connects your agent to monetized APIs
2. Your agent discovers available services through MonetizedMCP
3. API calls are made with automatic payment handling (free on testnet)
4. Data is processed by your agent

## Project Structure

```
monetized-mcp-agent-example/
├── template_example.py       # Integration template for any framework
├── simple_mcp_example.py     # Simple Claude SDK example
├── test_mcp_tools.py         # Test setup (Claude SDK)
├── setup.sh                  # Automated setup
├── config/
│   └── mcp_config.json      # MCP server configuration
├── examples/
│   └── cambrian-claude-agent/  # Full agent implementation
└── docs/                     # Documentation
```

## Integration Guide

### Key Components

1. **Fluora MCP Server** (`fluora-mcp` npm package)
2. **MCP Configuration** (`config/mcp_config.json`)
3. **Wallet Configuration** (`~/.fluora/wallets.json`)
4. **MCP Tool Calls**:
   - `exploreServices` - Discover available APIs
   - `getServiceDetails` - Get API details
   - `callServiceTool` - Make API calls

### Integration Pattern

```python
# 1. Start MCP server
process = subprocess.Popen(['node', 'fluora-mcp'], ...)

# 2. Discover services
services = agent.call('mcp__fluora__exploreServices', {'category': ''})

# 3. Make API calls
result = agent.call('mcp__fluora__callServiceTool', {
    'serverId': '9f2e4fe1-...',
    'toolName': 'make-purchase',
    'args': {...}
})
```

## Configuration

### MCP Configuration
The `config/mcp_config.json` file is automatically configured by the setup script.

### Wallet Configuration
Create `~/.fluora/wallets.json` with your wallet private key. For testnet, any valid private key works (transactions are free during hackathon).

## Documentation

- [Detailed Setup Guide](docs/SETUP.md)
- [MCP Reference](docs/MCP_REFERENCE.md)

## Important Notes

- **Hackathon Period**: FREE on Base Sepolia testnet until August 15, 2025
- **After August 15**: Switches to Base mainnet with real USDC payments
- **Testnet**: Currently configured for Base Sepolia (no real money)

## Disclaimer

This is a demonstration project for educational purposes only. Nothing in this repository constitutes financial advice. Trading cryptocurrencies involves substantial risk of loss. Always do your own research and never invest more than you can afford to lose.

## License

MIT License - Copyright © 2025 Cambrian Network, a Cambrian Labs Project

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/cambriannetwork/monetized-mcp-agent-example/issues)
- Documentation: Check the `docs/` folder

## Resources

- [Fluora](https://www.fluora.ai) - MonetizedMCP marketplace
- [Cambrian Monetized MCP Server](https://github.com/cambriannetwork/cambrian-monetized-mcp) - Server source code
- [MCP Server Endpoint](https://mcp.rickycambrian.org/monetized) - Public endpoint
- [Cambrian API](https://www.cambrian.org) - Solana DeFi data provider
- [Claude SDK](https://github.com/anthropics/claude-code-sdk-python) - For Claude examples
- [MCP Specification](https://modelcontextprotocol.io) - Protocol documentation