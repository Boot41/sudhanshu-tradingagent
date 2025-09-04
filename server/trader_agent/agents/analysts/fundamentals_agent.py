"""
Fundamentals Agent

Purpose:
- Fetches company summary/fundamentals from NASDAQ API
- Extracts ratios, sector, dividend yield, market cap
- Transforms raw data into a fundamental score via scoring.fundamentals_score

Flow:
1. Coordinator passes ticker → Fundamentals Agent
2. Calls nasdaq_api.get_company_data(ticker)
3. Extracts key ratios (P/E, debt/equity, dividend, etc.)
4. Passes ratios → scoring.fundamentals_score
5. Returns structured dict {raw_data, fundamentals_score}
"""

import logging
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

# Import utility functions
from utils.nasdaq_api import get_company_data
from utils.scoring import fundamentals_score

logger = logging.getLogger(__name__)


def fetch_company_data(ticker: str) -> Dict[str, Any]:
    """
    Fetch company fundamental data from NASDAQ API.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        
    Returns:
        Dict containing normalized company data with keys like:
        - symbol, company_name, sector, industry
        - market_cap, pe_ratio, dividend_yield
        - price, volume, avg_volume
        - high_52week, low_52week, etc.
    """
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided to fetch_company_data: {ticker}")
        return {}
    
    ticker = ticker.upper().strip()
    logger.info(f"Fetching company data for ticker: {ticker}")
    
    try:
        company_data = get_company_data(ticker)
        
        if not company_data:
            logger.warning(f"No company data returned for ticker: {ticker}")
            return {}
        
        logger.info(f"Successfully fetched company data for {ticker}")
        return company_data
        
    except Exception as e:
        logger.error(f"Error fetching company data for {ticker}: {e}")
        return {}


def calculate_fundamentals_score(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate fundamentals score from company data.
    
    Args:
        company_data: Normalized company data dict from fetch_company_data
        
    Returns:
        Dict containing:
        - fundamental_score: Float score (0-100)
        - raw_data: Original company data for auditing
        - analysis: Breakdown of scoring components
    """
    if not company_data or not isinstance(company_data, dict):
        logger.warning("Invalid or empty company data provided to calculate_fundamentals_score")
        return {
            "fundamental_score": 50.0,
            "raw_data": {},
            "analysis": "No data available for analysis"
        }
    
    try:
        # Calculate the fundamentals score using the scoring module
        score = fundamentals_score(company_data)
        
        # Extract key metrics for analysis breakdown
        symbol = company_data.get("symbol", "Unknown")
        market_cap = company_data.get("market_cap", "N/A")
        pe_ratio = company_data.get("pe_ratio", "N/A")
        dividend_yield = company_data.get("dividend_yield", "N/A")
        sector = company_data.get("sector", "N/A")
        debt_to_equity = company_data.get("debt_to_equity", "N/A")
        price_to_book = company_data.get("price_to_book", "N/A")
        
        analysis = f"""
        Fundamentals Analysis for {symbol}:
        - Market Cap: {market_cap}
        - P/E Ratio: {pe_ratio}
        - Dividend Yield: {dividend_yield}
        - Sector: {sector}
        - Overall Score: {score:.2f}/100
        """
        
        result = {
            "fundamental_score": score,
            "raw_data": company_data,
            "analysis": analysis.strip()
        }
        
        logger.info(f"Calculated fundamentals score {score:.2f} for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating fundamentals score: {e}")
        return {
            "fundamental_score": 50.0,
            "raw_data": company_data,
            "analysis": f"Error in analysis: {str(e)}"
        }


# Define the Fundamentals Agent using Google ADK
FundamentalsAgent = LlmAgent(
    name="fundamentals_analyst",
    role="Analyze company fundamentals and compute fundamental strength scores",
    instructions="""
    You are a fundamentals analyst responsible for evaluating company financial health and fundamentals.
    
    Your workflow:
    1. When given a stock ticker, use fetch_company_data to get comprehensive company information from NASDAQ API
    2. Use calculate_fundamentals_score to convert the raw fundamental data into a normalized 0-100 score
    3. Provide clear analysis explaining the key factors that influenced the score
    
    Key metrics you analyze:
    - Market capitalization and company size
    - P/E ratio and valuation metrics
    - Dividend yield and income generation
    - Trading volume and liquidity
    - 52-week price performance and momentum
    - Sector and industry classification
    
    Always provide both the numerical score and qualitative analysis to help traders understand the investment thesis.
    Focus on identifying value opportunities and potential red flags in the fundamental data.
    """,
    tools=[
        Tool(name="fetch_company_data", func=fetch_company_data),
        Tool(name="calculate_fundamentals_score", func=calculate_fundamentals_score)
    ]
)