#!/usr/bin/env python3
"""
Simple wrapper script to run the Cambrian Trading Agent
"""

import sys
import subprocess

# Run the main agent script with all arguments passed through
subprocess.run([sys.executable, "cambrian_agent.py"] + sys.argv[1:])