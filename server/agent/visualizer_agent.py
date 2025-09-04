"""Visualizer agent: stock data visualization using direct tool calls.

This agent is designed to work as a sub-agent in ADK's multi-agent system,
specialized in creating interactive charts and graphs for stock data.
"""

from google.adk.agents import LlmAgent
import json
import re
import logging
from typing import Optional

# Directly import the function that will be used as a tool
from service.stock_data_service import get_historical_data

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

# Define the Visualizer Agent
visualizer_agent = LlmAgent(
    name="visualizer_agent",
    model="gemini-1.5-flash",
    description="Specialized agent for creating interactive stock charts and visualizations. Use this agent when users want to see charts, graphs, or plots of stock data.",
    # Provide the agent with the python function directly. ADK will automatically
    # convert it into a tool that the LLM can use.
    tools=[get_historical_data],
    instruction="""You are a stock data visualization specialist that returns JSON for rendering charts.

WORKFLOW:
1.  **Extract Ticker and Period**: Extract the stock ticker and time period from the user's request.
2.  **Call Tool**: Use the `get_historical_data` tool to fetch the necessary time-series data. The tool will return a Python dictionary.
3.  **Construct Response**: Use the dictionary from the tool's output to build the final JSON response. The `data` field in your response should contain the entire dictionary returned by the tool, serialized into a JSON string.

EXTRACTION RULES:
-   Ticker: Look for 2-5 uppercase letters (e.g., AAPL, MSFT, GOOGL).
-   Period: Extract from phrases like "1 year", "6 months", "30 days" or standard formats (1y, 6mo, 30d).
-   Default period: "1y" if not specified.
-   If no ticker is found, return `{"error": "Please specify a stock ticker symbol"}`.

RESPONSE FORMAT:
-   Always return a valid JSON object with the following structure.
-   The `data` field MUST be a JSON string containing the tool's output.

{
  "ticker": "AAPL",
  "period": "1y",
  "data": "{\"Open\":{...},\"High\":{...},\"Low\":{...},\"Close\":{...},\"Volume\":{...}}",
  "chart_type": "line",
  "title": "AAPL Stock Price - 1 Year"
}

If there's an error from the tool, return:
{
  "error": "Error message here"
}

IMPORTANT: Your response must be ONLY valid JSON. Do not include any other text, explanations, or formatting.
"""
)

# Export the agent for use in orchestrator
__all__ = ['visualizer_agent', 'extract_ticker_and_period']
