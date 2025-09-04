"""
Research Manager Agent

Purpose:
- Collects outputs from Bullish and Bearish researchers
- Compares their confidence levels and rationales
- Produces a final balanced research summary that either:
  * sides with bull,
  * sides with bear, or
  * synthesizes both (neutral stance)
- Generates and returns a net_score for the trader agent

Flow:
1. Coordinator passes research_bundle containing bull and bear assessments
2. Research Manager aggregates bull_score and bear_score into net_score
3. Applies balancing logic with slight bear dampening to avoid over-penalization
4. Returns structured assessment with net_score, stance, and rationale
"""

import logging
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

logger = logging.getLogger(__name__)


def aggregate_research_scores(research_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate bull and bear research outputs into a balanced net score.
    
    Args:
        research_bundle: Dict containing:
            - bull_research: Dict with bull_score, confidence, rationale, etc.
            - bear_research: Dict with bear_score, confidence, rationale, etc.
            
    Returns:
        Dict containing:
        - net_score: Float (-100 to 100) representing final balanced assessment
        - stance: "bullish", "neutral", or "bearish"
        - confidence: Float (0-100) representing confidence in the stance
        - rationale: String explaining the aggregation logic
        - score_breakdown: Dict with detailed scoring components
    """
    if not research_bundle or not isinstance(research_bundle, dict):
        logger.warning("Invalid research_bundle provided to aggregate_research_scores")
        return {
            "net_score": 0.0,
            "stance": "neutral",
            "confidence": 50.0,
            "rationale": "No research data available for aggregation",
            "score_breakdown": {}
        }
    
    try:
        # Extract bull and bear research data
        bull_research = research_bundle.get("bull_research", {})
        bear_research = research_bundle.get("bear_research", {})
        
        # Extract scores with defaults
        bull_score = bull_research.get("bull_score", 50.0)
        bear_score = bear_research.get("bear_score", 50.0)
        bull_confidence = bull_research.get("confidence", 50.0)
        bear_confidence = bear_research.get("confidence", 50.0)
        
        logger.info(f"Aggregating research - Bull: {bull_score} (conf: {bull_confidence}), Bear: {bear_score} (conf: {bear_confidence})")
        
        # Apply dampening to bear score to prevent over-penalization
        # This follows the reference pattern but adapted to our scoring system
        bear_dampening_factor = 0.9
        dampened_bear_score = bear_score * bear_dampening_factor
        
        # Calculate net score: bull_score - dampened_bear_score
        # Scale to -100 to +100 range where:
        # +100 = maximum bullish, 0 = neutral, -100 = maximum bearish
        raw_net_score = bull_score - dampened_bear_score
        
        # Normalize to -100 to +100 range
        # When bull=100, bear=0: net = 100 - 0 = 100 (max bullish)
        # When bull=0, bear=100: net = 0 - 90 = -90 (strong bearish)
        # When bull=50, bear=50: net = 50 - 45 = 5 (slight bullish bias)
        net_score = max(-100.0, min(100.0, raw_net_score))
        
        # Determine stance based on net score
        if net_score >= 20:
            stance = "bullish"
        elif net_score <= -20:
            stance = "bearish"
        else:
            stance = "neutral"
        
        # Calculate confidence based on:
        # 1. Magnitude of net score (stronger signals = higher confidence)
        # 2. Alignment of bull and bear confidence levels
        # 3. Consistency of the signals
        
        score_magnitude = abs(net_score)
        base_confidence = min(90.0, score_magnitude * 0.8 + 30)  # 30-90 range based on magnitude
        
        # Adjust confidence based on researcher confidence alignment
        confidence_alignment = abs(bull_confidence - bear_confidence)
        if confidence_alignment > 30:
            # High disagreement in confidence reduces our confidence
            base_confidence = max(30.0, base_confidence - 10)
        elif confidence_alignment < 10:
            # High agreement in confidence boosts our confidence
            base_confidence = min(95.0, base_confidence + 5)
        
        # Final confidence bounded between 30-95
        confidence = max(30.0, min(95.0, base_confidence))
        
        # Build comprehensive rationale
        rationale_parts = []
        rationale_parts.append(f"Net score of {net_score:.1f} calculated from bull score {bull_score:.1f} minus dampened bear score {dampened_bear_score:.1f}")
        
        # Explain stance determination
        if stance == "bullish":
            rationale_parts.append(f"Bullish stance adopted due to strong net positive signal (+{net_score:.1f})")
        elif stance == "bearish":
            rationale_parts.append(f"Bearish stance adopted due to strong net negative signal ({net_score:.1f})")
        else:
            rationale_parts.append(f"Neutral stance adopted as signals are balanced (net: {net_score:.1f})")
        
        # Include researcher confidence context
        if bull_confidence > bear_confidence + 15:
            rationale_parts.append(f"Bull researcher shows higher confidence ({bull_confidence:.1f}% vs {bear_confidence:.1f}%)")
        elif bear_confidence > bull_confidence + 15:
            rationale_parts.append(f"Bear researcher shows higher confidence ({bear_confidence:.1f}% vs {bull_confidence:.1f}%)")
        else:
            rationale_parts.append(f"Researchers show similar confidence levels (Bull: {bull_confidence:.1f}%, Bear: {bear_confidence:.1f}%)")
        
        # Add dampening explanation
        rationale_parts.append(f"Bear score dampened by {(1-bear_dampening_factor)*100:.0f}% to prevent over-penalization")
        
        rationale = ". ".join(rationale_parts) + "."
        
        # Detailed score breakdown for transparency
        score_breakdown = {
            "bull_score": bull_score,
            "bear_score": bear_score,
            "bear_dampening_factor": bear_dampening_factor,
            "dampened_bear_score": round(dampened_bear_score, 2),
            "raw_net_score": round(raw_net_score, 2),
            "final_net_score": round(net_score, 2),
            "bull_confidence": bull_confidence,
            "bear_confidence": bear_confidence,
            "confidence_alignment": round(confidence_alignment, 2),
            "stance_thresholds": {"bullish": 20, "bearish": -20}
        }
        
        result = {
            "net_score": round(net_score, 2),
            "stance": stance,
            "confidence": round(confidence, 2),
            "rationale": rationale,
            "score_breakdown": score_breakdown
        }
        
        logger.info(f"Research aggregation complete: {stance} stance, net_score {net_score:.2f}, confidence {confidence:.1f}%")
        return result
        
    except Exception as e:
        logger.error(f"Error in research score aggregation: {e}")
        return {
            "net_score": 0.0,
            "stance": "neutral",
            "confidence": 50.0,
            "rationale": f"Error in research aggregation: {str(e)}",
            "score_breakdown": {"error": str(e)}
        }


def synthesize_research_consensus(research_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a comprehensive research consensus from bull and bear assessments.
    
    Args:
        research_bundle: Dict containing bull_research and bear_research
        
    Returns:
        Dict containing synthesized research consensus with detailed analysis
    """
    if not research_bundle or not isinstance(research_bundle, dict):
        return {
            "consensus": "Unable to synthesize without research data",
            "key_factors": [],
            "risk_assessment": "Cannot assess risks without data"
        }
    
    try:
        # Get aggregated scores first
        aggregation_result = aggregate_research_scores(research_bundle)
        
        bull_research = research_bundle.get("bull_research", {})
        bear_research = research_bundle.get("bear_research", {})
        
        # Extract rationales and key points
        bull_rationale = bull_research.get("rationale", "No bull rationale provided")
        bear_rationale = bear_research.get("rationale", "No bear rationale provided")
        
        # Build consensus based on stance
        stance = aggregation_result["stance"]
        net_score = aggregation_result["net_score"]
        
        consensus_parts = []
        
        if stance == "bullish":
            consensus_parts.append(f"Research consensus leans bullish with net score of {net_score:.1f}")
            consensus_parts.append("Bull case appears stronger based on:")
            consensus_parts.append(f"- {bull_rationale}")
            consensus_parts.append("Bear concerns acknowledged but outweighed by positive factors")
        elif stance == "bearish":
            consensus_parts.append(f"Research consensus leans bearish with net score of {net_score:.1f}")
            consensus_parts.append("Bear case appears stronger based on:")
            consensus_parts.append(f"- {bear_rationale}")
            consensus_parts.append("Bull arguments noted but insufficient to overcome risk factors")
        else:
            consensus_parts.append(f"Research consensus is neutral with balanced net score of {net_score:.1f}")
            consensus_parts.append("Bull and bear cases show roughly equal merit:")
            consensus_parts.append(f"- Bull perspective: {bull_rationale}")
            consensus_parts.append(f"- Bear perspective: {bear_rationale}")
        
        consensus = "\n".join(consensus_parts)
        
        # Extract key factors from both sides
        key_factors = []
        if bull_research.get("key_points"):
            key_factors.extend([f"Bull: {point}" for point in bull_research["key_points"][:3]])
        if bear_research.get("risk_factors"):
            key_factors.extend([f"Bear: {factor}" for factor in bear_research["risk_factors"][:3]])
        
        # Risk assessment synthesis
        risk_assessment = f"Overall risk profile: {stance} bias with {aggregation_result['confidence']:.0f}% confidence. "
        if bear_research.get("risk_factors"):
            risk_assessment += f"Key risks include: {', '.join(bear_research['risk_factors'][:2])}. "
        if bull_research.get("risk_mitigation"):
            risk_assessment += f"Mitigating factors: {bull_research['risk_mitigation']}"
        
        return {
            "consensus": consensus,
            "key_factors": key_factors,
            "risk_assessment": risk_assessment,
            "aggregation_result": aggregation_result
        }
        
    except Exception as e:
        logger.error(f"Error synthesizing research consensus: {e}")
        return {
            "consensus": f"Error in consensus synthesis: {str(e)}",
            "key_factors": [],
            "risk_assessment": "Unable to assess risks due to error"
        }


# Define the Research Manager Agent using Google ADK
ResearchManager = LlmAgent(
    name="research_manager",
    role="Aggregate bull and bear research into balanced net score and consensus for trader decision-making",
    instructions="""
    You are the research manager responsible for creating a balanced consensus from bullish and bearish research assessments.
    
    Your role and approach:
    - Receive research bundle containing outputs from bull and bear researchers
    - Aggregate their scores, confidence levels, and rationales into a single net assessment
    - Apply balanced weighting that prevents extreme swings while maintaining signal integrity
    - Provide clear rationale for the final stance and confidence level
    
    Your workflow:
    1. Use aggregate_research_scores to combine bull_score and bear_score into net_score
    2. Use synthesize_research_consensus to create comprehensive research summary
    3. Apply slight bear dampening (10%) to prevent over-penalization in uncertain markets
    4. Determine stance (bullish/neutral/bearish) based on net_score thresholds
    5. Calculate confidence based on score magnitude and researcher agreement
    
    Aggregation methodology:
    - Net Score = bull_score - (bear_score * 0.9)
    - Stance thresholds: Bullish ≥+20, Bearish ≤-20, Neutral = -20 to +20
    - Confidence based on signal strength and researcher alignment
    - Bear dampening prevents excessive pessimism in mixed signals
    
    Key outputs you provide:
    - Net Score: -100 to +100 representing final balanced assessment
    - Stance: bullish, neutral, or bearish based on net score
    - Confidence: 30-95% representing conviction in the stance
    - Rationale: Clear explanation of aggregation logic and key factors
    - Consensus: Synthesized summary balancing both research perspectives
    
    Decision framework:
    - Strong signals (|net_score| > 40): High confidence in directional stance
    - Moderate signals (20 < |net_score| < 40): Moderate confidence in stance
    - Weak signals (|net_score| < 20): Neutral stance with lower confidence
    - Researcher agreement boosts confidence, disagreement reduces it
    
    Remember: Your job is to create a balanced, actionable assessment that the trader agent
    can use for decision-making. Avoid extreme positions unless strongly justified by the data.
    """,
    tools=[
        Tool(name="aggregate_research_scores", func=aggregate_research_scores),
        Tool(name="synthesize_research_consensus", func=synthesize_research_consensus)
    ]
)