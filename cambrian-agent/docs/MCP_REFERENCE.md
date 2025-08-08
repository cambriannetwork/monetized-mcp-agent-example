# MCP (Model Context Protocol) Quick Reference

## Overview

MCP allows Claude to interact with external tools and APIs. This project uses the **monetized** version through Fluora, where each API call costs 0.001 USDC.

## Key Components

### 1. MCP Server (fluora-mcp)
- Node.js application that bridges Claude to external APIs
- Handles authentication and payment
- Installed via: `npm install -g fluora-mcp`

### 2. MCP Configuration
Location depends on your setup:

#### Claude Desktop (GUI)
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### claude-code-sdk (This Project)
```
config/mcp_config.json
```

Both use the same format:
```json
{
  "mcpServers": {
    "fluora": {
      "command": "node",
      "args": ["--experimental-global-webcrypto", "fluora-mcp"],
      "env": {
        "FLUORA_API_URL": "https://2bwsfmjzdd.us-west-2.awsapprunner.com/api"
      }
    }
  }
}
```

### 3. Wallet Configuration
Always in the same location for both:
```
~/.fluora/wallets.json
```

## Available MCP Tools

When connected to fluora, these tools become available:

### Discovery Tools
- `mcp__fluora__searchFluora` - Find available API servers
- `mcp__fluora__listServerTools` - List tools for a server

### API Interaction
- `mcp__fluora__callServerTool` - Call any tool on a connected server
  - Common tools: `pricing-listing`, `payment-methods`, `make-purchase`

## Making a Purchase

Example flow:
```python
# 1. Find the Cambrian API
mcp__fluora__searchFluora()

# 2. Get payment info
mcp__fluora__callServerTool(
    toolName="payment-methods"
)

# 3. Make purchase
mcp__fluora__callServerTool(
    toolName="make-purchase",
    args={
        "itemId": "solanapricecurrent",
        "params": {"token_address": "So11..."},
        "paymentMethod": "USDC_BASE_SEPOLIA",
        "itemPrice": 0.001
    }
)
```

## Cost Management

- Each purchase costs exactly what's specified (usually 0.001 USDC)
- Agent can only spend what's in the wallet
- Monitor spending at: https://sepolia.basescan.org/address/YOUR_WALLET

## Debugging

### Check MCP Connection
```python
# In your code
print(f"Available tools: {options.allowed_tools}")
```

### Common Issues

1. **"Tool not found"**
   - Ensure MCP server is properly configured
   - Check tool name format: `mcp__serverName__toolName`

2. **"Insufficient funds"**
   - Check wallet balance
   - Fund via faucet (testnet) or exchange (mainnet)

3. **"Connection failed"**
   - Verify fluora-mcp is installed
   - Check path in config/mcp_config.json

## Security

- Private keys in `~/.fluora/wallets.json` - NEVER commit!
- API keys in `.env` - Keep private
- Each purchase is a real blockchain transaction
- Use testnet (Base Sepolia) for development