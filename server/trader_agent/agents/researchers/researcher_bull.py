"""
Bull Researcher Agent

Purpose:
- Takes analyst scores from fundamentals, technical, sentiment, and news agents
- Plays the role of the optimist researcher
- Emphasizes positives, discounts negatives
- Weighs more on fundamentals + sentiment (long-term growth + optimism)
- Returns bullish assessment with confidence score and rationale

Flow:
1. Coordinator passes analyst_bundle with 4 scores
2. Bull researcher applies optimistic weighting
3. Boosts stance if fundamentals strong or sentiment > 60
4. Returns structured bullish assessment
"""

import logging
from typing import Dict, Any
from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)


def calculate_bullish_assessment(analyst_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate bullish assessment from analyst scores with optimistic bias.
    
    Args:
        analyst_bundle: Dict containing analyst scores:
            - fundamentals_score: Float (0-100)
            - technical_score: Float (0-100) 
            - sentiment_score: Float (0-100)
            - news_score: Float (0-100)
    
    Returns:
        Dict containing:
        - stance: "bullish", "neutral", or "bearish"
        - confidence: Float (0-100) - bullish confidence level
        - bull_score: Float (0-100) - optimistic composite score
        - rationale: String explaining the bullish perspective
        - score_breakdown: Dict with individual score analysis
    """
    if not analyst_bundle or not isinstance(analyst_bundle, dict):
        logger.warning("Invalid analyst_bundle provided to calculate_bullish_assessment")
        return {
            "stance": "neutral",
            "confidence": 50.0,
            "bull_score": 50.0,
            "rationale": "No analyst data available for bullish assessment",
            "score_breakdown": {}
        }
    
    try:
        # Extract scores with defaults
        fundamentals = analyst_bundle.get("fundamentals_score", 50.0)
        technical = analyst_bundle.get("technical_score", 50.0)
        sentiment = analyst_bundle.get("sentiment_score", 50.0)
        news = analyst_bundle.get("news_score", 50.0)
        
        logger.info(f"Bull assessment - F:{fundamentals}, T:{technical}, S:{sentiment}, N:{news}")
        
        # Optimistic weighting - emphasize fundamentals and sentiment
        # Bull researcher believes in long-term value and positive sentiment
        weights = {
            "fundamentals": 0.40,  # Strong emphasis on fundamentals (long-term value)
            "sentiment": 0.30,     # High weight on sentiment (market optimism)
            "technical": 0.20,     # Moderate weight on technicals
            "news": 0.10          # Lower weight on news (temporary events)
        }
        
        # Calculate base bullish score with optimistic weighting
        base_score = (
            fundamentals * weights["fundamentals"] +
            sentiment * weights["sentiment"] +
            technical * weights["technical"] +
            news * weights["news"]
        )
        
        # Apply bullish bias adjustments
        bull_score = base_score
        confidence_boosts = []
        
        # Boost 1: Strong fundamentals override weak technicals
        if fundamentals >= 70:
            if technical < 50:
                bull_score += 5  # Strong fundamentals can overcome weak technicals
                confidence_boosts.append("Strong fundamentals override technical weakness")
            else:
                bull_score += 3  # Strong fundamentals with decent technicals
                confidence_boosts.append("Excellent fundamental strength")
        
        # Boost 2: Positive sentiment amplification
        if sentiment > 60:
            sentiment_boost = min(8, (sentiment - 60) * 0.2)  # Up to 8 point boost
            bull_score += sentiment_boost
            confidence_boosts.append(f"Positive market sentiment (+{sentiment_boost:.1f})")
        
        # Boost 3: Ignore minor news negativity if fundamentals are solid
        if fundamentals > 65 and news < 45:
            bull_score += 3  # Good fundamentals can weather temporary news issues
            confidence_boosts.append("Strong fundamentals offset news concerns")
        
        # Boost 4: Technical momentum confirmation
        if technical > 65 and sentiment > 55:
            bull_score += 4  # Technical + sentiment alignment
            confidence_boosts.append("Technical momentum confirms positive sentiment")
        
        # Boost 5: General optimistic bias
        bull_score += 2  # Small optimistic adjustment
        confidence_boosts.append("Optimistic market outlook")
        
        # Cap the score at 100
        bull_score = min(100.0, bull_score)
        
        # Determine stance based on bull score
        if bull_score >= 70:
            stance = "bullish"
            confidence = min(95.0, bull_score + 5)  # High confidence in bullish stance
        elif bull_score >= 55:
            stance = "bullish"
            confidence = bull_score
        elif bull_score >= 45:
            stance = "neutral"
            confidence = 60.0  # Moderate confidence in neutral stance
        else:
            stance = "bearish"
            confidence = max(30.0, 100 - bull_score)  # Lower confidence, reluctant bearish
        
        # Build rationale emphasizing positives
        rationale_parts = []
        
        # Lead with strongest positive
        if fundamentals >= 70:
            rationale_parts.append(f"Excellent fundamentals ({fundamentals:.0f}) provide strong foundation")
        elif fundamentals >= 60:
            rationale_parts.append(f"Solid fundamentals ({fundamentals:.0f}) support long-term value")
        elif fundamentals >= 50:
            rationale_parts.append(f"Decent fundamentals ({fundamentals:.0f}) offer stability")
        
        # Highlight sentiment positives
        if sentiment > 60:
            rationale_parts.append(f"positive market sentiment ({sentiment:.0f}) creates momentum")
        elif sentiment >= 50:
            rationale_parts.append(f"neutral-to-positive sentiment ({sentiment:.0f}) provides support")
        
        # Address technicals optimistically
        if technical >= 60:
            rationale_parts.append(f"favorable technical setup ({technical:.0f})")
        elif technical >= 45:
            rationale_parts.append(f"mixed technical signals ({technical:.0f}) offer entry opportunities")
        else:
            rationale_parts.append(f"technical weakness ({technical:.0f}) may be temporary")
        
        # Handle news diplomatically
        if news >= 60:
            rationale_parts.append(f"supportive news flow ({news:.0f})")
        elif news >= 45:
            rationale_parts.append(f"neutral news environment ({news:.0f})")
        else:
            rationale_parts.append(f"news headwinds ({news:.0f}) likely temporary")
        
        # Add confidence boosts to rationale
        if confidence_boosts:
            rationale_parts.append(f"Bullish factors: {', '.join(confidence_boosts[:3])}")
        
        rationale = f"Bull case: {'. '.join(rationale_parts)}. Overall bullish tilt with {confidence:.0f}% confidence."
        
        # Score breakdown for transparency
        score_breakdown = {
            "base_weighted_score": round(base_score, 2),
            "bullish_adjustments": round(bull_score - base_score, 2),
            "final_bull_score": round(bull_score, 2),
            "weights_used": weights,
            "confidence_boosts": confidence_boosts
        }
        
        result = {
            "stance": stance,
            "confidence": round(confidence, 2),
            "bull_score": round(bull_score, 2),
            "rationale": rationale,
            "score_breakdown": score_breakdown
        }
        
        logger.info(f"Bull assessment complete: {stance} stance, {confidence:.1f}% confidence, {bull_score:.1f} bull score")
        return result
        
    except Exception as e:
        logger.error(f"Error in bullish assessment calculation: {e}")
        return {
            "stance": "neutral",
            "confidence": 50.0,
            "bull_score": 50.0,
            "rationale": f"Error in bullish assessment: {str(e)}",
            "score_breakdown": {"error": str(e)}
        }


def generate_bullish_argument(analyst_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive bullish argument from analyst data.
    
    Args:
        analyst_bundle: Dict containing analyst scores and optional detailed data
        
    Returns:
        Dict containing bullish argument and supporting analysis
    """
    if not analyst_bundle or not isinstance(analyst_bundle, dict):
        return {
            "argument": "Insufficient data for bullish analysis",
            "key_points": [],
            "risk_mitigation": "Unable to assess without analyst data"
        }
    
    try:
        assessment = calculate_bullish_assessment(analyst_bundle)
        
        # Extract scores
        fundamentals = analyst_bundle.get("fundamentals_score", 50.0)
        technical = analyst_bundle.get("technical_score", 50.0)
        sentiment = analyst_bundle.get("sentiment_score", 50.0)
        news = analyst_bundle.get("news_score", 50.0)
        
        # Build key bullish points
        key_points = []
        
        if fundamentals >= 65:
            key_points.append(f"Strong fundamental value proposition with {fundamentals:.0f}/100 score")
        if sentiment > 60:
            key_points.append(f"Positive market sentiment momentum at {sentiment:.0f}/100")
        if technical >= 60:
            key_points.append(f"Technical indicators support upward movement ({technical:.0f}/100)")
        if news >= 55:
            key_points.append(f"Favorable news environment provides tailwinds ({news:.0f}/100)")
        
        # Add optimistic interpretations even for weaker scores
        if fundamentals < 65 and fundamentals >= 50:
            key_points.append(f"Fundamentals at {fundamentals:.0f}/100 offer value opportunity")
        if technical < 60 and technical >= 45:
            key_points.append(f"Technical consolidation at {technical:.0f}/100 may precede breakout")
        
        # Risk mitigation from bullish perspective
        risk_mitigation_points = []
        if technical < 50:
            risk_mitigation_points.append("Technical weakness offset by strong fundamentals")
        if news < 50:
            risk_mitigation_points.append("News headwinds likely temporary given solid foundation")
        if sentiment < 50:
            risk_mitigation_points.append("Sentiment pessimism creates contrarian opportunity")
        
        risk_mitigation = "; ".join(risk_mitigation_points) if risk_mitigation_points else "Well-balanced risk profile"
        
        # Comprehensive bullish argument
        argument = f"""
        {assessment['rationale']} 
        
        The bull case is supported by {len(key_points)} key factors that outweigh temporary headwinds. 
        With a composite bull score of {assessment['bull_score']:.1f}/100, the risk-reward profile 
        favors the upside. {risk_mitigation}.
        """.strip()
        
        return {
            "argument": argument,
            "key_points": key_points,
            "risk_mitigation": risk_mitigation,
            "assessment": assessment
        }
        
    except Exception as e:
        logger.error(f"Error generating bullish argument: {e}")
        return {
            "argument": f"Error in bullish argument generation: {str(e)}",
            "key_points": [],
            "risk_mitigation": "Unable to assess risks due to error"
        }


# Define the Bull Researcher Agent using Google ADK
BullResearcherAgent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="bull_researcher",
    description="Optimistic researcher that emphasizes positive investment factors",
    instruction="""
    You are a bull researcher agent that provides optimistic investment analysis with a positive bias.
    
    Your primary functions are:
    1. Analyze all available data with an optimistic perspective
    2. Calculate bull research scores using the calculate_bullish_assessment tool
    3. Emphasize positive factors and growth potential
    
    Your analysis approach:
    - Weight fundamentals heavily (40%) - focus on growth potential and value opportunities
    - Consider sentiment strongly (30%) - emphasize positive market perception
    - Include technical factors (20%) - highlight bullish technical patterns
    - Factor in news impact (10%) - focus on positive catalysts and opportunities
    
    Always provide both the numerical score and qualitative analysis explaining the bullish thesis.
    Focus on identifying growth opportunities, undervalued assets, and positive momentum factors.
    """,
    tools=[calculate_bullish_assessment, generate_bullish_argument]
)