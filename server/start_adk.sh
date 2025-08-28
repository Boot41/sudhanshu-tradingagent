#!/bin/bash
# Script to start ADK web server on port 8001 to avoid conflicts with FastAPI

export ADK_WEB_PORT=8001
echo "Starting ADK web server on port $ADK_WEB_PORT"
echo "FastAPI can run simultaneously on port 8000"
echo "----------------------------------------"

adk web screener_agent
