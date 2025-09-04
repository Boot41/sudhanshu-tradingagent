"""
Technical Indicators Module


Pure math/statistics utilities for technical indicators.
Does not fetch any data — only calculates indicators from price data.


Functions:
- sma(prices: List[float], window: int) -> Optional[float]
- ema(prices: List[float], window: int) -> Optional[float] 
- rsi(prices: List[float], window: int = 14) -> Optional[float]
- macd(prices: List[float], short_win: int = 12, long_win: int = 26, signal: int = 9) -> Dict[str, Optional[float]]


Flow:
Technical Agent fetches price history → nasdaq_api.get_historical_data()
Converts to closing price list → calls indicators functions
Passes results into scoring.py for score conversion
"""


import logging
from typing import List, Optional, Dict, Union


logger = logging.getLogger(__name__)



def sma(prices: List[float], window: int) -> Optional[float]:
    """
    Calculate Simple Moving Average.
    
    Args:
        prices: List of price values (typically closing prices)
        window: Number of periods to average over
        
    Returns:
        SMA value or None if insufficient data
    """
    if not prices or not isinstance(prices, list):
        logger.error("Invalid prices data provided to SMA calculation")
        return None
        
    if window <= 0:
        logger.error(f"Invalid window size for SMA: {window}")
        return None
        
    if len(prices) < window:
        logger.warning(f"Insufficient data for SMA calculation: need {window}, got {len(prices)}")
        return None
    
    try:
        # Use the last 'window' prices
        recent_prices = prices[-window:]
        sma_value = sum(recent_prices) / window
        logger.debug(f"Calculated SMA({window}): {sma_value:.4f}")
        return sma_value
    except (TypeError, ValueError) as e:
        logger.error(f"Error calculating SMA: {e}")
        return None




def _ema_series(prices: List[float], window: int) -> List[float]:
    """
    Calculate Exponential Moving Average series.
    
    Args:
        prices: List of price values
        window: EMA period/span
        
    Returns:
        List of EMA values (empty if insufficient data)
    """
    if len(prices) < window:
        return []
    
    try:
        # Smoothing factor
        multiplier = 2.0 / (window + 1)
        ema_values = []
        
        # Initialize with SMA of first 'window' prices
        initial_sma = sum(prices[:window]) / window
        ema_values.append(initial_sma)
        
        # Calculate EMA for remaining prices
        for price in prices[window:]:
            ema_value = (price * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema_value)
            
        return ema_values
    except (TypeError, ValueError, ZeroDivisionError) as e:
        logger.error(f"Error calculating EMA series: {e}")
        return []




def ema(prices: List[float], window: int) -> Optional[float]:
    """
    Calculate Exponential Moving Average.
    
    Args:
        prices: List of price values (typically closing prices)
        window: EMA period/span
        
    Returns:
        Latest EMA value or None if insufficient data
    """
    if not prices or not isinstance(prices, list):
        logger.error("Invalid prices data provided to EMA calculation")
        return None
        
    if window <= 0:
        logger.error(f"Invalid window size for EMA: {window}")
        return None
        
    if len(prices) < window:
        logger.warning(f"Insufficient data for EMA calculation: need {window}, got {len(prices)}")
        return None
    
    try:
        ema_series_values = _ema_series(prices, window)
        if not ema_series_values:
            return None
            
        ema_value = ema_series_values[-1]
        logger.debug(f"Calculated EMA({window}): {ema_value:.4f}")
        return ema_value
    except Exception as e:
        logger.error(f"Error calculating EMA: {e}")
        return None




def rsi(prices: List[float], window: int = 14) -> Optional[float]:
    """
    Calculate Relative Strength Index.
    
    Args:
        prices: List of price values (typically closing prices)
        window: RSI period (default: 14)
        
    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if not prices or not isinstance(prices, list):
        logger.error("Invalid prices data provided to RSI calculation")
        return None
        
    if window <= 0:
        logger.error(f"Invalid window size for RSI: {window}")
        return None
        
    # Need at least window + 1 prices to calculate price changes
    if len(prices) < window + 1:
        logger.warning(f"Insufficient data for RSI calculation: need {window + 1}, got {len(prices)}")
        return None
    
    try:
        # Calculate price changes over the entire series
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [c if c > 0 else 0 for c in changes]
        losses = [-c if c < 0 else 0 for c in changes]


        # Calculate initial average gain and loss using simple moving average
        avg_gain = sum(gains[:window]) / window
        avg_loss = sum(losses[:window]) / window


        # Smooth the rest of the values using a standard RSI smoothing method
        for i in range(window, len(gains)):
            avg_gain = (avg_gain * (window - 1) + gains[i]) / window
            avg_loss = (avg_loss * (window - 1) + losses[i]) / window
            
        # Handle edge case where avg_loss is 0 to avoid division by zero
        if avg_loss == 0:
            rsi_value = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_value = 100.0 - (100.0 / (1.0 + rs))
        
        logger.debug(f"Calculated RSI({window}): {rsi_value:.2f}")
        return rsi_value
        
    except (TypeError, ValueError, ZeroDivisionError) as e:
        logger.error(f"Error calculating RSI: {e}")
        return None




def macd(prices: List[float], short_win: int = 12, long_win: int = 26, signal: int = 9) -> Dict[str, Optional[float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        prices: List of price values (typically closing prices)
        short_win: Fast EMA period (default: 12)
        long_win: Slow EMA period (default: 26)
        signal: Signal line EMA period (default: 9)
        
    Returns:
        Dict with 'macd_line', 'signal_line', and 'histogram' values
    """
    if not prices or not isinstance(prices, list):
        logger.error("Invalid prices data provided to MACD calculation")
        return {"macd_line": None, "signal_line": None, "histogram": None}
        
    if short_win <= 0 or long_win <= 0 or signal <= 0:
        logger.error(f"Invalid window sizes for MACD: short={short_win}, long={long_win}, signal={signal}")
        return {"macd_line": None, "signal_line": None, "histogram": None}
        
    if short_win >= long_win:
        logger.error(f"Short window ({short_win}) must be less than long window ({long_win})")
        return {"macd_line": None, "signal_line": None, "histogram": None}
    
    # Check if there's enough data for the longest EMA calculation plus the signal line
    # The EMA of the MACD line (signal) requires its own window
    if len(prices) < long_win + signal:
        logger.warning(f"Insufficient data for MACD: need {long_win + signal}, got {len(prices)}")
        return {"macd_line": None, "signal_line": None, "histogram": None}
    
    try:
        # Calculate fast and slow EMA series
        fast_ema_series = _ema_series(prices, short_win)
        slow_ema_series = _ema_series(prices, long_win)
        
        if not fast_ema_series or not slow_ema_series:
            logger.error("Failed to calculate EMA series for MACD")
            return {"macd_line": None, "signal_line": None, "histogram": None}
        
        # Create the MACD line. It starts where the slow EMA starts.
        # Align the fast EMA to match the starting point of the slow EMA.
        offset = len(fast_ema_series) - len(slow_ema_series)
        macd_line_series = [fast_ema_series[i + offset] - slow_ema_series[i] for i in range(len(slow_ema_series))]


        # Check if we have enough MACD line data to calculate the signal line
        if len(macd_line_series) < signal:
            logger.warning(f"Insufficient MACD data for signal line: need {signal}, got {len(macd_line_series)}")
            return {"macd_line": None, "signal_line": None, "histogram": None}
        
        # Calculate signal line (EMA of MACD line)
        signal_line_series = _ema_series(macd_line_series, signal)
        
        if not signal_line_series:
            logger.error("Failed to calculate signal line for MACD")
            return {"macd_line": None, "signal_line": None, "histogram": None}
        
        # Get latest values
        macd_line_value = macd_line_series[-1]
        signal_line_value = signal_line_series[-1]
        histogram_value = macd_line_value - signal_line_value
        
        result = {
            "macd_line": macd_line_value,
            "signal_line": signal_line_value,
            "histogram": histogram_value
        }
        
        logger.debug(f"Calculated MACD - Line: {macd_line_value:.4f}, Signal: {signal_line_value:.4f}, Histogram: {histogram_value:.4f}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        return {"macd_line": None, "signal_line": None, "histogram": None}




def validate_price_data(prices: List[float]) -> bool:
    """
    Validate price data for technical indicator calculations.
    
    Args:
        prices: List of price values to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not prices or not isinstance(prices, list):
        logger.error("Price data must be a non-empty list")
        return False
    
    if len(prices) == 0:
        logger.error("Price data list is empty")
        return False
    
    try:
        # Check if all values are numeric and positive
        for i, price in enumerate(prices):
            if not isinstance(price, (int, float)):
                logger.error(f"Non-numeric price at index {i}: {price}")
                return False
            if price <= 0:
                logger.error(f"Non-positive price at index {i}: {price}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating price data: {e}")
        return False




def extract_closing_prices(df) -> List[float]:
    """
    Extract closing prices from pandas DataFrame returned by nasdaq_api.get_historical_data().
    
    Args:
        df: pandas DataFrame with OHLCV data
        
    Returns:
        List of closing prices
    """
    try:
        if df is None or df.empty:
            logger.warning("Empty or None DataFrame provided")
            return []
        
        # yfinance DataFrames have 'Close' column
        if 'Close' not in df.columns:
            logger.error(f"No 'Close' column found. Available columns: {list(df.columns)}")
            return []
        
        # Convert to list and handle any NaN values
        closing_prices = df['Close'].dropna().tolist()
        
        if not closing_prices:
            logger.warning("No valid closing prices found after removing NaN values")
            return []
        
        logger.debug(f"Extracted {len(closing_prices)} closing prices")
        return closing_prices
        
    except Exception as e:
        logger.error(f"Error extracting closing prices: {e}")
        return []
