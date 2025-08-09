#!/bin/bash
# Quick setup script for Monetized MCP Agent Example

echo "========================================="
echo "Monetized MCP Agent Example Setup Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node
echo "Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION found"
else
    echo -e "${RED}✗${NC} Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Check npm
echo "Checking npm installation..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm $NPM_VERSION found"
else
    echo -e "${RED}✗${NC} npm not found. Please install npm"
    exit 1
fi

echo ""
echo "Installing dependencies..."
echo ""

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python packages installed"
else
    echo -e "${YELLOW}⚠${NC} Some Python packages may have failed to install"
fi

# Check if fluora-mcp is installed
echo "Checking fluora-mcp installation..."
if npm list -g fluora-mcp &> /dev/null; then
    echo -e "${GREEN}✓${NC} fluora-mcp is already installed"
else
    echo "Installing fluora-mcp..."
    npm install -g fluora-mcp
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} fluora-mcp installed successfully"
    else
        echo -e "${RED}✗${NC} Failed to install fluora-mcp. Try: sudo npm install -g fluora-mcp"
        exit 1
    fi
fi

echo ""
echo "Setting up configuration..."
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file from template"
    echo -e "${YELLOW}⚠${NC} Please edit .env and add your ANTHROPIC_API_KEY"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Create fluora directory
mkdir -p ~/.fluora
echo -e "${GREEN}✓${NC} Created ~/.fluora directory"

# Check for wallets.json
if [ ! -f ~/.fluora/wallets.json ]; then
    echo -e "${YELLOW}⚠${NC} Wallet configuration not found"
    echo ""
    echo "To configure your wallet, create ~/.fluora/wallets.json with:"
    echo ""
    echo '{'
    echo '  "USDC_BASE_SEPOLIA": {'
    echo '    "privateKey": "your-private-key-here"'
    echo '  }'
    echo '}'
    echo ""
else
    echo -e "${GREEN}✓${NC} Wallet configuration found"
fi

# Update MCP config with correct paths
echo "Updating MCP configuration..."
NODE_PATH=$(which node)
FLUORA_PATH=$(which fluora-mcp)

# Create temp file with updated config
cat > config/mcp_config.json.tmp << EOF
{
  "mcpServers": {
    "fluora": {
      "command": "$NODE_PATH",
      "args": [
        "--experimental-global-webcrypto",
        "$FLUORA_PATH"
      ],
      "env": {
        "FLUORA_API_URL": "https://2bwsfmjzdd.us-west-2.awsapprunner.com/api",
        "NODE_OPTIONS": "--experimental-global-webcrypto"
      }
    }
  }
}
EOF

mv config/mcp_config.json.tmp config/mcp_config.json
echo -e "${GREEN}✓${NC} Updated MCP configuration with local paths"

echo ""
echo "========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Configure your wallet in ~/.fluora/wallets.json"
echo "3. Test the setup: python3 test_mcp_tools.py"
echo "4. Run simple example: python3 simple_mcp_example.py"
echo "5. Run the agent: python3 cambrian_agent.py"
echo ""
echo "For detailed instructions, see docs/SETUP.md"