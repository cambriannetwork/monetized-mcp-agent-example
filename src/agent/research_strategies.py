"""
Diverse Research Strategies for Intelligent Market Analysis
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


class ResearchStrategies:
    """Collection of intelligent research strategies"""
    
    @staticmethod
    def get_progressive_market_analysis_prompt(
        cycle: int,
        analysis: Dict,
        signals: List[Dict],
        mcp_cache: Optional[Dict] = None
    ) -> str:
        """Generate intelligent, progressive prompts based on current state"""
        
        base_context = f"Cycle #{cycle}: Progressive Market Analysis\n\n"
        
        # Add analysis context
        if analysis:
            base_context += "Current Market State:\n"
            base_context += f"- Price: ${analysis.get('current_price', 'unknown')}\n"
            
            if "price_change_pct" in analysis:
                base_context += f"- 1-cycle change: {analysis['price_change_pct']:.2f}%\n"
            
            if "trend" in analysis:
                base_context += f"- Trend: {analysis['trend']['direction']} ({analysis['trend']['strength']:.1f}% strength)\n"
            
            if "volatility_pct" in analysis:
                base_context += f"- Volatility: {analysis['volatility_pct']:.1f}%\n"
            
            if "ma_3" in analysis:
                base_context += f"- MA(3): ${analysis['ma_3']:.2f}\n"
            
            base_context += "\n"
        
        # Add signals context
        if signals:
            base_context += "Active Trading Signals:\n"
            for signal in signals[:3]:  # Top 3 signals
                base_context += f"- {signal['type']}: {signal['reason']}\n"
            base_context += "\n"
        
        # Progressive research based on cycle
        if cycle <= 2:
            # Early cycles: Focus on price discovery and setup
            prompt = base_context + """
Your task: Establish baseline market data and begin trend analysis.

1. Get current SOL price via MCP purchase
2. Compare to any previous data and identify initial trend
3. Note any significant price levels
4. Save comprehensive analysis including all metrics

Focus on accuracy and establishing a data foundation."""
            
        elif cycle <= 5:
            # Early-mid cycles: Deepen analysis
            prompt = base_context + f"""
Your task: Deepen market analysis with trend confirmation.

Previous findings show price at ${analysis.get('current_price', 'N/A')} with {analysis.get('trend', {}).get('direction', 'unclear')} trend.

1. Get updated SOL price
2. Calculate and analyze:
   - Price momentum (acceleration/deceleration)
   - Volume indicators (if available via additional MCP calls)
   - Key support/resistance levels
3. Identify any pattern formations
4. Generate specific trading recommendations

Be specific with entry/exit levels and risk parameters."""
            
        elif cycle <= 10:
            # Mid cycles: Strategic analysis
            prompt = base_context + f"""
Your task: Strategic market positioning and signal generation.

Market showing {analysis.get('trend', {}).get('consecutive_moves', 0)} consecutive moves.
Current volatility: {analysis.get('volatility_pct', 'unknown')}%

1. Get current price and assess trend continuation probability
2. Identify divergences or exhaustion signals
3. Calculate risk/reward for current setups
4. Explore correlation opportunities (consider multi-token analysis)
5. Generate 1-3 high-conviction trade setups with:
   - Entry price
   - Stop loss
   - Take profit targets
   - Position sizing based on volatility

Think like a professional trader."""
            
        else:
            # Advanced cycles: Adaptive research
            volatility = analysis.get('volatility_pct', 3)
            
            if volatility > 5:
                # High volatility strategy
                prompt = base_context + f"""
Your task: High volatility trading strategy (current vol: {volatility:.1f}%)

CRITICAL: Market showing extreme volatility. Adapt strategy accordingly.

1. Get price and assess volatility expansion/contraction
2. Identify volatility-based trading opportunities:
   - Range trading setups
   - Breakout preparations
   - Options strategies (if applicable)
3. Calculate dynamic position sizing based on volatility
4. Set wider stops but smaller positions
5. Look for mean reversion opportunities

Generate specific trades optimized for high volatility."""
                
            elif len(signals) > 2:
                # Multiple signals - confluence trading
                prompt = base_context + f"""
Your task: Confluence-based trading with {len(signals)} active signals.

Strong signal confluence detected. Multiple indicators aligning.

1. Verify price action confirms signals
2. Identify the highest probability setup from:
{chr(10).join(f'   - {s["type"]}: {s["action"]}' for s in signals[:3])}
3. Calculate optimal entry with all signals considered
4. Define clear invalidation levels
5. Size position based on conviction level

Execute the best opportunity with precision."""
                
            else:
                # Exploratory advanced research
                prompt = base_context + f"""
Your task: Advanced market research - Cycle {cycle}

After {cycle} cycles of analysis, explore new dimensions:

1. Get current price and update core metrics
2. Choose ONE advanced analysis:
   - Arbitrage scan across DEXs (check price differences)
   - Correlation analysis with BTC/ETH
   - Liquidity depth analysis
   - On-chain metrics correlation
3. Identify any market inefficiencies
4. Develop a unique trading angle others might miss
5. Challenge previous assumptions

Be creative but data-driven. Find the edge."""
        
        # Add MCP optimization
        if mcp_cache:
            prompt += f"""

CRITICAL: Use cached MCP details to save time:
- Server ID: {mcp_cache['server_id']}
- Server URL: {mcp_cache['server_url']}
- Wallet: {mcp_cache['wallet_address']}

Go DIRECTLY to make-purchase. Skip all discovery steps."""
        else:
            prompt += """

First time: Use mcp__fluora__searchFluora, then listServerTools, then payment-methods to get details."""
        
        # Always end with save instruction
        prompt += f"""

Save your complete analysis to:
{f'knowledge/research/findings/cycle_{cycle}_market_analysis.json'}

Include: price, analysis metrics, signals generated, trading setups, and next research suggestions."""
        
        return prompt
    
    @staticmethod
    def get_arbitrage_research_prompt(cycle: int, known_dexs: List[str] = None) -> str:
        """Generate arbitrage-focused research prompt"""
        
        dexs = known_dexs or ["Jupiter", "Raydium", "Orca"]
        
        return f"""Cycle #{cycle}: Cross-DEX Arbitrage Analysis

Your task: Identify and analyze arbitrage opportunities across Solana DEXs.

1. Query multiple DEX prices for SOL/USDC pair:
   - {', '.join(dexs)}
2. Calculate price differences and spreads
3. Factor in:
   - Transaction fees
   - Slippage estimates
   - Execution time
4. Identify profitable opportunities with:
   - Entry DEX and price
   - Exit DEX and price
   - Profit margin after costs
   - Required capital
   - Risk factors
5. Rank opportunities by profitability and feasibility

Save detailed arbitrage analysis with actionable setups."""
    
    @staticmethod
    def get_correlation_research_prompt(cycle: int, target_pairs: List[str] = None) -> str:
        """Generate correlation analysis research prompt"""
        
        pairs = target_pairs or ["SOL/USDC", "BTC/USDC", "ETH/USDC"]
        
        return f"""Cycle #{cycle}: Cross-Asset Correlation Analysis

Your task: Analyze correlations between major crypto assets.

1. Gather price data for: {', '.join(pairs)}
2. Calculate correlation coefficients
3. Identify:
   - Leading/lagging relationships
   - Divergences from normal correlation
   - Pair trading opportunities
4. Generate trading signals based on:
   - Correlation breaks
   - Mean reversion setups
   - Trend alignment across assets
5. Provide specific pair trade setups

Focus on actionable correlation-based strategies."""
    
    @staticmethod
    def get_volatility_research_prompt(cycle: int, current_vol: float = None) -> str:
        """Generate volatility-focused research prompt"""
        
        vol_context = f"Current volatility: {current_vol:.1f}%" if current_vol else "Volatility unknown"
        
        return f"""Cycle #{cycle}: Volatility Analysis and Trading

{vol_context}

Your task: Deep volatility analysis for trading opportunities.

1. Calculate detailed volatility metrics:
   - Historical volatility (multiple timeframes)
   - Volatility of volatility
   - Skew and kurtosis
2. Identify volatility patterns:
   - Expansion/contraction cycles
   - Time-of-day patterns
   - Event-driven spikes
3. Generate volatility-based trades:
   - Breakout setups (volatility expansion)
   - Range trades (volatility contraction)
   - Options strategies if applicable
4. Risk management rules:
   - Dynamic position sizing
   - Volatility-adjusted stops
   - Portfolio heat limits

Provide specific, volatility-optimized trading setups."""