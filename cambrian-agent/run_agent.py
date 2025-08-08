#!/usr/bin/env python3
"""
Main entry point for Cambrian Trading Agent
Redirects to the production version
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Run the production version
    script_path = Path(__file__).parent / "run_agent_production.py"
    subprocess.run([sys.executable, str(script_path)])