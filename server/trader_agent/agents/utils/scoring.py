"""
Scoring Module

Converts raw signals (fundamental ratios, sentiment values, indicators) into normalized 0–100 scores.
Standardizes everything so higher layers (researcher/trader) don't need to understand raw data.

Functions:
- fundamentals_score(company_data: dict) -> float
- technical_score(indicators: dict) -> float  
- sentiment_score(news_data: list[dict]) -> float
- news_score(news_data: list[dict]) -> float

Flow:
Analysts fetch raw data → Raw data passed to scoring.py → 
Example: PE ratio → fundamentals_score() → Example: RSI/MACD → technical_score() →
Returns normalized float (0–100) → Research agents consume these scores.
"""

import logging
from typing import List, Dict, Any, Optional
from .indicators import rsi, macd, sma, extract_closing_prices

logger = logging.getLogger(__name__)

# ---------- Sentiment Keywords ----------
POSITIVE_KEYWORDS = [
    "beat", "beats", "surge", "record", "raise", "upgraded", "profit", 
    "growth", "strong", "upgrade", "bullish", "outperform", "buy",
    "partnership", "deal", "contract", "expansion", "innovation"
]

NEGATIVE_KEYWORDS = [
    "miss", "drop", "downgrade", "lawsuit", "probe", "recession", 
    "weak", "cut", "recall", "layoff", "bearish", "underperform", 
    "sell", "decline", "loss", "bankruptcy", "investigation"
]

HIGH_IMPACT_POSITIVE = [
    "beat earnings", "contract win", "partnership", "acquisition", 
    "record revenue", "guidance raise", "dividend increase"
]

HIGH_IMPACT_NEGATIVE = [
    "guidance cut", "sec probe", "regulatory action", "recall", 
    "lawsuit filed", "earnings miss", "downgrade"
]


def _parse_numeric_value(value_str: str) -> float:
    """
    Parse numeric value from string, handling currency symbols and formatting.
    
    Args:
        value_str: String value that may contain $, commas, percentages
        
    Returns:
        Parsed float value or 0.0 if parsing fails
    """
    if not value_str or not isinstance(value_str, str):
        return 0.0
    
    try:
        # Remove common formatting characters
        cleaned = value_str.replace("$", "").replace(",", "").replace("%", "").strip()
        
        # Handle special cases like "N/A", "--", etc.
        if cleaned.lower() in ["n/a", "na", "--", "", "null"]:
            return 0.0
            
        return float(cleaned)
    except (ValueError, TypeError):
        logger.warning(f"Failed to parse numeric value: {value_str}")
        return 0.0


def _parse_market_cap(market_cap_str: str) -> float:
    """
    Parse market cap string and convert to numeric value in dollars.
    
    Args:
        market_cap_str: Market cap string (e.g., "$2.5T", "$150.2B", "$5.1M")
        
    Returns:
        Market cap in dollars
    """
    if not market_cap_str:
        return 0.0
    
    try:
        cleaned = market_cap_str.replace("$", "").replace(",", "").strip().upper()
        
        if cleaned.endswith("T"):
            return float(cleaned[:-1]) * 1e12
        elif cleaned.endswith("B"):
            return float(cleaned[:-1]) * 1e9
        elif cleaned.endswith("M"):
            return float(cleaned[:-1]) * 1e6
        elif cleaned.endswith("K"):
            return float(cleaned[:-1]) * 1e3
        else:
            return float(cleaned)
    except (ValueError, TypeError):
        logger.warning(f"Failed to parse market cap: {market_cap_str}")
        return 0.0


def fundamentals_score(company_data: Dict[str, Any]) -> float:
    """
    Convert company fundamental data into a normalized 0-100 score.
    
    Args:
        company_data: Normalized company data from nasdaq_api.get_company_data()
        
    Returns:
        Fundamentals score (0-100)
    """
    if not company_data or not isinstance(company_data, dict):
        logger.warning("Invalid or empty company data provided")
        return 50.0  # Neutral score for missing data
    
    score = 0.0
    
    try:
        # Market Cap scoring (0-25 points)
        market_cap = _parse_market_cap(company_data.get("market_cap", ""))
        if market_cap > 0:
            # Large cap (>$10B) = 25 pts, Mid cap ($2-10B) = 15-25 pts, Small cap (<$2B) = 5-15 pts
            if market_cap >= 10e9:
                score += 25
            elif market_cap >= 2e9:
                score += 15 + (market_cap - 2e9) / (8e9) * 10  # Scale between 15-25
            else:
                score += max(5, (market_cap / 2e9) * 15)  # Scale between 5-15
        
        # P/E Ratio scoring (0-20 points)
        pe_ratio = _parse_numeric_value(company_data.get("pe_ratio", ""))
        if pe_ratio > 0:
            # Optimal P/E range is 15-25, penalize extremes
            if 15 <= pe_ratio <= 25:
                score += 20
            elif 10 <= pe_ratio < 15 or 25 < pe_ratio <= 35:
                score += 15
            elif 5 <= pe_ratio < 10 or 35 < pe_ratio <= 50:
                score += 10
            else:
                score += 5  # Very high or very low P/E
        
        # Dividend Yield scoring (0-15 points)
        dividend_yield = _parse_numeric_value(company_data.get("dividend_yield", ""))
        if dividend_yield > 0:
            # Sweet spot is 2-6% yield
            if 2 <= dividend_yield <= 6:
                score += 15
            elif 1 <= dividend_yield < 2 or 6 < dividend_yield <= 8:
                score += 10
            elif dividend_yield > 8:
                score += 5  # Very high yield might indicate distress
            else:
                score += 3  # Low yield
        
        # Volume/Liquidity scoring (0-15 points)
        volume = _parse_numeric_value(company_data.get("volume", ""))
        avg_volume = _parse_numeric_value(company_data.get("avg_volume", ""))
        if volume > 0 and avg_volume > 0:
            volume_ratio = volume / avg_volume
            # Higher than average volume is generally positive
            if volume_ratio >= 1.5:
                score += 15
            elif volume_ratio >= 1.2:
                score += 12
            elif volume_ratio >= 0.8:
                score += 8
            else:
                score += 5  # Low volume
        
        # 52-week position scoring (0-25 points)
        current_price = _parse_numeric_value(company_data.get("price", ""))
        high_52week = _parse_numeric_value(company_data.get("high_52week", ""))
        low_52week = _parse_numeric_value(company_data.get("low_52week", ""))
        
        if current_price > 0 and high_52week > 0 and low_52week > 0 and high_52week > low_52week:
            # Calculate position within 52-week range
            position = (current_price - low_52week) / (high_52week - low_52week)
            # Higher position in range is generally better
            score += position * 25
        
        # Ensure score is within bounds
        final_score = max(0.0, min(100.0, score))
        
        logger.debug(f"Calculated fundamentals score: {final_score:.2f} for {company_data.get('symbol', 'unknown')}")
        return final_score
        
    except Exception as e:
        logger.error(f"Error calculating fundamentals score: {e}")
        return 50.0  # Return neutral score on error


def technical_score(indicators: Dict[str, Any]) -> float:
    """
    Convert technical indicators into a normalized 0-100 score.
    
    Args:
        indicators: Dict containing technical indicator values from indicators.py functions
        Expected keys: 'rsi', 'macd', 'sma_50', 'sma_200', 'closing_prices'
        
    Returns:
        Technical score (0-100)
    """
    if not indicators or not isinstance(indicators, dict):
        logger.warning("Invalid or empty indicators data provided")
        return 50.0  # Neutral score for missing data
    
    score = 50.0  # Start with neutral base
    
    try:
        # RSI scoring (±20 points)
        rsi_value = indicators.get("rsi")
        if rsi_value is not None:
            if rsi_value < 30:
                score += 20  # Oversold - bullish signal
            elif rsi_value > 70:
                score -= 20  # Overbought - bearish signal
            elif 40 <= rsi_value <= 60:
                score += 5   # Neutral zone - slight positive
            # No change for 30-40 and 60-70 ranges
        
        # MACD scoring (±15 points)
        macd_data = indicators.get("macd", {})
        if isinstance(macd_data, dict):
            macd_line = macd_data.get("macd_line")
            signal_line = macd_data.get("signal_line")
            histogram = macd_data.get("histogram")
            
            if macd_line is not None and signal_line is not None:
                if macd_line > signal_line:
                    score += 15  # MACD above signal - bullish
                else:
                    score -= 15  # MACD below signal - bearish
            
            # Additional histogram consideration
            if histogram is not None:
                if histogram > 0:
                    score += 5   # Positive momentum
                else:
                    score -= 5   # Negative momentum
        
        # Moving Average scoring (±15 points)
        sma_50 = indicators.get("sma_50")
        sma_200 = indicators.get("sma_200")
        current_price = indicators.get("current_price")
        
        if sma_50 is not None and sma_200 is not None:
            if sma_50 > sma_200:
                score += 15  # Golden cross - bullish
            else:
                score -= 15  # Death cross - bearish
        
        # Price vs SMA scoring (±10 points)
        if current_price is not None and sma_50 is not None:
            if current_price > sma_50:
                score += 10  # Price above SMA50 - bullish
            else:
                score -= 10  # Price below SMA50 - bearish
        
        # Ensure score is within bounds
        final_score = max(0.0, min(100.0, score))
        
        logger.debug(f"Calculated technical score: {final_score:.2f}")
        return final_score
        
    except Exception as e:
        logger.error(f"Error calculating technical score: {e}")
        return 50.0  # Return neutral score on error


def sentiment_score(news_data: List[Dict[str, Any]]) -> float:
    """
    Analyze news sentiment and convert to normalized 0-100 score.
    
    Args:
        news_data: List of news articles from nasdaq_api.get_news_data()
        
    Returns:
        Sentiment score (0-100)
    """
    if not news_data or not isinstance(news_data, list):
        logger.warning("Invalid or empty news data provided")
        return 50.0  # Neutral score for missing data
    
    if len(news_data) == 0:
        return 50.0
    
    try:
        positive_count = 0
        negative_count = 0
        
        for article in news_data:
            if not isinstance(article, dict):
                continue
                
            # Analyze title and summary
            title = (article.get("title", "") or "").lower()
            summary = (article.get("summary", "") or "").lower()
            text = f"{title} {summary}"
            
            # Count positive keywords
            for keyword in POSITIVE_KEYWORDS:
                if keyword in text:
                    positive_count += 1
            
            # Count negative keywords
            for keyword in NEGATIVE_KEYWORDS:
                if keyword in text:
                    negative_count += 1
        
        total_sentiment = positive_count + negative_count
        
        if total_sentiment == 0:
            return 50.0  # Neutral if no sentiment keywords found
        
        # Calculate sentiment ratio
        sentiment_ratio = positive_count / total_sentiment
        score = sentiment_ratio * 100
        
        logger.debug(f"Calculated sentiment score: {score:.2f} (pos: {positive_count}, neg: {negative_count})")
        return score
        
    except Exception as e:
        logger.error(f"Error calculating sentiment score: {e}")
        return 50.0


def news_score(news_data: List[Dict[str, Any]]) -> float:
    """
    Analyze news impact and convert to normalized 0-100 score.
    Focuses on high-impact events that could significantly affect stock price.
    
    Args:
        news_data: List of news articles from nasdaq_api.get_news_data()
        
    Returns:
        News impact score (0-100)
    """
    if not news_data or not isinstance(news_data, list):
        logger.warning("Invalid or empty news data provided")
        return 50.0  # Neutral score for missing data
    
    if len(news_data) == 0:
        return 50.0
    
    try:
        score = 50.0  # Start with neutral base
        
        for article in news_data:
            if not isinstance(article, dict):
                continue
                
            title = (article.get("title", "") or "").lower()
            summary = (article.get("summary", "") or "").lower()
            text = f"{title} {summary}"
            
            # Check for high-impact positive events
            for event in HIGH_IMPACT_POSITIVE:
                if event in text:
                    score += 10  # Significant positive impact
            
            # Check for high-impact negative events
            for event in HIGH_IMPACT_NEGATIVE:
                if event in text:
                    score -= 12  # Significant negative impact (slightly weighted more)
            
            # Check for general positive keywords (smaller impact)
            for keyword in POSITIVE_KEYWORDS:
                if keyword in text:
                    score += 2
            
            # Check for general negative keywords (smaller impact)
            for keyword in NEGATIVE_KEYWORDS:
                if keyword in text:
                    score -= 2
        
        # Ensure score is within bounds
        final_score = max(0.0, min(100.0, score))
        
        logger.debug(f"Calculated news impact score: {final_score:.2f}")
        return final_score
        
    except Exception as e:
        logger.error(f"Error calculating news score: {e}")
        return 50.0


def technical_score_from_prices(closing_prices: List[float]) -> float:
    """
    Calculate technical score directly from closing prices using indicators.
    
    Args:
        closing_prices: List of closing prices
        
    Returns:
        Technical score (0-100)
    """
    if not closing_prices or len(closing_prices) < 50:
        logger.warning("Insufficient price data for technical analysis")
        return 50.0
    
    try:
        # Calculate indicators
        rsi_value = rsi(closing_prices, 14)
        macd_data = macd(closing_prices, 12, 26, 9)
        sma_50_value = sma(closing_prices, 50)
        sma_200_value = sma(closing_prices, 200) if len(closing_prices) >= 200 else None
        current_price = closing_prices[-1] if closing_prices else None
        
        # Create indicators dict
        indicators = {
            "rsi": rsi_value,
            "macd": macd_data,
            "sma_50": sma_50_value,
            "sma_200": sma_200_value,
            "current_price": current_price
        }
        
        return technical_score(indicators)
        
    except Exception as e:
        logger.error(f"Error calculating technical score from prices: {e}")
        return 50.0


def composite_score(fundamentals: float, technical: float, sentiment: float, 
                   news: float, weights: Optional[Dict[str, float]] = None) -> float:
    """
    Calculate a weighted composite score from individual component scores.
    
    Args:
        fundamentals: Fundamentals score (0-100)
        technical: Technical score (0-100)
        sentiment: Sentiment score (0-100)
        news: News impact score (0-100)
        weights: Optional dict with weights for each component
        
    Returns:
        Composite score (0-100)
    """
    # Default weights
    default_weights = {
        "fundamentals": 0.4,
        "technical": 0.3,
        "sentiment": 0.15,
        "news": 0.15
    }
    
    if weights is None:
        weights = default_weights
    
    try:
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight == 0:
            logger.error("Total weight is zero, using default weights")
            weights = default_weights
            total_weight = 1.0
        
        normalized_weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate weighted score
        composite = (
            fundamentals * normalized_weights.get("fundamentals", 0.4) +
            technical * normalized_weights.get("technical", 0.3) +
            sentiment * normalized_weights.get("sentiment", 0.15) +
            news * normalized_weights.get("news", 0.15)
        )
        
        final_score = max(0.0, min(100.0, composite))
        
        logger.debug(f"Calculated composite score: {final_score:.2f}")
        return final_score
        
    except Exception as e:
        logger.error(f"Error calculating composite score: {e}")
        return 50.0