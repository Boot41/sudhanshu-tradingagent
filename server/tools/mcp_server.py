"""
MCP Server for Trading Agent Tools.

This module sets up an MCP (Model Context Protocol) server that registers
stock data service functions as tools for AI agents to use.
"""

from fastapi_mcp import MCPServer
from ..service import stock_data_service

# Initialize the MCP Server
mcp_server = MCPServer()

# Register the public, data-fetching functions from stock data service as tools.
# The server inspects these functions, including their docstrings and type hints,
# to create a manifest that agents can use to understand what tools are available.
mcp_server.register_tools(
    tools=[
        stock_data_service.get_historical_data,
        stock_data_service.get_technical_indicators,
    ]
)
