from google.adk.agents import LlmAgent
from google.adk.tools import Tool
from utils.nasdaq_api import resolve_ticker
import logging

logger = logging.getLogger(__name__)

def resolve_and_validate_ticker(query: str) -> dict:
    """
    Resolve company name or ticker symbol to a valid ticker using NASDAQ API.
    
    Args:
        query: Company name (e.g., "Apple") or ticker symbol (e.g., "AAPL")
        
    Returns:
        dict: {
            "symbol": str or None,
            "valid": bool,
            "message": str
        }
    """
    if not query or not query.strip():
        return {
            "symbol": None,
            "valid": False,
            "message": "Empty query provided"
        }
    
    query = query.strip()
    logger.info(f"Attempting to resolve ticker for: {query}")
    
    try:
        # Use the resolve_ticker function from nasdaq_api
        resolved_ticker = resolve_ticker(query)
        
        if resolved_ticker:
            return {
                "symbol": resolved_ticker,
                "valid": True,
                "message": f"Successfully resolved '{query}' to ticker: {resolved_ticker}"
            }
        else:
            return {
                "symbol": None,
                "valid": False,
                "message": f"Could not resolve ticker for: {query}"
            }
            
    except Exception as e:
        logger.error(f"Error resolving ticker for '{query}': {e}")
        return {
            "symbol": None,
            "valid": False,
            "message": f"Error occurred while resolving ticker: {str(e)}"
        }

TickerAgent = LlmAgent(
    name="ticker_resolver",
    role="Convert company names to valid NASDAQ ticker symbols",
    instructions="""
    You are a ticker resolution agent that converts user input (company names or potential ticker symbols) 
    into valid NASDAQ ticker symbols.
    
    Your primary function is to:
    1. Take user input like "Apple", "Microsoft", "AAPL", etc.
    2. Use the resolve_and_validate_ticker tool to convert it to a valid ticker
    3. Return the resolved ticker symbol along with validation status
    
    Always use the resolve_and_validate_ticker tool for any ticker resolution requests.
    Provide clear feedback about whether the resolution was successful or not.
    """,
    tools=[Tool(name="resolve_and_validate_ticker", func=resolve_and_validate_ticker)]
)