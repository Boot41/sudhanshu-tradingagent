"""
News Agent

Purpose:
- Fetches recent news headlines/articles from NASDAQ API using get_news_data
- Focuses on event/macro analysis rather than sentiment
- Detects big events: lawsuits, mergers, product launches, regulatory issues
- Produces a news impact score separate from sentiment using scoring.news_score method

Flow:
1. Coordinator passes ticker → News Agent
2. Calls nasdaq_api.get_news_data(ticker)
3. Analyzes articles for high-impact events and macro factors
4. Calls scoring.news_score for impact scoring
5. Returns {articles, news_impact_score, event_analysis}
"""

import logging
from typing import Dict, Any, List
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

# Import utility functions
from utils.nasdaq_api import get_news_data
from utils.scoring import news_score

logger = logging.getLogger(__name__)


def fetch_news_data(ticker: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """
    Fetch recent news articles for a given stock ticker from NASDAQ API.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        limit: Maximum number of articles to fetch (default: 10)
        offset: Offset for pagination (default: 0)
        
    Returns:
        Dict containing:
        - symbol: Stock ticker
        - articles: List of news articles
        - article_count: Number of articles retrieved
        - limit: Limit used for the request
        - offset: Offset used for the request
    """
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided to fetch_news_data: {ticker}")
        return {
            "symbol": "",
            "articles": [],
            "article_count": 0,
            "limit": limit,
            "offset": offset,
            "error": "Invalid ticker provided"
        }
    
    ticker = ticker.upper().strip()
    logger.info(f"Fetching news for ticker: {ticker}, limit: {limit}, offset: {offset}")
    
    try:
        # Get news data from NASDAQ API
        articles = get_news_data(ticker, limit=limit, offset=offset)
        
        if not articles:
            logger.warning(f"No news articles returned for ticker: {ticker}")
            return {
                "symbol": ticker,
                "articles": [],
                "article_count": 0,
                "limit": limit,
                "offset": offset,
                "error": "No news articles available"
            }
        
        result = {
            "symbol": ticker,
            "articles": articles,
            "article_count": len(articles),
            "limit": limit,
            "offset": offset
        }
        
        logger.info(f"Successfully fetched {len(articles)} news articles for {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching news for {ticker}: {e}")
        return {
            "symbol": ticker,
            "articles": [],
            "article_count": 0,
            "limit": limit,
            "offset": offset,
            "error": f"Error fetching news: {str(e)}"
        }


def calculate_news_impact(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate news impact score from articles focusing on high-impact events.
    
    Args:
        articles: List of news articles from nasdaq_api.get_news_data()
        
    Returns:
        Dict containing:
        - news_score: Float score (0-100)
        - article_count: Number of articles analyzed
        - event_analysis: Breakdown of events detected
        - high_impact_events: List of detected high-impact events
    """
    if not articles or not isinstance(articles, list):
        logger.warning("Invalid or empty articles data provided to calculate_news_impact")
        return {
            "news_score": 50.0,
            "article_count": 0,
            "event_analysis": "No articles data available for news impact analysis",
            "high_impact_events": []
        }
    
    if len(articles) == 0:
        return {
            "news_score": 50.0,
            "article_count": 0,
            "event_analysis": "No articles to analyze",
            "high_impact_events": []
        }
    
    try:
        logger.info(f"Calculating news impact for {len(articles)} articles")
        
        # Calculate the news impact score using the scoring module
        score = news_score(articles)
        
        # Analyze for high-impact events
        high_impact_events = []
        event_categories = {
            "earnings": ["earnings", "beat", "miss", "guidance", "revenue", "profit"],
            "regulatory": ["sec", "fda", "regulatory", "investigation", "probe", "lawsuit", "settlement"],
            "corporate": ["merger", "acquisition", "partnership", "deal", "contract", "spin-off"],
            "product": ["launch", "recall", "approval", "patent", "innovation", "breakthrough"],
            "management": ["ceo", "cfo", "executive", "resignation", "appointment", "leadership"],
            "financial": ["dividend", "buyback", "debt", "financing", "ipo", "bankruptcy"]
        }
        
        category_counts = {cat: 0 for cat in event_categories.keys()}
        
        # Import keywords from scoring module for detailed analysis
        from utils.scoring import HIGH_IMPACT_POSITIVE, HIGH_IMPACT_NEGATIVE
        
        for article in articles:
            if not isinstance(article, dict):
                continue
                
            title = (article.get("title", "") or "").lower()
            summary = (article.get("summary", "") or "").lower()
            text = f"{title} {summary}"
            
            # Check for high-impact events
            for event in HIGH_IMPACT_POSITIVE:
                if event in text:
                    high_impact_events.append({
                        "title": article.get("title", "")[:100] + "..." if len(article.get("title", "")) > 100 else article.get("title", ""),
                        "event_type": event,
                        "impact": "Positive",
                        "url": article.get("url", "")
                    })
            
            for event in HIGH_IMPACT_NEGATIVE:
                if event in text:
                    high_impact_events.append({
                        "title": article.get("title", "")[:100] + "..." if len(article.get("title", "")) > 100 else article.get("title", ""),
                        "event_type": event,
                        "impact": "Negative",
                        "url": article.get("url", "")
                    })
            
            # Categorize events
            for category, keywords in event_categories.items():
                for keyword in keywords:
                    if keyword in text:
                        category_counts[category] += 1
                        break
        
        # Build analysis string
        analysis_parts = [
            f"News Impact Analysis of {len(articles)} articles:",
            f"- News Impact Score: {score:.2f}/100",
            f"- High-impact events detected: {len(high_impact_events)}"
        ]
        
        # Add event category breakdown
        active_categories = {k: v for k, v in category_counts.items() if v > 0}
        if active_categories:
            analysis_parts.append("- Event categories detected:")
            for category, count in active_categories.items():
                analysis_parts.append(f"  * {category.title()}: {count} articles")
        else:
            analysis_parts.append("- No specific event categories detected")
        
        # Add interpretation
        if score > 70:
            interpretation = "Strong positive news impact - significant bullish events detected"
        elif score > 60:
            interpretation = "Moderate positive news impact - some positive developments"
        elif score < 30:
            interpretation = "Strong negative news impact - significant bearish events detected"
        elif score < 40:
            interpretation = "Moderate negative news impact - some concerning developments"
        else:
            interpretation = "Neutral news impact - balanced or routine news coverage"
        
        analysis_parts.append(f"- Impact Assessment: {interpretation}")
        
        # Add top high-impact events
        if high_impact_events:
            analysis_parts.append("\nTop high-impact events:")
            for i, event in enumerate(high_impact_events[:3], 1):
                analysis_parts.append(f"{i}. {event['title']} - {event['impact']} ({event['event_type']})")
        
        analysis = "\n".join(analysis_parts)
        
        result = {
            "news_score": score,
            "article_count": len(articles),
            "high_impact_events": high_impact_events,
            "event_categories": category_counts,
            "event_analysis": analysis
        }
        
        logger.info(f"Calculated news impact score: {score:.2f} from {len(articles)} articles with {len(high_impact_events)} high-impact events")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating news impact: {e}")
        return {
            "news_score": 50.0,
            "article_count": len(articles) if articles else 0,
            "event_analysis": f"Error in news impact calculation: {str(e)}",
            "high_impact_events": []
        }


def analyze_news_events(ticker: str, limit: int = 10) -> Dict[str, Any]:
    """
    Complete workflow: fetch news and calculate impact score for a ticker.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        limit: Maximum number of articles to analyze (default: 10)
        
    Returns:
        Dict containing both news data and impact analysis
    """
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided to analyze_news_events: {ticker}")
        return {
            "symbol": "",
            "news_score": 50.0,
            "article_count": 0,
            "error": "Invalid ticker provided"
        }
    
    ticker = ticker.upper().strip()
    logger.info(f"Starting complete news event analysis for {ticker}")
    
    try:
        # Step 1: Fetch news articles
        news_data = fetch_news_data(ticker, limit=limit)
        
        if "error" in news_data:
            return {
                "symbol": ticker,
                "news_score": 50.0,
                "article_count": 0,
                "news_data": news_data,
                "error": f"Failed to fetch news: {news_data['error']}"
            }
        
        # Step 2: Calculate news impact
        impact_data = calculate_news_impact(news_data["articles"])
        
        # Step 3: Combine results
        result = {
            "symbol": ticker,
            "news_score": impact_data["news_score"],
            "article_count": impact_data["article_count"],
            "high_impact_events": impact_data.get("high_impact_events", []),
            "event_categories": impact_data.get("event_categories", {}),
            "news_data": news_data,
            "event_analysis": impact_data["event_analysis"]
        }
        
        logger.info(f"Completed news event analysis for {ticker}: score={impact_data['news_score']:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"Error in complete news event analysis for {ticker}: {e}")
        return {
            "symbol": ticker,
            "news_score": 50.0,
            "article_count": 0,
            "error": f"Error in news event analysis: {str(e)}"
        }


# Define the News Agent using Google ADK
NewsAgent = LlmAgent(
    name="news_analyst",
    role="Analyze news events and compute event-level impact scores for stock analysis",
    instructions="""
    You are a news analyst responsible for evaluating market-moving events through news analysis.
    
    Your workflow:
    1. When given a stock ticker, use fetch_news_data to get recent news articles from NASDAQ API
    2. Use calculate_news_impact to analyze articles for high-impact events and macro factors
    3. Use analyze_news_events for a complete end-to-end analysis combining both steps
    4. Focus on event-level risk assessment rather than sentiment analysis
    
    News impact analysis approach:
    - Detects big events: lawsuits, mergers, product launches, regulatory issues
    - Focuses on macro-level developments that could significantly impact stock price
    - Produces a news impact score separate from sentiment analysis
    - Categorizes events into: earnings, regulatory, corporate, product, management, financial
    - Normalizes results to 0-100 scale where:
      * 0-30: Strong negative impact events (lawsuits, regulatory issues, earnings misses)
      * 30-70: Neutral/routine news coverage
      * 70-100: Strong positive impact events (partnerships, product launches, earnings beats)
    
    Key event types you track:
    - High-impact positive: earnings beats, contract wins, partnerships, acquisitions, guidance raises
    - High-impact negative: guidance cuts, SEC probes, regulatory actions, recalls, lawsuits
    - Corporate events: mergers, acquisitions, spin-offs, management changes
    - Regulatory events: FDA approvals, SEC investigations, compliance issues
    - Product events: launches, recalls, patent approvals, innovations
    
    Market implications:
    - High positive impact (70+): Potential catalyst for price appreciation, increased institutional interest
    - High negative impact (30-): Potential headwinds, regulatory overhang, operational challenges
    - Neutral impact (30-70): Business as usual, fundamentals likely primary driver
    - Consider event timing, magnitude, and potential duration of impact
    
    Always provide both quantitative impact scores and qualitative event analysis to help traders understand:
    - Key events that could move the stock price
    - Event categories and their relative importance
    - Potential timeline and magnitude of impact
    - Distinction between temporary events vs. structural changes
    
    Focus on identifying market-moving events, regulatory developments, and macro factors that could 
    significantly impact the company's business operations and stock valuation.
    """,
    tools=[
        Tool(name="fetch_news_data", func=fetch_news_data),
        Tool(name="calculate_news_impact", func=calculate_news_impact),
        Tool(name="analyze_news_events", func=analyze_news_events)
    ]
)