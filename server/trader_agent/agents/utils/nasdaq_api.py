"""
NASDAQ API Client - Central hub for external financial data access.

This module provides a clean interface for fetching:
1. Company fundamental data and summaries
2. Historical price data (OHLCV) as pandas DataFrames
3. News articles related to specific stocks

All functions abstract away raw HTTP requests and return normalized Python structures.
Agents can call these functions directly without handling URLs or HTTP details.
"""

import logging
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd

from .http import get_json, DEFAULT_HEADERS

logger = logging.getLogger(__name__)


def _iso_date(d: date) -> str:
    """Convert date object to ISO format string (YYYY-MM-DD)."""
    return d.isoformat()


def _default_date_range(months: int = 3) -> tuple[str, str]:
    """
    Generate default date range for historical data queries.
    
    Args:
        months: Number of months back from today (default: 3)
        
    Returns:
        Tuple of (start_date, end_date) in ISO format
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=30 * months)
    return _iso_date(start_date), _iso_date(end_date)


def _parse_period_to_months(period: str) -> int:
    """
    Parse period string to number of months.
    
    Args:
        period: Period string like "1mo", "3mo", "6mo", "1y", "2y"
        
    Returns:
        Number of months as integer
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
        # Default fallback
        logger.warning(f"Unknown period format: {period}, defaulting to 3 months")
        return 3


def _normalize_historical_data(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert raw NASDAQ historical data to normalized pandas DataFrame.
    
    Args:
        raw_data: Raw JSON response from NASDAQ API
        
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume
    """
    if not raw_data or 'data' not in raw_data:
        logger.warning("No data found in historical response")
        return pd.DataFrame()
    
    try:
        data_points = raw_data['data']
        if not data_points:
            return pd.DataFrame()
        
        # Extract OHLCV data
        df_data = []
        for point in data_points:
            if isinstance(point, dict):
                df_data.append({
                    'Date': pd.to_datetime(point.get('date', '')),
                    'Open': float(point.get('open', 0) or 0),
                    'High': float(point.get('high', 0) or 0),
                    'Low': float(point.get('low', 0) or 0),
                    'Close': float(point.get('close', 0) or 0),
                    'Volume': int(point.get('volume', 0) or 0)
                })
        
        df = pd.DataFrame(df_data)
        if not df.empty:
            df = df.sort_values('Date').reset_index(drop=True)
            df.set_index('Date', inplace=True)
        
        return df
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error normalizing historical data: {e}")
        return pd.DataFrame()


def _normalize_company_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize company data response to consistent format.
    
    Args:
        raw_data: Raw JSON response from NASDAQ API
        
    Returns:
        Normalized company data dictionary
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
    
    Args:
        raw_data: Raw JSON response from NASDAQ API
        
    Returns:
        List of normalized news article dictionaries
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


def get_company_data(ticker: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Fetch comprehensive company data including fundamentals and summary statistics.
    
    This function retrieves company profile, financial metrics, and current market data
    from NASDAQ's company summary API. Used primarily by fundamental analysis agents.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        use_cache: Whether to use HTTP caching (default: True)
        
    Returns:
        Dictionary containing normalized company data:
        - symbol, company_name, sector, industry
        - market_cap, pe_ratio, dividend_yield
        - current price, change, volume data
        - 52-week high/low ranges
        
    Example:
        >>> data = get_company_data("AAPL")
        >>> print(data['company_name'])  # "Apple Inc."
        >>> print(data['market_cap'])    # "$3.2T"
    """
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


def get_historical_data(ticker: str, period: str = "3mo", use_cache: bool = True) -> pd.DataFrame:
    """
    Fetch historical OHLCV (Open, High, Low, Close, Volume) data as pandas DataFrame.
    
    This function retrieves historical price and volume data from NASDAQ's charting API.
    Used primarily by technical analysis agents for trend analysis and indicator calculations.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        period: Time period for data ("1mo", "3mo", "6mo", "1y", "2y")
        use_cache: Whether to use HTTP caching (default: True)
        
    Returns:
        pandas DataFrame with DatetimeIndex and columns:
        - Open, High, Low, Close (float prices)
        - Volume (integer)
        
    Example:
        >>> df = get_historical_data("AAPL", "6mo")
        >>> print(df.head())
        >>> print(df['Close'].mean())  # Average closing price
    """
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided: {ticker}")
        return pd.DataFrame()
    
    ticker = ticker.upper().strip()
    months = _parse_period_to_months(period)
    start_date, end_date = _default_date_range(months)
    
    logger.info(f"Fetching historical data for {ticker} from {start_date} to {end_date}")
    
    url = f"https://charting.nasdaq.com/data/charting/historical?symbol={ticker}&date={start_date}~{end_date}&"
    
    raw_data = get_json(url, headers=DEFAULT_HEADERS, use_cache=use_cache)
    if not raw_data:
        logger.error(f"Failed to fetch historical data for {ticker}")
        return pd.DataFrame()
    
    df = _normalize_historical_data(raw_data)
    logger.info(f"Successfully retrieved {len(df)} data points for {ticker}")
    return df


def get_news_data(ticker: str, limit: int = 10, offset: int = 0, use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch recent news articles related to a specific stock symbol.
    
    This function retrieves news articles from NASDAQ's news API, providing
    sentiment analysis data for fundamental and news-based trading strategies.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        limit: Maximum number of articles to retrieve (default: 10)
        offset: Number of articles to skip (for pagination, default: 0)
        use_cache: Whether to use HTTP caching (default: True)
        
    Returns:
        List of dictionaries containing normalized news data:
        - title, summary, url, published_date
        - source, tags
        
    Example:
        >>> articles = get_news_data("AAPL", limit=5)
        >>> for article in articles:
        ...     print(f"{article['title']} - {article['source']}")
    """
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


# Utility functions for agents
def get_multiple_tickers_data(tickers: List[str], data_type: str = "company", **kwargs) -> Dict[str, Any]:
    """
    Fetch data for multiple tickers efficiently.
    
    Args:
        tickers: List of stock symbols
        data_type: Type of data to fetch ("company", "historical", "news")
        **kwargs: Additional arguments passed to individual fetch functions
        
    Returns:
        Dictionary mapping ticker -> data
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