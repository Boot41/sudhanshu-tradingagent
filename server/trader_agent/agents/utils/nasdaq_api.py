"""
Financial Data Client - Central hub for external financial data access.

This module provides a clean interface for fetching:
1. Historical price data (OHLCV) as pandas DataFrames using yfinance.
2. Company fundamental data and news (using deprecated Nasdaq endpoints).

All functions abstract away raw HTTP requests and return normalized Python structures.
Agents can call these functions directly without handling URLs or HTTP details.
"""

import logging
import os
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import yfinance as yf
from curl_cffi import requests as curl_requests

# http_client is still needed for the other (deprecated) functions
from http_client import get_json, DEFAULT_HEADERS

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


def _iso_date(d: date) -> str:
    """Convert date object to ISO format string (YYYY-MM-DD)."""
    return d.isoformat()


def _default_date_range(months: int = 3) -> tuple[str, str]:
    """
    Generate default date range for historical data queries.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=30 * months)
    return _iso_date(start_date), _iso_date(end_date)


def _parse_period_to_months(period: str) -> int:
    """
    Parse period string to number of months.
    """
    period = period.lower().strip()
    
    if period.endswith('mo'):
        return int(period[:-2])
    elif period.endswith('m'):
        return int(period[:-1])
    elif period.endswith('y'):
        return int(period[:-1]) * 12
    elif period.endswith('d'):
        # Convert days to approximate months
        days = int(period[:-1])
        return max(1, days // 30)
    else:
        logger.warning(f"Unknown period format: {period}, defaulting to 3 months")
        return 3

# --- Normalization functions for deprecated endpoints ---

def _normalize_company_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize company data response to consistent format.
    """
    if not raw_data or 'data' not in raw_data:
        return {}
    
    try:
        data = raw_data['data']
        summary_data = data.get('summaryData', {})
        
        return {
            'symbol': data.get('symbol', ''),
            'company_name': summary_data.get('CompanyName', {}).get('value', ''),
            'sector': summary_data.get('Sector', {}).get('value', ''),
            'industry': summary_data.get('Industry', {}).get('value', ''),
            'market_cap': summary_data.get('MarketCap', {}).get('value', ''),
            'pe_ratio': summary_data.get('PERatio', {}).get('value', ''),
            'dividend_yield': summary_data.get('Yield', {}).get('value', ''),
            'price': summary_data.get('LastSale', {}).get('value', ''),
            'change': summary_data.get('NetChange', {}).get('value', ''),
            'change_percent': summary_data.get('PctChange', {}).get('value', ''),
            'volume': summary_data.get('Volume', {}).get('value', ''),
            'avg_volume': summary_data.get('AverageVolume', {}).get('value', ''),
            'high_52week': summary_data.get('High52Weeks', {}).get('value', ''),
            'low_52week': summary_data.get('Low52Weeks', {}).get('value', ''),
        }
        
    except (KeyError, TypeError) as e:
        logger.error(f"Error normalizing company data: {e}")
        return {}


def _normalize_news_data(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize news data response to consistent format.
    """
    if not raw_data or 'data' not in raw_data:
        return []
    
    try:
        articles = raw_data['data'].get('rows', [])
        normalized_articles = []
        
        for article in articles:
            if isinstance(article, dict):
                normalized_articles.append({
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'published_date': article.get('published_date', ''),
                    'source': article.get('source', ''),
                    'tags': article.get('tags', [])
                })
        
        return normalized_articles
        
    except (KeyError, TypeError) as e:
        logger.error(f"Error normalizing news data: {e}")
        return []


# --- Data Fetching Functions ---

def get_historical_data(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """
    Fetch historical OHLCV data using yfinance with a session that impersonates a browser
    to avoid rate limiting.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        period: Time period string ("1mo", "3mo", "6mo", "1y", "2y")
        
    Returns:
        pandas DataFrame with DatetimeIndex and columns for OHLCV data.
    """
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided: {ticker}")
        return pd.DataFrame()

    ticker = ticker.upper().strip()
    months = _parse_period_to_months(period)
    start_date, end_date = _default_date_range(months)
    
    logger.info(f"Fetching historical data for {ticker} from {start_date} to {end_date} using yfinance.")
    
    try:
        # Create a session object that impersonates a Chrome browser
        session = curl_requests.Session(impersonate="chrome")
        
        # Pass the session to the yfinance Ticker object
        yf_ticker = yf.Ticker(ticker, session=session)
        
        # Download the data using the custom session
        df = yf_ticker.history(start=start_date, end=end_date, auto_adjust=True)
        
        if df.empty:
            logger.warning(f"yfinance returned no data for {ticker} in the given period.")
            return pd.DataFrame()
            
        logger.info(f"Successfully retrieved {len(df)} data points for {ticker}")
        return df

    except Exception as e:
        logger.error(f"An error occurred while fetching data with yfinance for {ticker}: {e}")
        return pd.DataFrame()

def get_company_data(ticker: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    [DEPRECATED] Fetch comprehensive company data. Uses an old, unreliable endpoint.
    """
    logger.warning("get_company_data uses a deprecated, unreliable endpoint and may fail.")
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided: {ticker}")
        return {}
    
    ticker = ticker.upper().strip()
    logger.info(f"Fetching company data for {ticker}")
    
    url = f"https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks"
    headers = {"accept": "application/json", **DEFAULT_HEADERS}
    
    raw_data = get_json(url, headers=headers, use_cache=use_cache)
    if not raw_data:
        logger.error(f"Failed to fetch company data for {ticker}")
        return {}
    
    normalized_data = _normalize_company_data(raw_data)
    logger.info(f"Successfully retrieved company data for {ticker}")
    return normalized_data


def get_news_data(ticker: str, limit: int = 10, offset: int = 0, use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    [DEPRECATED] Fetch recent news articles. Uses an old, unreliable endpoint.
    """
    logger.warning("get_news_data uses a deprecated, unreliable endpoint and may fail.")
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided: {ticker}")
        return []
    
    ticker = ticker.upper().strip()
    logger.info(f"Fetching news data for {ticker} (limit: {limit}, offset: {offset})")
    
    url = f"https://www.nasdaq.com/api/news/topic/articlebysymbol?q={ticker}|STOCKS&offset={offset}&limit={limit}&fallback=true"
    headers = {"accept": "application/json", **DEFAULT_HEADERS}
    
    raw_data = get_json(url, headers=headers, use_cache=use_cache)
    if not raw_data:
        logger.error(f"Failed to fetch news data for {ticker}")
        return []
    
    articles = _normalize_news_data(raw_data)
    logger.info(f"Successfully retrieved {len(articles)} news articles for {ticker}")
    return articles


def get_multiple_tickers_data(tickers: List[str], data_type: str = "company", **kwargs) -> Dict[str, Any]:
    """
    Fetch data for multiple tickers efficiently.
    """
    results = {}
    
    for ticker in tickers:
        try:
            if data_type == "company":
                results[ticker] = get_company_data(ticker, **kwargs)
            elif data_type == "historical":
                results[ticker] = get_historical_data(ticker, **kwargs)
            elif data_type == "news":
                results[ticker] = get_news_data(ticker, **kwargs)
            else:
                logger.error(f"Unknown data type: {data_type}")
                
        except Exception as e:
            logger.error(f"Error fetching {data_type} data for {ticker}: {e}")
            results[ticker] = None
    
    return results
