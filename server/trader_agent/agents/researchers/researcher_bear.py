"""
Bear Researcher Agent

Purpose:
- Takes the 4 scores from analyst agents (fundamentals, sentiment, technical, news)
- Plays the role of the skeptic researcher focusing on risks, weaknesses, red flags
- Weighs technical + news more heavily (short-term threats)
- Penalizes negative sentiment strongly
- Discounts fundamentals slightly (assumes market may not care about intrinsic value short-term)
- Returns a bearish assessment with bear score and confidence

Flow:
1. Coordinator passes analyst bundle with the 4 scores
2. Bear Researcher processes scores with bearish bias
3. Returns structured bearish assessment with rationale
"""

import logging
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

logger = logging.getLogger(__name__)


def calculate_bearish_assessment(analyst_scores: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate bearish assessment from analyst scores with skeptical bias.
    
    Args:
        analyst_scores: Dict containing scores from all 4 analysts:
            - fundamental_score: Float (0-100)
            - sentiment_score: Float (0-100) 
            - technical_score: Float (0-100)
            - news_score: Float (0-100)
            
    Returns:
        Dict containing:
        - stance: "bearish"
        - confidence: Float (0-100) representing bearish confidence
        - bear_score: Float (0-100) representing overall bearish assessment
        - rationale: String explaining the bearish case
        - risk_factors: List of identified risk factors
    """
    if not analyst_scores or not isinstance(analyst_scores, dict):
        logger.warning("Invalid or empty analyst scores provided to calculate_bearish_assessment")
        return {
            "stance": "bearish",
            "confidence": 50.0,
            "bear_score": 50.0,
            "rationale": "No analyst data available for bearish assessment",
            "risk_factors": ["Insufficient data for analysis"]
        }
    
    try:
        # Extract scores with defaults
        fundamental_score = analyst_scores.get("fundamental_score", 50.0)
        sentiment_score = analyst_scores.get("sentiment_score", 50.0)
        technical_score = analyst_scores.get("technical_score", 50.0)
        news_score = analyst_scores.get("news_score", 50.0)
        
        logger.info(f"Calculating bearish assessment from scores: F={fundamental_score}, S={sentiment_score}, T={technical_score}, N={news_score}")
        
        # Bearish weighting strategy:
        # - Technical (35%): Short-term price action threats
        # - News (30%): Event-driven risks and negative catalysts
        # - Sentiment (25%): Market psychology and fear indicators
        # - Fundamentals (10%): Discounted as market may ignore intrinsic value short-term
        
        # Convert scores to bearish perspective (invert them)
        bearish_technical = 100 - technical_score
        bearish_news = 100 - news_score
        bearish_sentiment = 100 - sentiment_score
        bearish_fundamental = 100 - fundamental_score
        
        # Apply bearish weights
        weighted_bear_score = (
            0.35 * bearish_technical +      # Heavy weight on technical weakness
            0.30 * bearish_news +           # Heavy weight on negative news
            0.25 * bearish_sentiment +      # Strong penalty for negative sentiment
            0.10 * bearish_fundamental      # Light weight on fundamental weakness
        )
        
        # Ensure score is within bounds
        bear_score = max(0.0, min(100.0, weighted_bear_score))
        
        # Calculate confidence based on score consistency and extremes
        score_variance = [bearish_technical, bearish_news, bearish_sentiment, bearish_fundamental]
        avg_score = sum(score_variance) / len(score_variance)
        variance = sum((x - avg_score) ** 2 for x in score_variance) / len(score_variance)
        
        # Higher confidence when scores are consistently bearish or when key indicators are very bearish
        base_confidence = bear_score
        
        # Boost confidence for extreme bearish signals in key areas
        if bearish_technical > 70 or bearish_news > 70:
            base_confidence = min(100.0, base_confidence + 15)
        
        # Boost confidence when sentiment is very negative
        if bearish_sentiment > 80:
            base_confidence = min(100.0, base_confidence + 10)
        
        # Reduce confidence if scores are inconsistent (high variance)
        if variance > 400:  # High variance threshold
            base_confidence = max(0.0, base_confidence - 10)
        
        confidence = max(0.0, min(100.0, base_confidence))
        
        # Identify specific risk factors
        risk_factors = []
        
        if technical_score < 30:
            risk_factors.append("Weak technical indicators suggest downward price momentum")
        if news_score < 40:
            risk_factors.append("Negative news events creating headwinds")
        if sentiment_score < 35:
            risk_factors.append("Poor market sentiment indicating selling pressure")
        if fundamental_score < 45:
            risk_factors.append("Fundamental weaknesses may not support current valuation")
        
        # Additional risk factors based on score combinations
        if technical_score < 40 and news_score < 40:
            risk_factors.append("Combined technical weakness and negative news create high risk environment")
        if sentiment_score < 30 and news_score < 35:
            risk_factors.append("Negative sentiment amplified by poor news coverage")
        
        if not risk_factors:
            risk_factors.append("Market conditions appear relatively stable")
        
        # Build rationale
        rationale_parts = []
        rationale_parts.append(f"Bear case analysis reveals {bear_score:.1f}/100 bearish conviction.")
        
        if bear_score > 70:
            rationale_parts.append("Strong bearish signals across multiple indicators.")
        elif bear_score > 50:
            rationale_parts.append("Moderate bearish tilt with concerning signals.")
        else:
            rationale_parts.append("Limited bearish conviction, but risks remain.")
        
        # Highlight key concerns
        key_concerns = []
        if bearish_technical > 60:
            key_concerns.append(f"technical weakness ({technical_score:.1f})")
        if bearish_news > 60:
            key_concerns.append(f"negative news impact ({news_score:.1f})")
        if bearish_sentiment > 70:
            key_concerns.append(f"poor sentiment ({sentiment_score:.1f})")
        
        if key_concerns:
            rationale_parts.append(f"Primary concerns: {', '.join(key_concerns)}.")
        
        # Market timing perspective
        if bearish_technical > 50 and bearish_news > 50:
            rationale_parts.append("Short-term outlook appears challenging with technical and news headwinds.")
        
        if bearish_sentiment > 60:
            rationale_parts.append("Market psychology suggests potential for further downside.")
        
        rationale = " ".join(rationale_parts)
        
        result = {
            "stance": "bearish",
            "confidence": round(confidence, 1),
            "bear_score": round(bear_score, 1),
            "rationale": rationale,
            "risk_factors": risk_factors,
            "score_breakdown": {
                "technical_weight": 35,
                "news_weight": 30,
                "sentiment_weight": 25,
                "fundamental_weight": 10,
                "weighted_components": {
                    "technical": round(0.35 * bearish_technical, 1),
                    "news": round(0.30 * bearish_news, 1),
                    "sentiment": round(0.25 * bearish_sentiment, 1),
                    "fundamental": round(0.10 * bearish_fundamental, 1)
                }
            }
        }
        
        logger.info(f"Calculated bearish assessment: score={bear_score:.1f}, confidence={confidence:.1f}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating bearish assessment: {e}")
        return {
            "stance": "bearish",
            "confidence": 50.0,
            "bear_score": 50.0,
            "rationale": f"Error in bearish analysis: {str(e)}",
            "risk_factors": ["Analysis error occurred"]
        }


def analyze_bearish_scenario(analyst_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete bearish analysis workflow from analyst bundle.
    
    Args:
        analyst_bundle: Dict containing results from all analyst agents
        
    Returns:
        Dict containing comprehensive bearish assessment
    """
    if not analyst_bundle or not isinstance(analyst_bundle, dict):
        logger.error("Invalid analyst bundle provided to analyze_bearish_scenario")
        return {
            "stance": "bearish",
            "confidence": 50.0,
            "bear_score": 50.0,
            "error": "Invalid analyst bundle provided"
        }
    
    try:
        # Extract scores from analyst bundle
        analyst_scores = {}
        
        # Extract fundamental score
        fundamentals_data = analyst_bundle.get("fundamentals", {})
        if isinstance(fundamentals_data, dict):
            analyst_scores["fundamental_score"] = fundamentals_data.get("fundamental_score", 50.0)
        
        # Extract sentiment score
        sentiment_data = analyst_bundle.get("sentiment", {})
        if isinstance(sentiment_data, dict):
            analyst_scores["sentiment_score"] = sentiment_data.get("sentiment_score", 50.0)
        
        # Extract technical score
        technical_data = analyst_bundle.get("technical", {})
        if isinstance(technical_data, dict):
            analyst_scores["technical_score"] = technical_data.get("technical_score", 50.0)
        
        # Extract news score
        news_data = analyst_bundle.get("news", {})
        if isinstance(news_data, dict):
            analyst_scores["news_score"] = news_data.get("news_score", 50.0)
        
        logger.info(f"Extracted analyst scores for bearish analysis: {analyst_scores}")
        
        # Calculate bearish assessment
        bearish_result = calculate_bearish_assessment(analyst_scores)
        
        # Add metadata
        bearish_result["analyst_bundle"] = analyst_bundle
        bearish_result["analysis_timestamp"] = analyst_bundle.get("timestamp")
        bearish_result["symbol"] = analyst_bundle.get("symbol", "Unknown")
        
        return bearish_result
        
    except Exception as e:
        logger.error(f"Error in bearish scenario analysis: {e}")
        return {
            "stance": "bearish",
            "confidence": 50.0,
            "bear_score": 50.0,
            "error": f"Error in bearish scenario analysis: {str(e)}"
        }


# Define the Bear Researcher Agent using Google ADK
ResearcherBear = LlmAgent(
    name="bear_researcher",
    role="Produce bearish assessment and risk analysis based on analyst signals with skeptical bias",
    instructions="""
    You are a bear researcher responsible for providing skeptical, risk-focused analysis of stocks.
    
    Your role and approach:
    - Act as the skeptic in the analysis process
    - Focus on risks, weaknesses, and red flags
    - Challenge overly optimistic assessments
    - Emphasize short-term threats and market psychology
    
    Your workflow:
    1. Receive analyst bundle containing scores from 4 analyst agents (fundamentals, sentiment, technical, news)
    2. Use calculate_bearish_assessment to process scores with bearish bias
    3. Use analyze_bearish_scenario for complete end-to-end bearish analysis
    4. Provide clear risk-focused rationale and specific risk factors
    
    Bearish analysis methodology:
    - Weight technical analysis heavily (35%) - focus on price action weakness and momentum breakdown
    - Weight news impact heavily (30%) - emphasize negative catalysts and event risks
    - Weight sentiment strongly (25%) - penalize negative market psychology heavily
    - Discount fundamentals (10%) - assume market may ignore intrinsic value in short-term
    
    Key risk factors you emphasize:
    - Technical breakdown: bearish chart patterns, momentum loss, support breaks
    - Negative news catalysts: earnings misses, regulatory issues, management problems
    - Poor sentiment: selling pressure, analyst downgrades, institutional outflows
    - Market timing risks: macro headwinds, sector rotation, liquidity concerns
    
    Assessment framework:
    - Bear Score 70-100: Strong bearish conviction, multiple risk factors aligned
    - Bear Score 50-70: Moderate bearish tilt, some concerning signals
    - Bear Score 0-50: Limited bearish case, but remain vigilant for risks
    
    Always provide:
    - Clear bearish stance with confidence level
    - Specific risk factors and their potential impact
    - Rationale explaining why bearish view is justified
    - Focus on what could go wrong rather than what might go right
    
    Remember: Your job is to be the voice of caution and identify potential downside scenarios
    that other analysts might miss or underweight. Challenge bullish assumptions and highlight
    risks that could lead to poor investment outcomes.
    """,
    tools=[
        Tool(name="calculate_bearish_assessment", func=calculate_bearish_assessment),
        Tool(name="analyze_bearish_scenario", func=analyze_bearish_scenario)
    ]
)