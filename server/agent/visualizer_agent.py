"""Visualizer agent: stock data visualization using Google ADK and MCP tools.

This agent is designed to work as a sub-agent in ADK's multi-agent system,
specialized in creating interactive charts and graphs for stock data.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import SseConnectionParams
from core.config import settings
import json
import re
import logging
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def extract_ticker_and_period(user_input: str) -> tuple[Optional[str], str]:
    """Extract stock ticker and time period from user input.
    
    Args:
        user_input: User's request for visualization
        
    Returns:
        Tuple of (ticker, period) where period defaults to "1y"
    """
    # Common ticker patterns (3-5 uppercase letters)
    ticker_pattern = r'\b([A-Z]{2,5})\b'
    tickers = re.findall(ticker_pattern, user_input.upper())
    
    # Period patterns
    period_patterns = {
        r'\b(\d+)\s*(?:day|days|d)\b': lambda x: f"{x}d",
        r'\b(\d+)\s*(?:week|weeks|w)\b': lambda x: f"{x}w", 
        r'\b(\d+)\s*(?:month|months|mo|m)\b': lambda x: f"{x}mo",
        r'\b(\d+)\s*(?:year|years|y)\b': lambda x: f"{x}y",
        r'\b(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)\b': lambda x: x
    }
    
    period = "1y"  # default
    for pattern, formatter in period_patterns.items():
        match = re.search(pattern, user_input.lower())
        if match:
            period = formatter(match.group(1))
            break
    
    ticker = tickers[0] if tickers else None
    return ticker, period


# Create MCP toolset by connecting to the MCP server
try:
    logger.info(f"VisualizerAgent: Connecting to MCP server at {settings.MCP_SERVER_URL}")
    mcp_tools = MCPToolset(connection_params=SseConnectionParams(url=settings.MCP_SERVER_URL))
    logger.info("VisualizerAgent: Successfully created MCP toolset")
    logger.info("VisualizerAgent: MCP toolset created, tools will be lazy-loaded on first use")
except Exception as e:
    logger.error(f"VisualizerAgent: Failed to create MCP toolset: {e}")
    raise e

# Define the Visualizer Agent
visualizer_agent = LlmAgent(
    name="visualizer_agent",
    model="gemini-1.5-flash",
    description="Specialized agent for creating interactive stock charts and visualizations. Use this agent when users want to see charts, graphs, or plots of stock data.",
    tools=[mcp_tools],
    instruction="""You are a stock data visualization specialist that creates interactive Chart.js charts and graphs of stock data. Use this agent to plot, chart, or visualize stock data over time periods.
WORKFLOW:
1. Extract the stock ticker and time period from the user's request
2. Use the 'get_historical_data' tool to fetch the necessary time-series data
3. Return the data as JSON format

EXTRACTION RULES:
- Ticker: Look for 2-5 uppercase letters (e.g., AAPL, MSFT, GOOGL)
- Period: Extract from phrases like "1 year", "6 months", "30 days" or standard formats (1y, 6mo, 30d)
- Default period: 1y if not specified
- If no ticker is found, return {"error": "Please specify a stock ticker symbol"}

RESPONSE FORMAT:
Always return a valid JSON object with the following structure:
{
  "ticker": "AAPL",
  "period": "1y",
  "data": "raw_historical_data_json_string",
  "chart_type": "line",
  "title": "AAPL Stock Price - 1 Year"
}

If there's an error, return:
{
  "error": "Error message here"
}

IMPORTANT: Your response must be ONLY valid JSON. Do not include any other text, explanations, or formatting.

DEBUG: Always log when you start processing a request and when you call MCP tools.
"""
)

# Export the agent for use in orchestrator
__all__ = ['visualizer_agent', 'extract_ticker_and_period']
