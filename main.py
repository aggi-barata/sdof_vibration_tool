#!/usr/bin/env python3
"""SDOF Vibration Analysis Tool - Entry Point."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.app import run


if __name__ == "__main__":
    run()
