"""
Trader Agent

Purpose:
- Consumes Research Manager's consensus output (net_score, stance, confidence, score_breakdown)
- Translates research assessment into actionable trading decisions: BUY, SELL, or HOLD
- Determines position sizing based on confidence and score magnitude
- Applies risk management rules and exposure limits
- Outputs structured trade recommendation for downstream execution systems

Flow:
1. Receives assessment from Research Manager with net_score (-100 to +100), stance, and confidence
2. Applies decision logic based on stance and confidence thresholds
3. Calculates position size using confidence and net_score magnitude
4. Applies risk management constraints (max 20% exposure, min confidence thresholds)
5. Returns structured trade recommendation with action, position_size, and rationale

Decision Logic:
- "bullish" stance + confidence >= 40% → BUY
- "bearish" stance + confidence >= 40% → SELL  
- "neutral" stance OR confidence < 40% → HOLD
- Position sizing scales with confidence and net_score magnitude
- Maximum 20% portfolio exposure per trade
"""

import logging
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

logger = logging.getLogger(__name__)


def make_trading_decision(assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Research Manager assessment into actionable trading decision.
    
    Args:
        assessment: Dict containing Research Manager output:
            - net_score: Float (-100 to 100) representing balanced assessment
            - stance: "bullish", "neutral", or "bearish"
            - confidence: Float (0-100) representing conviction level
            - rationale: String explaining the research consensus
            - score_breakdown: Dict with detailed scoring components
            
    Returns:
        Dict containing:
        - action: "BUY", "SELL", or "HOLD"
        - position_size: Float (0-20) representing % of portfolio to allocate
        - confidence: Float (0-100) from input assessment
        - stance: String from input assessment
        - net_score: Float from input assessment
        - rationale: String explaining the trading decision
        - risk_metrics: Dict with risk management details
    """
    if not assessment or not isinstance(assessment, dict):
        logger.warning("Invalid assessment provided to make_trading_decision")
        return {
            "action": "HOLD",
            "position_size": 0.0,
            "confidence": 0.0,
            "stance": "neutral",
            "net_score": 0.0,
            "rationale": "No valid assessment data provided. Holding position for safety.",
            "risk_metrics": {"reason": "invalid_input", "max_exposure": 20.0}
        }
    
    try:
        # Extract key metrics from assessment
        net_score = assessment.get("net_score", 0.0)
        stance = assessment.get("stance", "neutral")
        confidence = assessment.get("confidence", 0.0)
        research_rationale = assessment.get("rationale", "No rationale provided")
        
        logger.info(f"Processing trading decision - Stance: {stance}, Net Score: {net_score}, Confidence: {confidence}%")
        
        # Risk Management Rule 1: Minimum confidence threshold
        min_confidence_threshold = 40.0
        if confidence < min_confidence_threshold:
            return {
                "action": "HOLD",
                "position_size": 0.0,
                "confidence": confidence,
                "stance": stance,
                "net_score": net_score,
                "rationale": f"Confidence {confidence:.1f}% below minimum threshold of {min_confidence_threshold}%. Holding position to avoid low-conviction trades.",
                "risk_metrics": {
                    "reason": "low_confidence",
                    "threshold": min_confidence_threshold,
                    "actual_confidence": confidence,
                    "max_exposure": 20.0
                }
            }
        
        # Decision Logic: Determine base action from stance
        if stance == "bullish":
            base_action = "BUY"
        elif stance == "bearish":
            base_action = "SELL"
        else:  # neutral
            base_action = "HOLD"
        
        # Position Sizing Calculation
        position_size = 0.0
        
        if base_action != "HOLD":
            # Base position from normalized net_score magnitude
            # net_score range: -100 to +100, normalize to 0-1
            score_magnitude = abs(net_score) / 100.0
            
            # Confidence factor (40-100% maps to 0.4-1.0)
            confidence_factor = confidence / 100.0
            
            # Combined sizing factor
            sizing_factor = score_magnitude * confidence_factor
            
            # Maximum exposure per trade: 20% of portfolio
            max_exposure = 20.0
            position_size = sizing_factor * max_exposure
            
            # Ensure position size is within bounds
            position_size = max(0.0, min(max_exposure, position_size))
            
            # Additional risk check: Very small positions become HOLD
            if position_size < 1.0:  # Less than 1% allocation
                base_action = "HOLD"
                position_size = 0.0
        
        # Build comprehensive rationale
        rationale_parts = []
        
        if base_action == "BUY":
            rationale_parts.append(f"BUY signal generated from bullish stance with {confidence:.1f}% confidence")
            rationale_parts.append(f"Position size: {position_size:.1f}% of portfolio based on net score {net_score:.1f} and confidence level")
        elif base_action == "SELL":
            rationale_parts.append(f"SELL signal generated from bearish stance with {confidence:.1f}% confidence")
            rationale_parts.append(f"Position size: {position_size:.1f}% of portfolio based on net score magnitude {abs(net_score):.1f} and confidence level")
        else:
            if stance == "neutral":
                rationale_parts.append(f"HOLD decision due to neutral stance (net score: {net_score:.1f})")
            else:
                rationale_parts.append(f"HOLD decision despite {stance} stance due to insufficient position size or risk constraints")
        
        # Add research context
        rationale_parts.append(f"Research basis: {research_rationale}")
        
        # Risk management summary
        risk_metrics = {
            "max_exposure_limit": 20.0,
            "actual_exposure": position_size,
            "confidence_threshold": min_confidence_threshold,
            "score_magnitude": abs(net_score),
            "sizing_factor": sizing_factor if base_action != "HOLD" else 0.0,
            "risk_adjusted": True
        }
        
        if position_size > 0:
            rationale_parts.append(f"Risk management: Position capped at {max_exposure}% maximum exposure")
        
        rationale = ". ".join(rationale_parts) + "."
        
        result = {
            "action": base_action,
            "position_size": round(position_size, 2),
            "confidence": confidence,
            "stance": stance,
            "net_score": net_score,
            "rationale": rationale,
            "risk_metrics": risk_metrics
        }
        
        logger.info(f"Trading decision: {base_action} with {position_size:.1f}% position size")
        return result
        
    except Exception as e:
        logger.error(f"Error in trading decision making: {e}")
        return {
            "action": "HOLD",
            "position_size": 0.0,
            "confidence": 0.0,
            "stance": "neutral",
            "net_score": 0.0,
            "rationale": f"Error in decision processing: {str(e)}. Defaulting to HOLD for safety.",
            "risk_metrics": {"error": str(e), "max_exposure": 20.0}
        }


def validate_trade_parameters(trade_decision: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize trade decision parameters before execution.
    
    Args:
        trade_decision: Dict containing trade decision from make_trading_decision
        
    Returns:
        Dict with validation results and any adjustments made
    """
    if not trade_decision or not isinstance(trade_decision, dict):
        return {
            "valid": False,
            "errors": ["Invalid trade decision format"],
            "adjusted_decision": None
        }
    
    errors = []
    adjustments = []
    adjusted_decision = trade_decision.copy()
    
    try:
        # Validate action
        valid_actions = ["BUY", "SELL", "HOLD"]
        action = trade_decision.get("action", "HOLD")
        if action not in valid_actions:
            errors.append(f"Invalid action '{action}', must be one of {valid_actions}")
            adjusted_decision["action"] = "HOLD"
            adjustments.append("Action reset to HOLD due to invalid value")
        
        # Validate position size
        position_size = trade_decision.get("position_size", 0.0)
        if not isinstance(position_size, (int, float)):
            errors.append("Position size must be numeric")
            adjusted_decision["position_size"] = 0.0
            adjustments.append("Position size reset to 0.0")
        elif position_size < 0:
            errors.append("Position size cannot be negative")
            adjusted_decision["position_size"] = 0.0
            adjustments.append("Negative position size reset to 0.0")
        elif position_size > 20.0:
            errors.append(f"Position size {position_size}% exceeds maximum 20%")
            adjusted_decision["position_size"] = 20.0
            adjustments.append("Position size capped at 20% maximum")
        
        # Validate confidence
        confidence = trade_decision.get("confidence", 0.0)
        if not isinstance(confidence, (int, float)):
            errors.append("Confidence must be numeric")
            adjusted_decision["confidence"] = 0.0
        elif confidence < 0 or confidence > 100:
            errors.append(f"Confidence {confidence}% must be between 0-100%")
            adjusted_decision["confidence"] = max(0, min(100, confidence))
            adjustments.append("Confidence bounded to 0-100% range")
        
        # Consistency check: HOLD should have 0 position size
        if adjusted_decision["action"] == "HOLD" and adjusted_decision["position_size"] > 0:
            adjusted_decision["position_size"] = 0.0
            adjustments.append("Position size reset to 0 for HOLD action")
        
        # Consistency check: Non-zero position should not be HOLD
        if adjusted_decision["position_size"] > 0 and adjusted_decision["action"] == "HOLD":
            adjusted_decision["action"] = "BUY"  # Default to BUY for positive positions
            adjustments.append("Action changed from HOLD to BUY for non-zero position")
        
        validation_result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "adjustments": adjustments,
            "adjusted_decision": adjusted_decision
        }
        
        if adjustments:
            logger.warning(f"Trade decision adjustments made: {adjustments}")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating trade parameters: {e}")
        return {
            "valid": False,
            "errors": [f"Validation error: {str(e)}"],
            "adjusted_decision": {
                "action": "HOLD",
                "position_size": 0.0,
                "confidence": 0.0,
                "stance": "neutral",
                "net_score": 0.0,
                "rationale": "Error in validation, defaulting to safe HOLD position",
                "risk_metrics": {"validation_error": str(e)}
            }
        }


# Define the Trader Agent using Google ADK
TraderAgent = LlmAgent(
    name="trader_agent",
    role="Convert research consensus into actionable trading decisions with risk management",
    instructions="""
    You are the Trader Agent responsible for making final trading decisions based on research consensus.
    
    Your role and approach:
    - Receive assessment from Research Manager containing net_score, stance, confidence, and rationale
    - Apply systematic decision logic to determine BUY, SELL, or HOLD actions
    - Calculate appropriate position sizing based on conviction and risk parameters
    - Enforce strict risk management rules to protect capital
    - Provide clear rationale for all trading decisions
    
    Your decision framework:
    1. Confidence Threshold: Require minimum 40% confidence for any non-HOLD action
    2. Stance Translation: bullish→BUY, bearish→SELL, neutral→HOLD
    3. Position Sizing: Scale with confidence and net_score magnitude
    4. Risk Limits: Maximum 20% portfolio exposure per trade
    5. Minimum Position: Positions < 1% become HOLD to avoid over-trading
    
    Position sizing methodology:
    - Base Size = (|net_score| / 100) * (confidence / 100) * 20% max exposure
    - Higher confidence + stronger signals = larger positions
    - Lower confidence or weak signals = smaller positions or HOLD
    - Always respect maximum 20% exposure limit
    
    Risk management rules you must enforce:
    - Never exceed 20% portfolio allocation on any single trade
    - Reject signals with confidence below 40% (force HOLD)
    - Convert tiny positions (<1%) to HOLD to reduce transaction costs
    - Validate all parameters before finalizing decisions
    
    Your outputs must include:
    - Action: "BUY", "SELL", or "HOLD"
    - Position Size: 0-20% of portfolio allocation
    - Confidence: Pass-through from research assessment
    - Stance: Pass-through from research assessment  
    - Net Score: Pass-through from research assessment
    - Rationale: Clear explanation of decision logic and risk considerations
    - Risk Metrics: Detailed risk management information
    
    Decision examples:
    - Bullish stance, 80% confidence, net_score +60 → BUY with ~12% position
    - Bearish stance, 70% confidence, net_score -45 → SELL with ~6.3% position  
    - Neutral stance, 65% confidence, net_score +5 → HOLD (neutral stance)
    - Bullish stance, 35% confidence, net_score +40 → HOLD (low confidence)
    
    Remember: Your primary responsibility is capital preservation through disciplined risk management
    while capturing high-conviction opportunities identified by the research process.
    """,
    tools=[
        Tool(name="make_trading_decision", func=make_trading_decision),
        Tool(name="validate_trade_parameters", func=validate_trade_parameters)
    ]
)