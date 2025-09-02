#!/bin/bash
# Script to start ADK web server on port 8001 to avoid conflicts with FastAPI

echo "Starting ADK web server on port 8001"
echo "FastAPI can run simultaneously on port 8000"
echo "----------------------------------------"

# Activate the virtual environment before running the server
source .venv/bin/activate

# Set port via environment variable and start ADK with agent directory
export PORT=8001
# Create a directory for ADK data if it doesn't exist
mkdir -p .adk_data

# Start ADK with a specified data directory for traces
adk web agent --port 8001 --adk-dir .adk_data
