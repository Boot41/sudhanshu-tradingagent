#!/usr/bin/env python3
"""
Script to run ADK web server with custom port configuration.
This avoids port conflicts with FastAPI server running on port 8000.

Usage:
    python run_adk_web.py
"""

import os
import subprocess
import sys
from core.config import settings

def main():
    """Run ADK web server with configured port."""
    # Set the ADK_WEB_PORT environment variable
    os.environ['ADK_WEB_PORT'] = str(settings.ADK_WEB_PORT)
    
    print(f"Starting ADK web server on port {settings.ADK_WEB_PORT}")
    print("This avoids conflicts with FastAPI server on port 8000")
    print("-" * 50)
    
    # Run the adk web command
    try:
        subprocess.run(['adk', 'web', 'screener_agent'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running ADK web server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down ADK web server...")
        sys.exit(0)

if __name__ == "__main__":
    main()
