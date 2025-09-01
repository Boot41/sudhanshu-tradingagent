"""Recommendation agent: stock buy/sell/hold recommendations using Google ADK and MCP tools.

This agent is designed to work as a sub-agent in ADK's multi-agent system,
specialized in providing trading recommendations based on technical analysis.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp import MCPToolset
from google.adk.tools.mcp.client import SseServerParams
from ..core.config import settings
import json
import re
from typing import Optional


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
mcp_tools = MCPToolset(connection_params=SseServerParams(url=settings.MCP_SERVER_URL))

# Define the Recommendation Agent
root_agent = LlmAgent(
    name="recommendation_agent",
    model="gemini-1.5-flash",
    # The description is vital for the orchestrator to decide when to delegate to this agent
    description="Specialized agent for providing buy, sell, or hold recommendations for stocks based on technical analysis. Use this agent when users ask for trading advice or stock recommendations.",
    # Provide the agent with the MCP tools it's allowed to use
    tools=[mcp_tools],
    # The instruction prompt guides the agent's behavior
    instruction="""You are a professional technical analyst providing clear, actionable trading signals and recommendations.

WORKFLOW:
1. Extract the stock ticker from the user's request (e.g., "should I buy AAPL?" → extract "AAPL")
2. Use the 'get_technical_indicators' tool to fetch technical analysis data for the specified ticker
3. Parse the returned JSON data which includes signal, RSI, moving averages, and other indicators
4. Formulate a clear, human-readable response with the main recommendation and supporting analysis

EXTRACTION RULES:
- Look for stock tickers (2-5 uppercase letters) in phrases like:
  * "Should I buy AAPL?"
  * "TSLA recommendation"
  * "What's your signal on MSFT?"
  * "Hold or sell GOOGL?"
- If no ticker is found, ask the user to specify the stock symbol

RESPONSE FORMAT:
1. Start with a clear signal: "STRONG BUY signal for [TICKER]" or "HOLD signal for [TICKER]" etc.
2. Provide key supporting data:
   - Current RSI level and interpretation
   - Moving average analysis (50-day, 200-day)
   - Any other relevant technical indicators
   - Brief rationale for the recommendation
3. Include appropriate risk disclaimer

SIGNAL INTERPRETATION:
- STRONG BUY: Multiple bullish indicators align
- BUY: Generally positive technical setup
- HOLD: Mixed signals or neutral technical picture
- SELL: Generally negative technical setup  
- STRONG SELL: Multiple bearish indicators align

TECHNICAL INDICATORS GUIDANCE:
- RSI > 70: Potentially overbought (bearish)
- RSI < 30: Potentially oversold (bullish)
- RSI 30-70: Neutral zone
- Price above 50-day MA: Short-term bullish
- Price above 200-day MA: Long-term bullish
- Golden Cross (50-day > 200-day): Very bullish
- Death Cross (50-day < 200-day): Very bearish

ERROR HANDLING:
- If ticker extraction fails, ask user to specify the stock symbol
- If technical data is unavailable, explain the limitation
- Handle API errors gracefully with helpful messages

RISK DISCLAIMER:
Always include: "This is not financial advice. Please do your own research and consider your risk tolerance before making investment decisions."

EXAMPLE RESPONSES:
- "STRONG BUY signal for AAPL. RSI at 45 shows healthy momentum, price is above both 50-day ($150) and 200-day ($140) moving averages indicating strong uptrend. Recent golden cross formation supports bullish outlook."
- "HOLD signal for TSLA. Mixed technical picture with RSI at 65 approaching overbought territory, though price remains above key moving averages. Wait for clearer directional signals."
"""
)

# Export the agent for use in orchestrator
__all__ = ['root_agent', 'extract_ticker_from_input']
