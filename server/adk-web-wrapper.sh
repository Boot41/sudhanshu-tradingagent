#!/bin/bash
# ADK Web Wrapper Script
# This script ensures adk web always runs on port 8001 to avoid conflicts with FastAPI

# Default port to 8001 if not specified
DEFAULT_PORT=8001

# Check if --port is already specified in arguments
if [[ "$*" == *"--port"* ]]; then
    # Port already specified, run as-is
    exec adk web "$@"
else
    # No port specified, add default port
    exec adk web --port $DEFAULT_PORT "$@"
fi
