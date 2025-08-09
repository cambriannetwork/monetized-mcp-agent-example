#!/usr/bin/env python3
"""Quick status check of the agent's progress"""

import json
from pathlib import Path

# Check cycle count
state_file = Path("knowledge/state.json")
if state_file.exists():
    with open(state_file) as f:
        state = json.load(f)
        print(f"Current cycle: {state.get('cycle_count', 0)}")
        print(f"Last run: {state.get('last_run', 'Never')[:19]}")

# Check MCP cache
cache_file = Path("knowledge/mcp_cache.json")
if cache_file.exists():
    print("\n✅ MCP cache found - connections optimized")
else:
    print("\n❌ No MCP cache - first run will be slower")

# Check findings
findings_dir = Path("knowledge/research/findings")
if findings_dir.exists():
    files = list(findings_dir.glob("*.json"))
    print(f"\n📊 Findings: {len(files)} files")
    
    if files:
        # Get latest
        latest = max(files, key=lambda f: f.stat().st_mtime)
        with open(latest) as f:
            data = json.load(f)
            print(f"Latest: Cycle {data.get('cycle', '?')} - ${data.get('price', 0):.2f}")
else:
    print("\n📊 No findings yet")

print("\nTo run agent: python cambrian_agent.py")
print("To view progress: python view_analysis_progress.py")