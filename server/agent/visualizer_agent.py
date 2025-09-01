"""Visualizer agent: stock data visualization using Google ADK and MCP tools.

This agent is designed to work as a sub-agent in ADK's multi-agent system,
specialized in creating interactive charts and graphs for stock data.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp import MCPToolset
from google.adk.tools.mcp.client import SseServerParams
from ..core.config import settings
import json
import re
from typing import Optional, Dict, Any


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
# This toolset will lazy-load the available tools (get_historical_data, get_technical_indicators, etc.)
mcp_tools = MCPToolset(connection_params=SseServerParams(url=settings.MCP_SERVER_URL))

# Define the Visualizer Agent
root_agent = LlmAgent(
    name="visualizer_agent",
    model="gemini-1.5-flash",
    # The description is vital for the orchestrator to decide when to delegate to this agent
    description="Specialized agent for creating interactive charts and graphs of stock data. Use this agent to plot, chart, or visualize stock data over time periods.",
    # Provide the agent with the MCP tools it's allowed to use
    tools=[mcp_tools],
    # The instruction prompt guides the agent's behavior
    instruction="""You are an expert financial data visualization assistant specialized in creating beautiful, interactive stock charts.

WORKFLOW:
1. Extract the stock ticker and time period from the user's request
2. Use the 'get_historical_data' tool to fetch the necessary time-series data
3. Parse the returned JSON data carefully
4. Generate a self-contained HTML file with Chart.js to create an interactive line chart
5. Return ONLY the HTML code block without any additional text or formatting

EXTRACTION RULES:
- Ticker: Look for 2-5 uppercase letters (e.g., AAPL, MSFT, GOOGL)
- Period: Extract from phrases like "1 year", "6 months", "30 days" or standard formats (1y, 6mo, 30d)
- Default period: 1y if not specified

CHART REQUIREMENTS:
- Use Chart.js library for interactive charts
- Title should include the stock ticker and period
- X-axis: Date (properly formatted)
- Y-axis: Price ($) with proper scaling
- Line chart with smooth curves
- Responsive design
- Professional color scheme (blue/teal theme)
- Include hover tooltips with date and price
- Grid lines for better readability

HTML STRUCTURE:
- Complete HTML5 document
- Include Chart.js CDN
- Responsive viewport meta tag
- Clean, professional styling
- Chart container with proper dimensions

ERROR HANDLING:
- If ticker extraction fails, ask user to specify the stock symbol
- If data fetch fails, provide a helpful error message
- Handle empty or invalid data gracefully

IMPORTANT: Your final output must be ONLY the HTML code block. Do not add explanatory text, markdown formatting, or any other content outside the HTML.

EXAMPLE USER INPUTS:
- "Plot AAPL for the last 6 months"
- "Show me TSLA stock chart for 1 year" 
- "Visualize GOOGL over 2 years"
- "Chart MSFT performance last 30 days"
"""
)

# Export the agent for use in orchestrator
__all__ = ['root_agent', 'extract_ticker_and_period']
