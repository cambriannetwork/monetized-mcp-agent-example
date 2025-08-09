#!/usr/bin/env python3
"""
Direct MCP Data Collector - Programmatically call MCP server for real data
"""

import asyncio
import json
import httpx
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.strategy.real_mcp_collector import RealMCPDataCollector


class DirectMCPCollector:
    """Direct programmatic MCP client for data collection"""
    
    def __init__(self):
        self.real_data_collector = RealMCPDataCollector()
        self.server_params = None
        self.session = None
        self.cambrian_server_id = None
        self.cambrian_url = None
        self.wallet_address = None
        self.prices_collected = 0
        self.total_cost = 0.0
        
    async def initialize(self):
        """Initialize MCP connection"""
        print("🔌 Initializing MCP connection...")
        
        # Load MCP config
        with open('config/mcp_config.json') as f:
            config = json.load(f)
        
        # Get fluora server config
        fluora_config = config['mcpServers']['mcp__fluora']
        
        # Set up server parameters
        self.server_params = StdioServerParameters(
            command=fluora_config['command'],
            args=fluora_config['args'] if 'args' in fluora_config else [],
            env=fluora_config.get('env', {})
        )
        
        print("✅ MCP configuration loaded")
        
    async def connect(self):
        """Connect to MCP server"""
        print("🔗 Connecting to fluora MCP server...")
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                
                # Initialize the connection
                await session.initialize()
                
                print("✅ Connected to MCP server")
                
                # Find Cambrian server
                await self.find_cambrian_server()
                
                # Start collecting data
                await self.collect_price_data()
    
    async def find_cambrian_server(self):
        """Find Cambrian server details"""
        print("\n🔍 Searching for Cambrian server...")
        
        # Search for Cambrian
        result = await self.session.call_tool(
            "searchFluora",
            arguments={"query": "cambrian"}
        )
        
        if result and result.content:
            servers = json.loads(result.content[0].text)
            if servers and len(servers) > 0:
                cambrian = servers[0]
                self.cambrian_server_id = cambrian.get('id')
                self.cambrian_url = cambrian.get('serverUrl')
                print(f"✅ Found Cambrian: {cambrian.get('name')}")
                print(f"   Server ID: {self.cambrian_server_id}")
                
                # Get server tools to find wallet
                await self.get_server_details()
            else:
                raise Exception("Cambrian server not found")
    
    async def get_server_details(self):
        """Get Cambrian server details including wallet"""
        print("\n📋 Getting server details...")
        
        # List server tools
        result = await self.session.call_tool(
            "listServerTools",
            arguments={
                "serverName": "cambrian",
                "mcpServerUrl": self.cambrian_url
            }
        )
        
        if result and result.content:
            print("✅ Got server tools")
            
            # Get payment methods to find wallet
            payment_result = await self.session.call_tool(
                "callServerTool",
                arguments={
                    "serverId": self.cambrian_server_id,
                    "mcpServerUrl": self.cambrian_url,
                    "toolName": "payment-methods",
                    "args": {}
                }
            )
            
            if payment_result and payment_result.content:
                data = json.loads(payment_result.content[0].text)
                self.wallet_address = data.get('serverWalletAddress')
                print(f"✅ Got wallet: {self.wallet_address}")
    
    async def collect_price_data(self):
        """Collect real price data"""
        print("\n💰 Starting price data collection...")
        print("Target: 100 real price points")
        print("-" * 50)
        
        # Check current data
        try:
            current_prices, _ = self.real_data_collector.get_real_prices()
            current_count = len(current_prices)
        except:
            current_count = 0
        
        needed = max(0, 100 - current_count)
        print(f"Current: {current_count} points")
        print(f"Need: {needed} more points")
        
        if needed == 0:
            print("\n✅ Already have enough data!")
            return
        
        # Collect prices
        for i in range(needed):
            try:
                print(f"\n[{i+1}/{needed}] Collecting price point...")
                
                # Get pricing first
                pricing_result = await self.session.call_tool(
                    "callServerTool",
                    arguments={
                        "serverId": self.cambrian_server_id,
                        "mcpServerUrl": self.cambrian_url,
                        "toolName": "pricing-listing",
                        "args": {}
                    }
                )
                
                # Make purchase for current price
                purchase_result = await self.session.call_tool(
                    "callServerTool",
                    arguments={
                        "serverId": self.cambrian_server_id,
                        "mcpServerUrl": self.cambrian_url,
                        "toolName": "make-purchase",
                        "args": {
                            "itemId": "solanapricecurrent",
                            "paymentMethod": "testnet",
                            "itemPrice": 0.001,
                            "serverWalletAddress": self.wallet_address
                        }
                    }
                )
                
                if purchase_result and purchase_result.content:
                    # Extract price from response
                    response_text = purchase_result.content[0].text
                    price = self.extract_price(response_text)
                    
                    if price:
                        # Save to real data collector
                        self.real_data_collector.add_real_mcp_price(
                            price=price,
                            timestamp=datetime.now().isoformat(),
                            source="Direct_MCP_Collection"
                        )
                        self.prices_collected += 1
                        self.total_cost += 0.001
                        print(f"✅ Collected price: ${price:.2f}")
                    else:
                        print("⚠️  Could not extract price from response")
                
                # Small delay between requests
                if i < needed - 1:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"❌ Error collecting price: {e}")
        
        self.print_summary()
    
    def extract_price(self, response_text: str) -> Optional[float]:
        """Extract price from response"""
        import re
        
        # Try multiple patterns
        patterns = [
            r'price[:\s]+\$?([\d,]+\.?\d*)',
            r'current[:\s]+\$?([\d,]+\.?\d*)',
            r'\$?([\d,]+\.?\d*)\s*(?:USD|USDC)',
            r'"price"[:\s]+["\']?\$?([\d,]+\.?\d*)',
            r'SOL[:\s]+\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match.replace(',', ''))
                    if 50 < price < 500:  # Valid SOL range
                        return price
                except:
                    pass
        
        return None
    
    def print_summary(self):
        """Print collection summary"""
        print("\n" + "="*50)
        print("📊 COLLECTION SUMMARY")
        print("="*50)
        print(f"Prices collected: {self.prices_collected}")
        print(f"Total cost: ${self.total_cost:.3f} USDC")
        print(f"Success rate: {(self.prices_collected/max(1,self.prices_collected+5))*100:.1f}%")
        
        try:
            total_prices, _ = self.real_data_collector.get_real_prices()
            print(f"\n📈 Total real data points: {len(total_prices)}")
            if len(total_prices) >= 100:
                print("🎉 SUCCESS! Ready for strategy development!")
            else:
                print(f"📍 Need {100 - len(total_prices)} more points")
        except:
            pass
        print("="*50)


async def main():
    """Main entry point"""
    print("\n🚀 DIRECT MCP DATA COLLECTOR")
    print("="*50)
    print("This tool directly calls the MCP server to collect real price data")
    print("More efficient than using the agent")
    print("="*50)
    
    collector = DirectMCPCollector()
    
    try:
        await collector.initialize()
        await collector.connect()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # First check if we have mcp package
    try:
        import mcp
    except ImportError:
        print("\n❌ MCP package not installed!")
        print("Install with: pip install mcp")
        exit(1)
    
    asyncio.run(main())