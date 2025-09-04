"""
Technical Agent

Purpose:
- Fetches historical OHLCV data from NASDAQ API
- Calculates technical indicators (RSI, MACD, SMA, EMA)
- Converts indicator results into a normalized technical score

Flow:
1. Coordinator passes ticker → Technical Agent
2. Calls nasdaq_api.get_historical_data(ticker)
3. Extracts closing prices from DataFrame
4. Calculates technical indicators using indicators.py functions
5. Passes indicators → scoring.technical_score
6. Returns structured dict {indicators, technical_score}
"""

import logging
from typing import Dict, Any, List
from google.adk.agents import LlmAgent

# Import utility functions
from ..utils.nasdaq_api import get_historical_data
from ..utils.indicators import extract_closing_prices, rsi, macd, sma, ema
from ..utils.scoring import technical_score

logger = logging.getLogger(__name__)


def fetch_historical_data(ticker: str, period: str = "3mo") -> Dict[str, Any]:
    """
    Fetch historical OHLCV data from NASDAQ API and extract closing prices.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        period: Time period string ("1mo", "3mo", "6mo", "1y", "2y")
        
    Returns:
        Dict containing:
        - symbol: Stock ticker
        - closing_prices: List of closing prices
        - data_points: Number of data points retrieved
        - period: Time period used
    """
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided to fetch_historical_data: {ticker}")
        return {
            "symbol": "",
            "closing_prices": [],
            "data_points": 0,
            "period": period,
            "error": "Invalid ticker provided"
        }
    
    ticker = ticker.upper().strip()
    logger.info(f"Fetching historical data for ticker: {ticker}, period: {period}")
    
    try:
        # Get historical data as DataFrame
        df = get_historical_data(ticker, period)
        
        if df.empty:
            logger.warning(f"No historical data returned for ticker: {ticker}")
            return {
                "symbol": ticker,
                "closing_prices": [],
                "data_points": 0,
                "period": period,
                "error": "No historical data available"
            }
        
        # Extract closing prices from DataFrame
        closing_prices = extract_closing_prices(df)
        
        if not closing_prices:
            logger.warning(f"No closing prices extracted for ticker: {ticker}")
            return {
                "symbol": ticker,
                "closing_prices": [],
                "data_points": 0,
                "period": period,
                "error": "No valid closing prices found"
            }
        
        result = {
            "symbol": ticker,
            "closing_prices": closing_prices,
            "data_points": len(closing_prices),
            "period": period
        }
        
        logger.info(f"Successfully fetched {len(closing_prices)} data points for {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")
        return {
            "symbol": ticker,
            "closing_prices": [],
            "data_points": 0,
            "period": period,
            "error": f"Error fetching data: {str(e)}"
        }


def calculate_technical_indicators(closing_prices: List[float]) -> Dict[str, Any]:
    """
    Calculate technical indicators from closing prices.
    
    Args:
        closing_prices: List of closing price values
        
    Returns:
        Dict containing calculated indicators:
        - rsi: RSI value (14-period)
        - macd: MACD dict with macd_line, signal_line, histogram
        - sma_50: 50-period Simple Moving Average
        - sma_200: 200-period Simple Moving Average
        - ema_12: 12-period Exponential Moving Average
        - ema_26: 26-period Exponential Moving Average
        - current_price: Latest closing price
        - data_points: Number of data points used
    """
    if not closing_prices or not isinstance(closing_prices, list):
        logger.error("Invalid closing prices provided to calculate_technical_indicators")
        return {
            "rsi": None,
            "macd": {"macd_line": None, "signal_line": None, "histogram": None},
            "sma_50": None,
            "sma_200": None,
            "ema_12": None,
            "ema_26": None,
            "current_price": None,
            "data_points": 0,
            "error": "Invalid closing prices data"
        }
    
    if len(closing_prices) < 14:
        logger.warning(f"Insufficient data for technical indicators: need at least 14, got {len(closing_prices)}")
        return {
            "rsi": None,
            "macd": {"macd_line": None, "signal_line": None, "histogram": None},
            "sma_50": None,
            "sma_200": None,
            "ema_12": None,
            "ema_26": None,
            "current_price": closing_prices[-1] if closing_prices else None,
            "data_points": len(closing_prices),
            "error": "Insufficient data for technical analysis"
        }
    
    try:
        logger.info(f"Calculating technical indicators for {len(closing_prices)} data points")
        
        # Calculate RSI (14-period)
        rsi_value = rsi(closing_prices, 14)
        
        # Calculate MACD (12, 26, 9)
        macd_data = macd(closing_prices, 12, 26, 9)
        
        # Calculate Simple Moving Averages
        sma_50_value = sma(closing_prices, 50) if len(closing_prices) >= 50 else None
        sma_200_value = sma(closing_prices, 200) if len(closing_prices) >= 200 else None
        
        # Calculate Exponential Moving Averages
        ema_12_value = ema(closing_prices, 12)
        ema_26_value = ema(closing_prices, 26) if len(closing_prices) >= 26 else None
        
        # Get current price
        current_price = closing_prices[-1] if closing_prices else None
        
        indicators = {
            "rsi": rsi_value,
            "macd": macd_data,
            "sma_50": sma_50_value,
            "sma_200": sma_200_value,
            "ema_12": ema_12_value,
            "ema_26": ema_26_value,
            "current_price": current_price,
            "data_points": len(closing_prices)
        }
        
        logger.info(f"Successfully calculated technical indicators")
        logger.debug(f"RSI: {rsi_value}, MACD: {macd_data}, SMA50: {sma_50_value}, SMA200: {sma_200_value}")
        
        return indicators
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        return {
            "rsi": None,
            "macd": {"macd_line": None, "signal_line": None, "histogram": None},
            "sma_50": None,
            "sma_200": None,
            "ema_12": None,
            "ema_26": None,
            "current_price": closing_prices[-1] if closing_prices else None,
            "data_points": len(closing_prices),
            "error": f"Error calculating indicators: {str(e)}"
        }


def calculate_technical_score(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate technical score from indicators using scoring module.
    
    Args:
        indicators: Dict containing technical indicator values
        
    Returns:
        Dict containing:
        - technical_score: Float score (0-100)
        - indicators: Original indicators data for auditing
        - analysis: Breakdown of scoring components
    """
    if not indicators or not isinstance(indicators, dict):
        logger.warning("Invalid or empty indicators data provided to calculate_technical_score")
        return {
            "technical_score": 50.0,
            "indicators": {},
            "analysis": "No indicators data available for analysis"
        }
    
    # Check if there's an error in the indicators
    if "error" in indicators:
        return {
            "technical_score": 50.0,
            "indicators": indicators,
            "analysis": f"Error in indicators: {indicators['error']}"
        }
    
    try:
        # Calculate the technical score using the scoring module
        score = technical_score(indicators)
        
        # Extract key indicators for analysis breakdown
        rsi_value = indicators.get("rsi")
        macd_data = indicators.get("macd", {})
        sma_50 = indicators.get("sma_50")
        sma_200 = indicators.get("sma_200")
        current_price = indicators.get("current_price")
        data_points = indicators.get("data_points", 0)
        
        # Build analysis string
        analysis_parts = [f"Technical Analysis based on {data_points} data points:"]
        
        if rsi_value is not None:
            if rsi_value < 30:
                rsi_signal = "Oversold (Bullish)"
            elif rsi_value > 70:
                rsi_signal = "Overbought (Bearish)"
            else:
                rsi_signal = "Neutral"
            analysis_parts.append(f"- RSI(14): {rsi_value:.2f} - {rsi_signal}")
        
        if isinstance(macd_data, dict) and macd_data.get("macd_line") is not None:
            macd_line = macd_data.get("macd_line")
            signal_line = macd_data.get("signal_line")
            if signal_line is not None:
                macd_signal = "Bullish" if macd_line > signal_line else "Bearish"
                analysis_parts.append(f"- MACD: {macd_line:.4f} vs Signal: {signal_line:.4f} - {macd_signal}")
        
        if sma_50 is not None and sma_200 is not None:
            ma_signal = "Golden Cross (Bullish)" if sma_50 > sma_200 else "Death Cross (Bearish)"
            analysis_parts.append(f"- SMA50: {sma_50:.2f} vs SMA200: {sma_200:.2f} - {ma_signal}")
        elif sma_50 is not None:
            analysis_parts.append(f"- SMA50: {sma_50:.2f}")
        
        if current_price is not None and sma_50 is not None:
            price_signal = "Above SMA50 (Bullish)" if current_price > sma_50 else "Below SMA50 (Bearish)"
            analysis_parts.append(f"- Price vs SMA50: {current_price:.2f} vs {sma_50:.2f} - {price_signal}")
        
        analysis_parts.append(f"- Overall Technical Score: {score:.2f}/100")
        
        analysis = "\n".join(analysis_parts)
        
        result = {
            "technical_score": score,
            "indicators": indicators,
            "analysis": analysis
        }
        
        logger.info(f"Calculated technical score: {score:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating technical score: {e}")
        return {
            "technical_score": 50.0,
            "indicators": indicators,
            "analysis": f"Error in technical score calculation: {str(e)}"
        }


# Define the Technical Agent using Google ADK
TechnicalAgent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="technical_analyst",
    description="Analyze stock price data and technical indicators to compute technical strength scores",
    instruction="""
    You are a technical analyst agent that evaluates stocks based on price action and technical indicators.
    
    Your primary functions are:
    1. Fetch historical price data using the fetch_historical_data tool
    2. Calculate technical scores (0-100) using the calculate_technical_score tool
    3. Provide detailed analysis of technical patterns and indicators
    
    Key technical indicators you analyze:
    - RSI (Relative Strength Index) for momentum
    - MACD (Moving Average Convergence Divergence) for trend
    - Simple Moving Averages (SMA) for trend direction
    - Exponential Moving Averages (EMA) for recent price action
    - Price momentum and volatility patterns
    - Support and resistance levels
    - Volume analysis and trading patterns
    
    Always provide both the numerical score and qualitative analysis explaining the technical setup.
    Focus on identifying trend direction, momentum strength, and potential entry/exit points.
    """,
    tools=[
        fetch_historical_data,
        calculate_technical_score
    ]
)