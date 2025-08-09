# Detailed Setup Guide

This guide will walk you through setting up the Monetized MCP Agent Example step by step.

## Prerequisites

You'll need:
- Python 3.8 or higher
- Node.js 16 or higher
- An Anthropic API key
- A funded wallet for MCP purchases

## Step 1: Install Node.js

### macOS
```bash
# Using Homebrew
brew install node

# Or download from https://nodejs.org/
```

### Windows
Download and install from [nodejs.org](https://nodejs.org/)

### Verify installation
```bash
node --version  # Should show v16.0.0 or higher
npm --version   # Should show 8.0.0 or higher
```

## Step 2: Set Up Fluora MCP Server

### Install Fluora globally
```bash
npm install -g fluora-mcp
```

### Create Fluora configuration directory
```bash
# macOS/Linux
mkdir -p ~/.fluora

# Windows
mkdir %USERPROFILE%\.fluora
```

## Step 3: Create Your Wallet

### Install eth-account
```bash
pip install eth-account
```

### Generate a new wallet
Create a file `create_wallet.py`:

```python
from eth_account import Account

acct = Account.create()
print("Address:", acct.address)
print("Private Key:", acct.key.hex())
print("\nSAVE YOUR PRIVATE KEY SECURELY!")
```

Run it:
```bash
python create_wallet.py
```

### Configure wallet in Fluora
Create `~/.fluora/wallets.json`:

```json
{
  "USDC_BASE_SEPOLIA": {
    "privateKey": "YOUR_PRIVATE_KEY_HERE"
  },
  "USDC_BASE_MAINNET": {
    "privateKey": ""
  }
}
```

**⚠️ IMPORTANT**: Replace `YOUR_PRIVATE_KEY_HERE` with your actual private key. Never share this file!

## Step 4: Fund Your Wallet

### For Testing (Base Sepolia)
1. Go to [Circle's USDC Faucet](https://faucet.circle.com/)
2. Enter your wallet address
3. Select "Base Sepolia" network
4. Request USDC (may take a few minutes)

### For Production (Base Mainnet)
1. Buy USDC on an exchange (e.g., Coinbase)
2. Send USDC to your wallet address
3. **Important**: Select "Base" network when transferring

## Step 5: Set Up the Agent

### Clone the repository
```bash
git clone https://github.com/your-username/cambrian-agent.git
cd cambrian-agent
```

### Install Python dependencies
```bash
pip install -r requirements.txt
```

### Configure environment
```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

## Step 6: Update MCP Configuration

The `config/mcp_config.json` needs to point to your fluora installation.

### Find fluora-mcp location
```bash
which fluora-mcp
```

### Update config/mcp_config.json
```json
{
  "mcpServers": {
    "fluora": {
      "command": "node",
      "args": [
        "--experimental-global-webcrypto",
        "/path/to/fluora-mcp"  // Update this path
      ],
      "env": {
        "FLUORA_API_URL": "https://2bwsfmjzdd.us-west-2.awsapprunner.com/api",
        "NODE_OPTIONS": "--experimental-global-webcrypto",
        "FLUORA_MCP_SERVER_URL": "http://localhost:80"
      }
    }
  }
}
```

## Step 7: Run the Agent

### Test with simple example first
```bash
python simple_mcp_example.py
```

This will make one purchase and show you the SOL price.

### Run the full autonomous agent
```bash
python cambrian_agent.py
```

The agent will:
- Make a real purchase every 15 seconds
- Analyze price trends
- Save findings to `knowledge/research/findings/`

## Monitoring

### Check your transactions
Base Sepolia: https://sepolia.basescan.org/address/YOUR_WALLET_ADDRESS

### View agent logs
```bash
tail -f knowledge/research/findings/*.json
```

## Troubleshooting

### "No API key found"
Make sure your `.env` file contains:
```
ANTHROPIC_API_KEY=your-key-here
```

### "Cannot find fluora-mcp"
Ensure fluora is installed globally:
```bash
npm install -g fluora-mcp
```

### "Insufficient funds"
Check your wallet balance and fund it using the faucet (testnet) or exchange (mainnet).

### "MCP connection failed"
Verify your `config/mcp_config.json` has the correct path to fluora-mcp.

## Security Notes

1. **Never commit your private key** - The `wallets.json` file should never be shared
2. **Keep your .env file private** - It contains your API keys
3. **Monitor your wallet** - The agent can only spend what's in the wallet
4. **Use testnet first** - Always test with Base Sepolia before using mainnet

## Next Steps

- Read the [README](README.md) for usage details
- Check [simple_mcp_example.py](simple_mcp_example.py) to understand the basics
- Customize the agent logic in [cambrian_agent.py](cambrian_agent.py)

Happy trading! 🚀