"""
Trading Coordinator Agent

Purpose:
- Orchestrates the complete trading analysis workflow from user input to final trading decision
- Manages sequential execution of all agent layers: validation → analysis → research → management → trading
- Handles error propagation, data flow validation, and workflow state management
- Provides comprehensive logging and audit trail for all trading decisions

Architecture Overview:
The coordinator manages a 6-layer architecture:
1. VALIDATION LAYER: Ticker resolution and input validation
2. ANALYST LAYER: Parallel execution of 4 specialized analysts
3. RESEARCHER LAYER: Bull/bear perspective analysis
4. MANAGEMENT LAYER: Research consensus and score aggregation
5. EXECUTION LAYER: Trading decision with risk management
6. OUTPUT LAYER: Structured results with audit trail

Workflow Execution:
1. Input Processing → Ticker Agent (validate/resolve company name to ticker)
2. Parallel Analysis → 4 Analyst Agents (fundamentals, technical, sentiment, news)
3. Research Synthesis → Bull & Bear Researchers (optimistic vs skeptical perspectives)
4. Consensus Building → Research Manager (aggregate to net_score with dampening)
5. Trading Decision → Trader Agent (BUY/SELL/HOLD with position sizing)
6. Result Packaging → Structured output with full audit trail
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

# Import all agent modules
from agents.analysts.ticker_agent import resolve_and_validate_ticker
from agents.analysts.fundamentals_agent import fetch_company_data, calculate_fundamentals_score
from agents.analysts.technical_agent import fetch_historical_data, calculate_technical_indicators, calculate_technical_score
from agents.analysts.sentiment_agent import analyze_news_sentiment
from agents.analysts.news_agent import analyze_news_events
from agents.researchers.researcher_bull import calculate_bullish_assessment, generate_bullish_argument
from agents.researchers.researcher_bear import calculate_bearish_assessment, analyze_bearish_scenario
from agents.manager.research_manager import aggregate_research_scores, synthesize_research_consensus
from agents.trader.trader_agent import make_trading_decision, calculate_position_size, apply_risk_management

logger = logging.getLogger(__name__)


def orchestrate_trading_analysis(user_input: str) -> Dict[str, Any]:
    """
    Main workflow orchestrator for complete trading analysis pipeline.
    
    Args:
        user_input: Company name or ticker symbol from user
        
    Returns:
        Dict containing complete analysis results with audit trail
    """
    start_time = datetime.now()
    workflow_id = f"analysis_{start_time.strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"Starting trading analysis workflow {workflow_id} for input: {user_input}")
    
    try:
        # Phase 1: Input Validation & Ticker Resolution
        logger.info("Phase 1: Ticker validation and resolution")
        validation_result = validate_workflow_inputs({"user_input": user_input})
        
        if not validation_result["valid"]:
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": validation_result["error"],
                "phase": "validation",
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
        
        ticker = validation_result["ticker"]
        company_name = validation_result.get("company_name", ticker)
        
        # Phase 2: Parallel Analyst Execution
        logger.info(f"Phase 2: Executing analyst layer for {ticker}")
        analyst_results = execute_analyst_layer(ticker)
        
        if not analyst_results["success"]:
            return {
                "workflow_id": workflow_id,
                "ticker": ticker,
                "status": "failed",
                "error": analyst_results["error"],
                "phase": "analysis",
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
        
        # Phase 3: Research Layer Execution
        logger.info("Phase 3: Executing research layer")
        research_results = execute_research_layer(analyst_results["analyst_bundle"])
        
        if not research_results["success"]:
            return {
                "workflow_id": workflow_id,
                "ticker": ticker,
                "status": "failed", 
                "error": research_results["error"],
                "phase": "research",
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
        
        # Phase 4: Research Management & Consensus
        logger.info("Phase 4: Building research consensus")
        consensus_result = aggregate_research_scores(research_results["research_bundle"])
        
        # Phase 5: Trading Decision & Risk Management
        logger.info("Phase 5: Making final trading decision")
        trading_decision = finalize_trading_decision(consensus_result)
        
        # Phase 6: Result Compilation & Audit
        logger.info("Phase 6: Generating audit trail and final results")
        audit_trail = generate_audit_trail({
            "workflow_id": workflow_id,
            "user_input": user_input,
            "ticker": ticker,
            "company_name": company_name,
            "validation_result": validation_result,
            "analyst_results": analyst_results,
            "research_results": research_results,
            "consensus_result": consensus_result,
            "trading_decision": trading_decision,
            "start_time": start_time
        })
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Build comprehensive result
        result = {
            "workflow_id": workflow_id,
            "ticker": ticker,
            "company_name": company_name,
            "analysis_timestamp": start_time.isoformat(),
            "workflow_status": "completed",
            
            "analyst_scores": {
                "fundamentals": analyst_results["analyst_bundle"].get("fundamentals_score", 50.0),
                "technical": analyst_results["analyst_bundle"].get("technical_score", 50.0),
                "sentiment": analyst_results["analyst_bundle"].get("sentiment_score", 50.0),
                "news": analyst_results["analyst_bundle"].get("news_score", 50.0)
            },
            
            "research_assessment": {
                "bull_score": research_results["research_bundle"]["bull_research"].get("bull_score", 50.0),
                "bear_score": research_results["research_bundle"]["bear_research"].get("bear_score", 50.0),
                "net_score": consensus_result.get("net_score", 0.0),
                "stance": consensus_result.get("stance", "neutral"),
                "confidence": consensus_result.get("confidence", 50.0)
            },
            
            "trading_decision": {
                "action": trading_decision.get("action", "HOLD"),
                "position_size": trading_decision.get("position_size", 0.0),
                "rationale": trading_decision.get("rationale", "No rationale available"),
                "risk_metrics": trading_decision.get("risk_metrics", {})
            },
            
            "executive_summary": generate_executive_summary(consensus_result, trading_decision),
            "audit_trail": audit_trail,
            "processing_time_ms": round(processing_time, 2)
        }
        
        logger.info(f"Trading analysis workflow {workflow_id} completed successfully in {processing_time:.0f}ms")
        return result
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Critical error in trading analysis workflow {workflow_id}: {e}")
        
        return {
            "workflow_id": workflow_id,
            "status": "failed",
            "error": f"Critical workflow error: {str(e)}",
            "phase": "orchestration",
            "processing_time_ms": round(processing_time, 2)
        }


def validate_workflow_inputs(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize workflow inputs.
    
    Args:
        input_data: Dict containing user_input and optional parameters
        
    Returns:
        Dict with validation results and resolved ticker
    """
    if not input_data or not isinstance(input_data, dict):
        return {
            "valid": False,
            "error": "Invalid input data provided",
            "ticker": None
        }
    
    user_input = input_data.get("user_input", "").strip()
    
    if not user_input:
        return {
            "valid": False,
            "error": "Empty user input provided",
            "ticker": None
        }
    
    try:
        # Use ticker agent to resolve and validate
        ticker_result = resolve_and_validate_ticker(user_input)
        
        if not ticker_result["valid"]:
            return {
                "valid": False,
                "error": f"Ticker validation failed: {ticker_result['message']}",
                "ticker": None,
                "suggestions": get_ticker_suggestions(user_input)
            }
        
        return {
            "valid": True,
            "ticker": ticker_result["symbol"],
            "company_name": user_input if user_input.upper() != ticker_result["symbol"] else ticker_result["symbol"],
            "message": ticker_result["message"]
        }
        
    except Exception as e:
        logger.error(f"Error in input validation: {e}")
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
            "ticker": None
        }


def execute_analyst_layer(ticker: str) -> Dict[str, Any]:
    """
    Execute all 4 analysts in parallel for efficiency.
    
    Args:
        ticker: Valid stock ticker symbol
        
    Returns:
        Dict containing analyst results and consolidated bundle
    """
    if not ticker:
        return {
            "success": False,
            "error": "No ticker provided for analyst execution",
            "analyst_bundle": {}
        }
    
    try:
        analyst_results = {}
        errors = []
        
        # Execute analysts in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all analyst tasks
            futures = {
                executor.submit(execute_fundamentals_analysis, ticker): "fundamentals",
                executor.submit(execute_technical_analysis, ticker): "technical", 
                executor.submit(execute_sentiment_analysis, ticker): "sentiment",
                executor.submit(execute_news_analysis, ticker): "news"
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                analyst_type = futures[future]
                try:
                    result = future.result(timeout=30)  # 30 second timeout per analyst
                    analyst_results[analyst_type] = result
                    logger.info(f"{analyst_type.capitalize()} analysis completed for {ticker}")
                except Exception as e:
                    error_msg = f"{analyst_type} analysis failed: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    # Use default neutral score for failed analysts
                    analyst_results[analyst_type] = {
                        f"{analyst_type}_score": 50.0,
                        "error": str(e),
                        "status": "failed"
                    }
        
        # Build consolidated analyst bundle
        analyst_bundle = {
            "fundamentals_score": analyst_results.get("fundamentals", {}).get("fundamental_score", 50.0),
            "technical_score": analyst_results.get("technical", {}).get("technical_score", 50.0),
            "sentiment_score": analyst_results.get("sentiment", {}).get("sentiment_score", 50.0),
            "news_score": analyst_results.get("news", {}).get("news_score", 50.0),
            "raw_data": {
                "fundamentals": analyst_results.get("fundamentals", {}),
                "technical": analyst_results.get("technical", {}),
                "sentiment": analyst_results.get("sentiment", {}),
                "news": analyst_results.get("news", {})
            }
        }
        
        # Log summary
        scores_summary = f"F:{analyst_bundle['fundamentals_score']:.1f}, T:{analyst_bundle['technical_score']:.1f}, S:{analyst_bundle['sentiment_score']:.1f}, N:{analyst_bundle['news_score']:.1f}"
        logger.info(f"Analyst layer completed for {ticker} - Scores: {scores_summary}")
        
        return {
            "success": True,
            "analyst_bundle": analyst_bundle,
            "individual_results": analyst_results,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"Critical error in analyst layer execution: {e}")
        return {
            "success": False,
            "error": f"Analyst layer execution failed: {str(e)}",
            "analyst_bundle": {}
        }


def execute_research_layer(analyst_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute bull and bear researchers in parallel.
    
    Args:
        analyst_bundle: Consolidated analyst scores and data
        
    Returns:
        Dict containing research results from both perspectives
    """
    if not analyst_bundle:
        return {
            "success": False,
            "error": "No analyst bundle provided for research execution",
            "research_bundle": {}
        }
    
    try:
        research_results = {}
        errors = []
        
        # Execute researchers in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit research tasks
            futures = {
                executor.submit(calculate_bullish_assessment, analyst_bundle): "bull",
                executor.submit(calculate_bearish_assessment, analyst_bundle): "bear"
            }
            
            # Collect results
            for future in as_completed(futures):
                researcher_type = futures[future]
                try:
                    result = future.result(timeout=20)  # 20 second timeout per researcher
                    research_results[researcher_type] = result
                    logger.info(f"{researcher_type.capitalize()} research completed")
                except Exception as e:
                    error_msg = f"{researcher_type} research failed: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    # Use default neutral assessment for failed researchers
                    research_results[researcher_type] = {
                        f"{researcher_type}_score": 50.0,
                        "confidence": 50.0,
                        "stance": "neutral",
                        "rationale": f"Error in {researcher_type} research: {str(e)}",
                        "error": str(e)
                    }
        
        # Build research bundle for manager
        research_bundle = {
            "bull_research": research_results.get("bull", {}),
            "bear_research": research_results.get("bear", {}),
            "analyst_bundle": analyst_bundle  # Include original data for context
        }
        
        # Log summary
        bull_score = research_results.get("bull", {}).get("bull_score", 50.0)
        bear_score = research_results.get("bear", {}).get("bear_score", 50.0)
        logger.info(f"Research layer completed - Bull: {bull_score:.1f}, Bear: {bear_score:.1f}")
        
        return {
            "success": True,
            "research_bundle": research_bundle,
            "individual_results": research_results,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"Critical error in research layer execution: {e}")
        return {
            "success": False,
            "error": f"Research layer execution failed: {str(e)}",
            "research_bundle": {}
        }


def finalize_trading_decision(research_consensus: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert research consensus into final trading decision with risk management.
    
    Args:
        research_consensus: Output from research manager aggregation
        
    Returns:
        Dict containing final trading decision with risk controls
    """
    if not research_consensus:
        logger.warning("No research consensus provided for trading decision")
        return {
            "action": "HOLD",
            "position_size": 0.0,
            "confidence": 50.0,
            "rationale": "No research consensus available - defaulting to HOLD",
            "risk_metrics": {"reason": "no_data"}
        }
    
    try:
        # Use trader agent to make decision
        trading_decision = make_trading_decision(research_consensus)
        
        # Apply additional risk management layers
        risk_managed_decision = apply_risk_management(trading_decision, research_consensus)
        
        # Validate final decision meets all constraints
        validated_decision = validate_trading_decision(risk_managed_decision)
        
        logger.info(f"Trading decision finalized: {validated_decision['action']} {validated_decision['position_size']:.1f}%")
        return validated_decision
        
    except Exception as e:
        logger.error(f"Error in trading decision finalization: {e}")
        return {
            "action": "HOLD",
            "position_size": 0.0,
            "confidence": 50.0,
            "rationale": f"Error in decision making: {str(e)} - defaulting to HOLD",
            "risk_metrics": {"error": str(e)}
        }


def generate_audit_trail(workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate comprehensive audit trail for regulatory compliance.
    
    Args:
        workflow_data: Complete workflow execution data
        
    Returns:
        List of audit events with timestamps and details
    """
    audit_events = []
    
    try:
        start_time = workflow_data.get("start_time", datetime.now())
        
        # Workflow initiation
        audit_events.append({
            "timestamp": start_time.isoformat(),
            "event": "workflow_initiated",
            "details": {
                "workflow_id": workflow_data.get("workflow_id"),
                "user_input": workflow_data.get("user_input"),
                "resolved_ticker": workflow_data.get("ticker")
            }
        })
        
        # Validation phase
        if workflow_data.get("validation_result"):
            audit_events.append({
                "timestamp": (start_time).isoformat(),
                "event": "ticker_validation",
                "details": workflow_data["validation_result"]
            })
        
        # Analyst execution
        if workflow_data.get("analyst_results"):
            audit_events.append({
                "timestamp": (start_time).isoformat(),
                "event": "analyst_execution",
                "details": {
                    "scores": workflow_data["analyst_results"]["analyst_bundle"],
                    "errors": workflow_data["analyst_results"].get("errors")
                }
            })
        
        # Research execution
        if workflow_data.get("research_results"):
            audit_events.append({
                "timestamp": (start_time).isoformat(),
                "event": "research_execution", 
                "details": {
                    "bull_assessment": workflow_data["research_results"]["research_bundle"]["bull_research"],
                    "bear_assessment": workflow_data["research_results"]["research_bundle"]["bear_research"]
                }
            })
        
        # Consensus building
        if workflow_data.get("consensus_result"):
            audit_events.append({
                "timestamp": (start_time).isoformat(),
                "event": "consensus_building",
                "details": workflow_data["consensus_result"]
            })
        
        # Trading decision
        if workflow_data.get("trading_decision"):
            audit_events.append({
                "timestamp": (start_time).isoformat(),
                "event": "trading_decision",
                "details": workflow_data["trading_decision"]
            })
        
        # Workflow completion
        audit_events.append({
            "timestamp": datetime.now().isoformat(),
            "event": "workflow_completed",
            "details": {
                "workflow_id": workflow_data.get("workflow_id"),
                "status": "success"
            }
        })
        
        return audit_events
        
    except Exception as e:
        logger.error(f"Error generating audit trail: {e}")
        return [{
            "timestamp": datetime.now().isoformat(),
            "event": "audit_error",
            "details": {"error": str(e)}
        }]


# Helper functions for analyst execution
def execute_fundamentals_analysis(ticker: str) -> Dict[str, Any]:
    """Execute fundamentals analysis for given ticker."""
    try:
        company_data = fetch_company_data(ticker)
        return calculate_fundamentals_score(company_data)
    except Exception as e:
        logger.error(f"Fundamentals analysis failed for {ticker}: {e}")
        return {"fundamental_score": 50.0, "error": str(e)}


def execute_technical_analysis(ticker: str) -> Dict[str, Any]:
    """Execute technical analysis for given ticker."""
    try:
        historical_data = fetch_historical_data(ticker)
        indicators = calculate_technical_indicators(historical_data)
        return calculate_technical_score(indicators)
    except Exception as e:
        logger.error(f"Technical analysis failed for {ticker}: {e}")
        return {"technical_score": 50.0, "error": str(e)}


def execute_sentiment_analysis(ticker: str) -> Dict[str, Any]:
    """Execute sentiment analysis for given ticker."""
    try:
        return analyze_news_sentiment(ticker)
    except Exception as e:
        logger.error(f"Sentiment analysis failed for {ticker}: {e}")
        return {"sentiment_score": 50.0, "error": str(e)}


def execute_news_analysis(ticker: str) -> Dict[str, Any]:
    """Execute news analysis for given ticker."""
    try:
        return analyze_news_events(ticker)
    except Exception as e:
        logger.error(f"News analysis failed for {ticker}: {e}")
        return {"news_score": 50.0, "error": str(e)}


def get_ticker_suggestions(query: str) -> List[str]:
    """Generate ticker suggestions for failed resolution."""
    # This would typically use a fuzzy matching algorithm
    # For now, return common suggestions
    common_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
    return [t for t in common_tickers if query.upper() in t or t in query.upper()]


def generate_executive_summary(consensus: Dict[str, Any], decision: Dict[str, Any]) -> str:
    """Generate executive summary of analysis and decision."""
    try:
        stance = consensus.get("stance", "neutral")
        net_score = consensus.get("net_score", 0.0)
        confidence = consensus.get("confidence", 50.0)
        action = decision.get("action", "HOLD")
        position_size = decision.get("position_size", 0.0)
        
        summary = f"Analysis recommends {action}"
        
        if action != "HOLD":
            summary += f" with {position_size:.1f}% portfolio allocation"
        
        summary += f". Research consensus is {stance} with net score of {net_score:.1f} "
        summary += f"and {confidence:.0f}% confidence. "
        
        if stance == "bullish":
            summary += "Positive fundamentals and sentiment support upside potential."
        elif stance == "bearish":
            summary += "Risk factors and negative signals suggest caution."
        else:
            summary += "Mixed signals warrant neutral positioning."
            
        return summary
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def validate_trading_decision(decision: Dict[str, Any]) -> Dict[str, Any]:
    """Validate trading decision meets all risk constraints."""
    try:
        # Ensure position size is within bounds
        position_size = decision.get("position_size", 0.0)
        position_size = max(0.0, min(20.0, position_size))  # Cap at 20%
        
        # Ensure confidence meets minimum threshold for non-HOLD actions
        confidence = decision.get("confidence", 50.0)
        action = decision.get("action", "HOLD")
        
        if action != "HOLD" and confidence < 40.0:
            action = "HOLD"
            position_size = 0.0
            decision["rationale"] += " [Overridden to HOLD due to insufficient confidence]"
        
        decision.update({
            "action": action,
            "position_size": round(position_size, 2),
            "confidence": round(confidence, 2)
        })
        
        return decision
        
    except Exception as e:
        logger.error(f"Error validating trading decision: {e}")
        return {
            "action": "HOLD",
            "position_size": 0.0,
            "confidence": 50.0,
            "rationale": f"Validation error: {str(e)} - defaulting to HOLD"
        }


# Define the Coordinator Agent using Google ADK
CoordinatorAgent = LlmAgent(
    name="coordinator_agent",
    role="Orchestrate complete trading analysis workflow from user input to actionable trading decisions",
    instructions="""
    You are the Trading Coordinator responsible for managing the entire trading analysis pipeline.
    
    Your core responsibilities:
    1. WORKFLOW ORCHESTRATION: Execute the complete 6-layer trading analysis pipeline
    2. DATA FLOW MANAGEMENT: Ensure proper data passing between agent layers
    3. ERROR HANDLING: Manage failures gracefully with fallback strategies
    4. QUALITY ASSURANCE: Validate outputs at each stage before proceeding
    5. AUDIT TRAIL: Maintain comprehensive logging for regulatory compliance
    
    EXECUTION SEQUENCE:
    
    Phase 1 - Input Validation & Ticker Resolution:
    - Receive user input (company name or ticker symbol)
    - Use validate_workflow_inputs() to resolve and validate ticker
    - Validate ticker exists and is tradeable
    - If validation fails: return error with suggestions
    
    Phase 2 - Parallel Analyst Execution:
    Execute all 4 analysts in parallel for efficiency:
    - FundamentalsAgent: fetch_company_data() + calculate_fundamentals_score()
    - TechnicalAgent: fetch_historical_data() + calculate_technical_indicators() + calculate_technical_score()
    - SentimentAgent: analyze_news_sentiment() for lexicon-based sentiment analysis
    - NewsAgent: analyze_news_events() for event-driven impact analysis
    
    Collect outputs: {fundamentals_score, technical_score, sentiment_score, news_score}
    
    Phase 3 - Research Perspective Analysis:
    Execute bull and bear researchers in parallel:
    - ResearcherBull: calculate_bullish_assessment() + generate_bullish_argument()
    - ResearcherBear: calculate_bearish_assessment() + analyze_bearish_scenario()
    
    Collect outputs: {bull_score, bull_confidence, bear_score, bear_confidence, rationales}
    
    Phase 4 - Research Management & Consensus:
    - ResearchManager: aggregate_research_scores() to create net_score (-100 to +100)
    - Apply 10% bear dampening to prevent over-penalization
    - Determine stance (bullish ≥+20, bearish ≤-20, neutral -20 to +20)
    - Calculate confidence based on signal strength and researcher alignment
    
    Phase 5 - Trading Decision & Risk Management:
    - TraderAgent: make_trading_decision() with strict risk controls
    - Apply 40% minimum confidence threshold
    - Calculate position sizing: (|net_score|/100) * (confidence/100) * 20% max
    - Enforce maximum 20% portfolio exposure per trade
    - Validate all parameters before finalizing
    
    Phase 6 - Result Compilation & Audit:
    - Package complete analysis chain with timestamps
    - Include all intermediate scores and rationales
    - Provide executive summary with key decision factors
    - Generate audit trail for compliance and review
    
    ERROR HANDLING STRATEGIES:
    - Ticker validation failure: Suggest similar tickers, request clarification
    - Analyst failure: Use default neutral scores (50.0) with error flags
    - Data unavailability: Proceed with available data, note limitations
    - Network issues: Implement retry logic with exponential backoff
    - Calculation errors: Default to conservative HOLD position
    
    QUALITY GATES:
    - Validate ticker resolution before proceeding to analysis
    - Ensure all analyst scores are in valid 0-100 range
    - Verify research scores align with input analyst data
    - Confirm trading decision respects all risk management rules
    - Check final output completeness before returning to user
    
    PERFORMANCE REQUIREMENTS:
    - Complete analysis within 30 seconds for standard requests
    - Handle up to 10 concurrent analysis requests
    - Maintain 99.5% uptime for trading hours
    - Log all decisions for regulatory audit requirements
    
    RISK MANAGEMENT PRINCIPLES:
    - Never exceed 20% portfolio allocation per trade
    - Require minimum 40% confidence for any non-HOLD action
    - Default to HOLD on any system errors or data quality issues
    - Implement circuit breakers for extreme market conditions
    - Maintain detailed audit logs for all trading decisions
    
    Remember: You are the central orchestrator ensuring reliable, auditable, and risk-managed 
    trading decisions through systematic analysis of fundamental, technical, sentiment, and news factors.
    """,
    tools=[
        Tool(name="orchestrate_trading_analysis", func=orchestrate_trading_analysis),
        Tool(name="validate_workflow_inputs", func=validate_workflow_inputs),
        Tool(name="execute_analyst_layer", func=execute_analyst_layer),
        Tool(name="execute_research_layer", func=execute_research_layer),
        Tool(name="finalize_trading_decision", func=finalize_trading_decision),
        Tool(name="generate_audit_trail", func=generate_audit_trail)
    ]
)

root_agent = CoordinatorAgent