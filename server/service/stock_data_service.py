"""
Stock data service for fetching historical data and technical indicators.
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
from typing import Dict, Any


def get_historical_data(ticker: str, period: str = "3mo", interval: str = "1d") -> str:
    """
    Fetches historical stock data for a given ticker.
    
    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL').
        period: The time period (e.g., '1mo', '3mo', '1y').
        interval: The data interval (e.g., '1d', '1wk').
        
    Returns:
        A JSON string of the historical data.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        
        if hist.empty:
            return f"Could not find data for ticker {ticker}."
            
        return hist.to_json()
    except Exception as e:
        return f"Error fetching data for ticker {ticker}: {str(e)}"


def get_technical_indicators(ticker: str) -> Dict[str, Any]:
    """
    Calculates key technical indicators (RSI, Moving Averages) for a stock.
    
    Args:
        ticker: The stock ticker symbol.
        
    Returns:
        A dictionary with indicator values and trading signal.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            return {"error": f"Could not find data for ticker {ticker}."}

        # Calculate technical indicators
        rsi = hist.ta.rsi()
        ma50 = hist.ta.sma(50)
        ma200 = hist.ta.sma(200)

        # Get latest values
        last_close = hist['Close'].iloc[-1]
        last_rsi = rsi.iloc[-1]
        last_ma50 = ma50.iloc[-1]
        last_ma200 = ma200.iloc[-1]

        # Generate trading signal
        signal = "HOLD"
        if last_close > last_ma50 and last_close > last_ma200 and last_rsi < 70:
            signal = "BUY"
        elif last_close < last_ma50 and last_rsi > 30:
            signal = "SELL"
        
        return {
            "ticker": ticker,
            "last_close": round(last_close, 2),
            "rsi": round(last_rsi, 2),
            "ma50": round(last_ma50, 2),
            "ma200": round(last_ma200, 2),
            "signal": signal
        }
        
    except Exception as e:
        return {"error": f"Error calculating indicators for ticker {ticker}: {str(e)}"}
