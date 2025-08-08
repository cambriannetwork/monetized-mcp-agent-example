"""
Research agent that uses Claude to analyze Cambrian data
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

import anyio
from claude_code_sdk import query, ClaudeCodeOptions

import structlog

logger = structlog.get_logger()


class ResearchAgent:
    """Agent that conducts research using Claude and Cambrian API"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.research_history = []
    
    async def research_market_overview(self) -> Dict:
        """Research current market conditions"""
        logger.info("Starting market overview research")
        
        prompt = """You are a trading research agent with access to the Cambrian API via the fluora MCP server.

Your task is to analyze the current Solana token market. Please:

1. Use the fluora MCP to get current prices for major tokens:
   - SOL (So11111111111111111111111111111111111111112)
   - USDC (EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)
   - Any other trending tokens you discover

2. Analyze price movements and identify patterns

3. Save your findings to a file in knowledge/research/findings/ with timestamp

Use these MCP parameters:
- itemId: solanapricecurrent
- paymentMethod: USDC_BASE_SEPOLIA
- itemPrice: 0.001
- serverWalletAddress: 0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3

Focus on real data only. Document all findings."""

        options = ClaudeCodeOptions(
            max_turns=3,
            allowed_tools=[
                "Read", "Write", "Edit",
                "mcp__fluora__make-purchase",
                "mcp__fluora__list-purchasable-items"
            ]
        )
        
        messages = []
        findings = []
        
        async for message in query(prompt=prompt, options=options):
            messages.append(message)
            
            # Extract findings from Claude's responses
            if hasattr(message, 'content') and message.content:
                findings.append({
                    'timestamp': datetime.now().isoformat(),
                    'content': message.content,
                    'type': 'market_overview'
                })
        
        result = {
            'research_type': 'market_overview',
            'timestamp': datetime.now().isoformat(),
            'findings': findings,
            'message_count': len(messages)
        }
        
        self.research_history.append(result)
        logger.info("Market overview research completed", findings_count=len(findings))
        
        return result
    
    async def research_arbitrage_opportunities(self) -> Dict:
        """Research arbitrage opportunities across DEXs"""
        logger.info("Starting arbitrage opportunity research")
        
        prompt = """You are researching arbitrage opportunities in the Solana ecosystem.

Using the fluora MCP server and Cambrian API:

1. Compare prices across different DEXs (Orca, Raydium, Meteora)
2. Identify tokens with price discrepancies
3. Calculate potential profit margins accounting for fees
4. Document viable arbitrage opportunities

Save your findings to knowledge/research/findings/arbitrage_[timestamp].md

Use real Cambrian API data only. Include specific numbers and calculations."""

        options = ClaudeCodeOptions(
            max_turns=4,
            allowed_tools=[
                "Read", "Write", "Edit",
                "mcp__fluora__make-purchase",
                "mcp__fluora__list-purchasable-items"
            ]
        )
        
        messages = []
        opportunities = []
        
        async for message in query(prompt=prompt, options=options):
            messages.append(message)
            
            if hasattr(message, 'content') and message.content:
                # Parse for arbitrage opportunities
                if 'arbitrage' in message.content.lower() or 'profit' in message.content.lower():
                    opportunities.append({
                        'timestamp': datetime.now().isoformat(),
                        'analysis': message.content
                    })
        
        result = {
            'research_type': 'arbitrage_analysis',
            'timestamp': datetime.now().isoformat(),
            'opportunities_found': len(opportunities),
            'opportunities': opportunities,
            'message_count': len(messages)
        }
        
        self.research_history.append(result)
        logger.info("Arbitrage research completed", opportunities=len(opportunities))
        
        return result
    
    async def research_momentum_patterns(self) -> Dict:
        """Research momentum trading patterns"""
        logger.info("Starting momentum pattern research")
        
        prompt = """You are researching momentum trading patterns in Solana tokens.

Using the fluora MCP server:

1. Get historical price data for trending tokens
2. Identify tokens showing strong momentum (price and volume)
3. Analyze patterns in price movements
4. Document potential momentum trading strategies

Focus on:
- Tokens with >20% price change in 24h
- Volume surges
- Breakout patterns

Save findings to knowledge/research/findings/momentum_[timestamp].md"""

        options = ClaudeCodeOptions(
            max_turns=4,
            allowed_tools=[
                "Read", "Write", "Edit",
                "mcp__fluora__make-purchase",
                "mcp__fluora__list-purchasable-items"
            ]
        )
        
        messages = []
        patterns = []
        
        async for message in query(prompt=prompt, options=options):
            messages.append(message)
            
            if hasattr(message, 'content') and message.content:
                patterns.append({
                    'timestamp': datetime.now().isoformat(),
                    'pattern': message.content
                })
        
        result = {
            'research_type': 'momentum_patterns',
            'timestamp': datetime.now().isoformat(),
            'patterns_found': len(patterns),
            'patterns': patterns,
            'message_count': len(messages)
        }
        
        self.research_history.append(result)
        logger.info("Momentum research completed", patterns=len(patterns))
        
        return result
    
    def get_research_summary(self) -> Dict:
        """Get summary of all research conducted"""
        if not self.research_history:
            return {'total_research': 0, 'history': []}
        
        summary = {
            'total_research': len(self.research_history),
            'research_types': {},
            'latest_research': self.research_history[-1] if self.research_history else None,
            'history': []
        }
        
        for research in self.research_history:
            research_type = research['research_type']
            if research_type not in summary['research_types']:
                summary['research_types'][research_type] = 0
            summary['research_types'][research_type] += 1
            
            summary['history'].append({
                'type': research_type,
                'timestamp': research['timestamp'],
                'findings_count': len(research.get('findings', []))
            })
        
        return summary