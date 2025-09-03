"""Recommendation agent: stock buy/sell/hold recommendations using Google ADK and MCP tools.

This agent is designed to work as a sub-agent in ADK's multi-agent system,
specialized in providing trading recommendations based on technical analysis.
"""

from google.adk.agents import LlmAgent
#from google.adk.tools import ToolCodeInterpreter
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import SseConnectionParams
from core.config import settings
import json
import re
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def extract_ticker_from_input(user_input: str) -> Optional[str]:
    """Extract stock ticker from user input.
    
    Args:
        user_input: User's request for stock recommendation
        
    Returns:
        Stock ticker symbol or None if not found
    """
    # Common ticker patterns (2-5 uppercase letters)
    ticker_pattern = r'\b([A-Z]{2,5})\b'
    tickers = re.findall(ticker_pattern, user_input.upper())
    
    # Also look for common patterns like "should I buy AAPL" or "TSLA recommendation"
    recommendation_patterns = [
        r'(?:buy|sell|hold)\s+([A-Z]{2,5})',
        r'([A-Z]{2,5})\s+(?:recommendation|signal|analysis)',
        r'(?:recommend|suggest)\s+([A-Z]{2,5})',
        r'([A-Z]{2,5})\s+(?:stock|shares)'
    ]
    
    for pattern in recommendation_patterns:
        match = re.search(pattern, user_input.upper())
        if match:
            return match.group(1)
    
    return tickers[0] if tickers else None


# Create MCP toolset by connecting to the MCP server
# This toolset will lazy-load the available tools (get_technical_indicators, etc.)
try:
    logger.info(f"RecommendationAgent: Connecting to MCP server at {settings.MCP_SERVER_URL}")
    mcp_tools = MCPToolset(connection_params=SseConnectionParams(url=settings.MCP_SERVER_URL))
    logger.info("RecommendationAgent: Successfully created MCP toolset")
    
    # Test MCP connection by listing tools
    try:
        logger.info("RecommendationAgent: Testing MCP connection by listing tools...")
        # Note: This might not work immediately, but we'll log it
        logger.info("RecommendationAgent: MCP toolset created, tools will be lazy-loaded on first use")
    except Exception as test_e:
        logger.warning(f"RecommendationAgent: Could not test MCP connection immediately: {test_e}")
        
except Exception as e:
    logger.error(f"RecommendationAgent: Failed to create MCP toolset: {e}")
    raise e

# Define the Recommendation Agent
recommendation_agent = LlmAgent(
    name="recommendation_agent",
    model="gemini-1.5-flash",
    # The description is vital for the orchestrator to decide when to delegate to this agent
    description="Specialized agent for providing buy, sell, or hold recommendations for stocks based on technical analysis. Use this agent when users ask for trading advice or stock recommendations.",
    # Provide the agent with the MCP tools it's allowed to use
    tools=[mcp_tools],
    #enable_function_calling=True,  # Enable function call execution
    #tool_code_interpreter=ToolCodeInterpreter(),
    # The instruction prompt guides the agent's behavior
    instruction="""You are a technical analyst that returns JSON data for stock recommendations.

WORKFLOW:
1.  **Extract Ticker**: Extract the stock ticker from the user's request (e.g., "should I buy AAPL?" → extract "AAPL").
2.  **Call Tool**: Use the `get_technical_indicators` tool to fetch the analysis data for the extracted ticker.
3.  **Process Output**: The tool will return a JSON string. You must parse this JSON to access the data.
4.  **Construct Response**: Use the data from the tool's output to build the final JSON response in the specified format.

TOOL USAGE:
- The `get_technical_indicators` tool takes one argument: `ticker` (string).
- Example call: `get_technical_indicators(ticker="AAPL")`
- The tool returns a JSON object with fields like `signal`, `last_close`, `rsi`, etc.

RESPONSE FORMAT:
- After processing the tool's output, create a JSON object with the following structure:
{
  "ticker": "[ticker]",
  "signal": "[signal from tool]",
  "last_close": [last_close from tool],
  "rsi": [rsi from tool],
  "ma50": [ma50 from tool],
  "ma200": [ma200 from tool],
  "analysis": "[analysis from tool]"
}

ERROR HANDLING:
- If no ticker is found, return `{"error": "Please specify a stock ticker symbol"}`.
- If the tool returns an error, forward that error in the JSON response: `{"error": "[error from tool]"}`.

IMPORTANT: Your final response must be ONLY the valid JSON object. Do not include any other text, explanations, or formatting.
"""
)

# Export the agent for use in orchestrator
__all__ = ['recommendation_agent', 'extract_ticker_from_input']
