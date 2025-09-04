"""
Sentiment Agent

Purpose:
- Fetches recent news headlines/articles from NASDAQ API using get_news_data
- Uses a lexicon approach (positive/negative keywords) to measure tone
- Returns a sentiment score (0–100) using scoring.sentiment_score method

Flow:
1. Coordinator passes ticker → Sentiment Agent
2. Calls nasdaq_api.get_news_data(ticker)
3. Loops over titles/descriptions → counts sentiment keywords
4. Calls scoring.sentiment_score
5. Returns {articles, normalized_score}
"""

import logging
from typing import Dict, Any, List
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

# Import utility functions
from utils.nasdaq_api import get_news_data
from utils.scoring import sentiment_score

logger = logging.getLogger(__name__)


def fetch_news(ticker: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
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
        logger.error(f"Invalid ticker provided to fetch_news: {ticker}")
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


def calculate_sentiment(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate sentiment score from news articles using lexicon-based approach.
    
    Args:
        articles: List of news articles from nasdaq_api.get_news_data()
        
    Returns:
        Dict containing:
        - sentiment_score: Float score (0-100)
        - article_count: Number of articles analyzed
        - analysis: Breakdown of sentiment analysis
    """
    if not articles or not isinstance(articles, list):
        logger.warning("Invalid or empty articles data provided to calculate_sentiment")
        return {
            "sentiment_score": 50.0,
            "article_count": 0,
            "analysis": "No articles data available for sentiment analysis"
        }
    
    if len(articles) == 0:
        return {
            "sentiment_score": 50.0,
            "article_count": 0,
            "analysis": "No articles to analyze"
        }
    
    try:
        logger.info(f"Calculating sentiment for {len(articles)} articles")
        
        # Calculate the sentiment score using the scoring module
        score = sentiment_score(articles)
        
        # Build detailed analysis
        positive_count = 0
        negative_count = 0
        analyzed_articles = []
        
        # Import keywords from scoring module for analysis
        from utils.scoring import POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS
        
        for article in articles:
            if not isinstance(article, dict):
                continue
                
            title = (article.get("title", "") or "").lower()
            summary = (article.get("summary", "") or "").lower()
            text = f"{title} {summary}"
            
            article_positive = 0
            article_negative = 0
            
            # Count positive keywords in this article
            for keyword in POSITIVE_KEYWORDS:
                if keyword in text:
                    article_positive += 1
                    positive_count += 1
            
            # Count negative keywords in this article
            for keyword in NEGATIVE_KEYWORDS:
                if keyword in text:
                    article_negative += 1
                    negative_count += 1
            
            # Store article analysis
            if article_positive > 0 or article_negative > 0:
                sentiment_label = "Positive" if article_positive > article_negative else "Negative" if article_negative > article_positive else "Mixed"
                analyzed_articles.append({
                    "title": article.get("title", "")[:100] + "..." if len(article.get("title", "")) > 100 else article.get("title", ""),
                    "positive_keywords": article_positive,
                    "negative_keywords": article_negative,
                    "sentiment": sentiment_label
                })
        
        # Build analysis string
        total_sentiment_keywords = positive_count + negative_count
        analysis_parts = [
            f"Sentiment Analysis of {len(articles)} news articles:",
            f"- Total sentiment keywords found: {total_sentiment_keywords}",
            f"- Positive keywords: {positive_count}",
            f"- Negative keywords: {negative_count}",
            f"- Articles with sentiment signals: {len(analyzed_articles)}"
        ]
        
        if total_sentiment_keywords > 0:
            sentiment_ratio = positive_count / total_sentiment_keywords
            if sentiment_ratio > 0.6:
                overall_sentiment = "Predominantly Positive"
            elif sentiment_ratio < 0.4:
                overall_sentiment = "Predominantly Negative"
            else:
                overall_sentiment = "Mixed/Neutral"
            analysis_parts.append(f"- Overall sentiment: {overall_sentiment}")
        else:
            analysis_parts.append("- Overall sentiment: Neutral (no sentiment keywords found)")
        
        analysis_parts.append(f"- Sentiment Score: {score:.2f}/100")
        
        # Add top articles with sentiment
        if analyzed_articles:
            analysis_parts.append("\nTop articles with sentiment signals:")
            for i, article_info in enumerate(analyzed_articles[:3], 1):
                analysis_parts.append(f"{i}. {article_info['title']} - {article_info['sentiment']} (P:{article_info['positive_keywords']}, N:{article_info['negative_keywords']})")
        
        analysis = "\n".join(analysis_parts)
        
        result = {
            "sentiment_score": score,
            "article_count": len(articles),
            "positive_keywords_count": positive_count,
            "negative_keywords_count": negative_count,
            "articles_with_sentiment": len(analyzed_articles),
            "analysis": analysis
        }
        
        logger.info(f"Calculated sentiment score: {score:.2f} from {len(articles)} articles")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating sentiment: {e}")
        return {
            "sentiment_score": 50.0,
            "article_count": len(articles) if articles else 0,
            "analysis": f"Error in sentiment calculation: {str(e)}"
        }


def analyze_news_sentiment(ticker: str, limit: int = 10) -> Dict[str, Any]:
    """
    Complete workflow: fetch news and calculate sentiment for a ticker.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT")
        limit: Maximum number of articles to analyze (default: 10)
        
    Returns:
        Dict containing both news data and sentiment analysis
    """
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided to analyze_news_sentiment: {ticker}")
        return {
            "symbol": "",
            "sentiment_score": 50.0,
            "article_count": 0,
            "error": "Invalid ticker provided"
        }
    
    ticker = ticker.upper().strip()
    logger.info(f"Starting complete news sentiment analysis for {ticker}")
    
    try:
        # Step 1: Fetch news articles
        news_data = fetch_news(ticker, limit=limit)
        
        if "error" in news_data:
            return {
                "symbol": ticker,
                "sentiment_score": 50.0,
                "article_count": 0,
                "news_data": news_data,
                "error": f"Failed to fetch news: {news_data['error']}"
            }
        
        # Step 2: Calculate sentiment
        sentiment_data = calculate_sentiment(news_data["articles"])
        
        # Step 3: Combine results
        result = {
            "symbol": ticker,
            "sentiment_score": sentiment_data["sentiment_score"],
            "article_count": sentiment_data["article_count"],
            "positive_keywords_count": sentiment_data.get("positive_keywords_count", 0),
            "negative_keywords_count": sentiment_data.get("negative_keywords_count", 0),
            "articles_with_sentiment": sentiment_data.get("articles_with_sentiment", 0),
            "news_data": news_data,
            "sentiment_analysis": sentiment_data["analysis"]
        }
        
        logger.info(f"Completed sentiment analysis for {ticker}: score={sentiment_data['sentiment_score']:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"Error in complete sentiment analysis for {ticker}: {e}")
        return {
            "symbol": ticker,
            "sentiment_score": 50.0,
            "article_count": 0,
            "error": f"Error in sentiment analysis: {str(e)}"
        }


# Define the Sentiment Agent using Google ADK
SentimentAgent = LlmAgent(
    name="sentiment_analyst",
    role="Analyze news sentiment and compute sentiment-based scores for stock analysis",
    instructions="""
    You are a sentiment analyst responsible for evaluating market sentiment through news analysis.
    
    Your workflow:
    1. When given a stock ticker, use fetch_news to get recent news articles from NASDAQ API
    2. Use calculate_sentiment to analyze the sentiment of news articles using lexicon-based approach
    3. Use analyze_news_sentiment for a complete end-to-end analysis combining both steps
    4. Provide clear analysis explaining the sentiment signals and their market implications
    
    Sentiment analysis approach:
    - Uses lexicon-based method with positive and negative keyword dictionaries
    - Analyzes both article titles and summaries for sentiment keywords
    - Counts positive vs negative sentiment indicators
    - Normalizes results to 0-100 scale where:
      * 0-30: Predominantly negative sentiment
      * 30-70: Mixed/neutral sentiment  
      * 70-100: Predominantly positive sentiment
    
    Key sentiment indicators you track:
    - Positive keywords: "beat", "surge", "record", "growth", "upgrade", "bullish", "partnership", etc.
    - Negative keywords: "miss", "drop", "downgrade", "lawsuit", "recession", "bearish", "decline", etc.
    - High-impact events: earnings beats/misses, guidance changes, regulatory actions, partnerships
    
    Market implications:
    - High positive sentiment (70+): Potential bullish momentum, increased buying interest
    - High negative sentiment (30-): Potential bearish pressure, selling sentiment
    - Neutral sentiment (30-70): Balanced market view, fundamentals likely driving price
    - Consider sentiment in context with technical and fundamental analysis
    
    Always provide both quantitative sentiment scores and qualitative analysis to help traders understand:
    - Overall market sentiment toward the stock
    - Key themes driving positive/negative sentiment
    - Potential impact on stock price movement
    - Number and quality of sentiment signals found
    
    Focus on identifying sentiment trends, news themes, and potential market-moving events.
    """,
    tools=[
        Tool(name="fetch_news", func=fetch_news),
        Tool(name="calculate_sentiment", func=calculate_sentiment),
        Tool(name="analyze_news_sentiment", func=analyze_news_sentiment)
    ]
)