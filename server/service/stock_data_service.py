"""
Stock data service for fetching historical data and technical indicators.
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time
import random
import logging
from typing import Dict, Any, Optional
from functools import lru_cache
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _get_mock_historical_data(ticker: str, period: str = "3mo") -> Dict[str, Any]:
    """Generate mock historical data when API is unavailable."""
    from datetime import datetime, timedelta
    
    # Generate mock data based on ticker
    base_price = {"AAPL": 150, "MSFT": 300, "GOOGL": 2500, "TSLA": 200, "AMZN": 3000}.get(ticker, 100)
    
    # Generate 30 days of mock data
    data = {"Open": {}, "High": {}, "Low": {}, "Close": {}, "Volume": {}}
    
    for i in range(30):
        date_str = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
        price = base_price + random.uniform(-10, 10)
        data["Open"][date_str] = round(price, 2)
        data["High"][date_str] = round(price + random.uniform(0, 5), 2)
        data["Low"][date_str] = round(price - random.uniform(0, 5), 2)
        data["Close"][date_str] = round(price + random.uniform(-2, 2), 2)
        data["Volume"][date_str] = random.randint(1000000, 10000000)
    
    return data

@lru_cache(maxsize=100)
def get_historical_data(ticker: str, period: str = "3mo", interval: str = "1d") -> Dict[str, Any]:
    """
    Fetches historical stock data for a given ticker.

    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL').
        period: The time period (e.g., '1mo', '3mo', '1y').
        interval: The data interval (e.g., '1d', '1wk').

    Returns:
        A dictionary of the historical data.
    """
    logger.info(f"StockDataService: get_historical_data called with ticker={ticker}, period={period}, interval={interval}")
    try:
        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(0.1, 0.5))

        logger.info(f"StockDataService: Creating yfinance Ticker for {ticker}")
        stock = yf.Ticker(ticker)
        logger.info(f"StockDataService: Fetching history for {ticker} with period={period}, interval={interval}")
        hist = stock.history(period=period, interval=interval)
        logger.info(f"StockDataService: History fetched, shape: {hist.shape if not hist.empty else 'EMPTY'}")

        if hist.empty:
            logger.warning(f"StockDataService: No data returned from yfinance for {ticker}, using mock data")
            return _get_mock_historical_data(ticker, period)

        # Convert to dictionary with proper date formatting
        result = hist.to_dict()
        
        # Convert timestamp index to readable date strings
        date_mapping = {}
        for old_key in list(result['Open'].keys()):
            new_key = old_key.strftime('%Y-%m-%d %H:%M:%S') if hasattr(old_key, 'strftime') else str(old_key)
            date_mapping[old_key] = new_key
        
        # Update all columns with new date keys
        for column in result:
            new_column = {}
            for old_key, value in result[column].items():
                new_key = date_mapping.get(old_key, str(old_key))
                new_column[new_key] = value
            result[column] = new_column
            
        logger.info(f"StockDataService: Successfully processed historical data for {ticker}")
        return result

    except Exception as e:
        logger.error(f"StockDataService: Error fetching data for {ticker}: {e}")
        # If yfinance fails (rate limiting, network issues), return mock data
        if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
            logger.warning(f"StockDataService: Rate limit hit for {ticker}, using mock data")
            return _get_mock_historical_data(ticker, period)
        return {"error": f"Error fetching data for ticker {ticker}: {str(e)}"}


def _get_mock_technical_indicators(ticker: str) -> Dict[str, Any]:
    """Generate mock technical indicators when API is unavailable."""
    base_price = {"AAPL": 250, "MSFT": 300, "GOOGL": 2500, "TSLA": 200, "AMZN": 3000}.get(ticker, 100)
    
    # Generate realistic mock values
    last_close = base_price + random.uniform(-5, 5)
    rsi = random.uniform(30, 70)
    ma50 = last_close + random.uniform(-10, 10)
    ma200 = last_close + random.uniform(-20, 20)
    
    # Generate signal based on mock data
    signal = "HOLD"
    if last_close > ma50 and last_close > ma200 and rsi < 70:
        signal = "BUY"
    elif last_close < ma50 and rsi > 30:
        signal = "SELL"
    logger.debug(f"ticker: {ticker}, signal: {signal}, rsi: {rsi}, ma50: {ma50}, ma200: {ma200}")
    return {
        "ticker": ticker,
        "last_close": round(last_close, 2),
        "signal": signal,
        "rsi": round(rsi, 2),
        "ma50": round(ma50, 2),
        "ma200": round(ma200, 2),
        "analysis": f"Mock analysis for {ticker}: {signal} signal based on technical indicators"
    }

@lru_cache(maxsize=100)

def get_technical_indicators(ticker: str, period: str = "1y", indicators: Optional[str] = None) -> Dict[str, Any]:
    """
    Get technical indicators for a stock.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        indicators: List of indicators to calculate (sma, ema, rsi, macd, bollinger)
    
    Returns:
        Dictionary containing technical indicators
    """
    try:
        logger.debug(f"📊 StockDataService: ===== TECHNICAL INDICATORS REQUEST =====")
        logger.debug(f"📊 StockDataService: Ticker: {ticker}")
        logger.debug(f"📊 StockDataService: Period: {period}")
        logger.debug(f"📊 StockDataService: Indicators: {indicators}")
        logger.debug(f"📊 StockDataService: Starting data fetch...")
        if indicators is None:
            indicators = ("sma", "rsi")
        elif isinstance(indicators, list):
            indicators = tuple(indicators)

        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(0.1, 0.5))

        logger.info(f"📊 StockDataService: Creating yfinance Ticker object for {ticker}")
        stock = yf.Ticker(ticker)
        
        logger.info(f"📊 StockDataService: Fetching historical data for period {period}")
        hist = stock.history(period=period)
        
        logger.info(f"📊 StockDataService: Retrieved {len(hist)} data points")
        logger.info(f"📊 StockDataService: Data date range: {hist.index[0] if len(hist) > 0 else 'No data'} to {hist.index[-1] if len(hist) > 0 else 'No data'}")
        logger.info(f"StockDataService: History fetched, shape: {hist.shape if not hist.empty else 'EMPTY'}")

        if hist.empty:
            logger.warning(f"StockDataService: No data returned from yfinance for {ticker}, using mock data")
            return _get_mock_technical_indicators(ticker)

        # Calculate technical indicators
        rsi = ta.rsi(hist['Close'])
        ma50 = ta.sma(hist['Close'], length=50)
        ma200 = ta.sma(hist['Close'], length=200)

        # Get latest values
        last_close = hist['Close'].iloc[-1]
        last_rsi = rsi.iloc[-1] if rsi is not None and not rsi.empty else None
        last_ma50 = ma50.iloc[-1] if ma50 is not None and not ma50.empty else None
        last_ma200 = ma200.iloc[-1] if ma200 is not None and not ma200.empty else None

        # Generate trading signal
        signal = "HOLD"
        if (last_ma50 is not None and last_ma200 is not None and last_rsi is not None and
            last_close > last_ma50 and last_close > last_ma200 and last_rsi < 70):
            signal = "BUY"
        elif (last_ma50 is not None and last_rsi is not None and
              last_close < last_ma50 and last_rsi > 30):
            signal = "SELL"

        result = {
            "ticker": ticker,
            "last_close": round(last_close, 2),
            "signal": signal,
            "analysis": f"Technical analysis for {ticker}: {signal} signal based on RSI and moving averages"
        }

        if last_rsi is not None:
            result["rsi"] = round(last_rsi, 2)
        if last_ma50 is not None:
            result["ma50"] = round(last_ma50, 2)
        if last_ma200 is not None:
            result["ma200"] = round(last_ma200, 2)

        logger.info(f"✅ StockDataService: Successfully calculated technical indicators for {ticker}")
        logger.info(f"✅ StockDataService: Result keys: {list(result.keys())}")
        logger.info(f"✅ StockDataService: Result preview: {str(result)[:300]}...")
        logger.info(f"📊 StockDataService: ===== TECHNICAL INDICATORS COMPLETE =====")
        return result

    except Exception as e:
        logger.error(f"❌ StockDataService: Error calculating indicators for {ticker}: {e}")
        logger.error(f"❌ StockDataService: Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ StockDataService: Full traceback: {traceback.format_exc()}")
        
        # If yfinance fails (rate limiting, network issues), return mock data
        if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
            logger.warning(f"⚠️ StockDataService: Rate limit hit for {ticker}, using mock data")
            return _get_mock_technical_indicators(ticker)
        
        error_result = {"error": f"Error calculating indicators for ticker {ticker}: {str(e)}"}
        logger.error(f"❌ StockDataService: Returning error result: {error_result}")
        return error_result
