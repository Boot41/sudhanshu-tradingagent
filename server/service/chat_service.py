from typing import Optional
from datetime import datetime
import uuid
import logging

from schemas.chat_schema import ChatResponse, TradingAnalysisData, AnalystScores, ResearchAssessment, TradingDecision
from trader_agent.coordinator_agent import orchestrate_trading_analysis
from trader_agent.agents.analysts.ticker_agent import TickerAgent

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions with trading agent workflow."""

    def __init__(self):
        """Initialize the chat service."""
        pass

    async def process_message(
        self, message: str, user_id: Optional[int] = None, session_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a user message through the trading agent workflow.
        
        Args:
            message: User input (company name, ticker, or natural language query)
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            ChatResponse with structured trading analysis data
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        try:
            logger.info(f"Processing trading analysis for: {message}")
            
            # Extract company name/ticker from natural language using TickerAgent
            extracted_input = await self._extract_company_from_message(message.strip())
            
            # Execute the complete trading workflow
            analysis_result = orchestrate_trading_analysis(extracted_input)
            
            # Check if workflow completed successfully
            if analysis_result.get("workflow_status") == "completed":
                # Create structured response data
                trading_analysis = TradingAnalysisData(
                    workflow_id=analysis_result["workflow_id"],
                    ticker=analysis_result["ticker"],
                    company_name=analysis_result["company_name"],
                    analysis_timestamp=analysis_result["analysis_timestamp"],
                    workflow_status=analysis_result["workflow_status"],
                    analyst_scores=AnalystScores(**analysis_result["analyst_scores"]),
                    research_assessment=ResearchAssessment(**analysis_result["research_assessment"]),
                    trading_decision=TradingDecision(**analysis_result["trading_decision"]),
                    executive_summary=analysis_result["executive_summary"],
                    processing_time_ms=analysis_result["processing_time_ms"]
                )
                
                # Generate user-friendly message
                action = analysis_result["trading_decision"]["action"]
                ticker = analysis_result["ticker"]
                net_score = analysis_result["research_assessment"]["net_score"]
                
                message_text = f"Complete trading analysis for {ticker} finished. "
                message_text += f"Recommendation: {action} "
                
                if action != "HOLD":
                    position_size = analysis_result["trading_decision"]["position_size"]
                    message_text += f"({position_size:.1f}% allocation) "
                
                message_text += f"with net score {net_score:.1f}. "
                message_text += f"Analysis completed in {analysis_result['processing_time_ms']:.0f}ms."
                
                return ChatResponse(
                    message=message_text,
                    agent_name="Trading Coordinator",
                    trading_analysis=trading_analysis,
                    timestamp=datetime.utcnow(),
                    session_id=session_id,
                )
            
            else:
                # Handle workflow failure
                error_phase = analysis_result.get("phase", "unknown")
                error_msg = analysis_result.get("error", "Unknown error occurred")
                
                return ChatResponse(
                    message=f"Trading analysis failed during {error_phase} phase: {error_msg}",
                    agent_name="Trading Coordinator",
                    timestamp=datetime.utcnow(),
                    session_id=session_id,
                )
                
        except Exception as e:
            logger.error(f"Error in chat service: {e}")
            return ChatResponse(
                message=f"I encountered an error while processing your request: {str(e)}. Please try again with a valid company name or ticker symbol.",
                agent_name="Trading Coordinator",
                timestamp=datetime.utcnow(),
                session_id=session_id,
            )

    async def _extract_company_from_message(self, message: str) -> str:
        """
        Extract company name or ticker from natural language input using TickerAgent.
        
        Args:
            message: Raw user input (could be natural language)
            
        Returns:
            Extracted company name or ticker symbol
        """
        try:
            # Use the TickerAgent to intelligently extract company information
            # This mimics what ADK web interface does automatically
            response = await TickerAgent.run(
                f"Extract the company name or ticker symbol from this user input: '{message}'. "
                f"If it's already a clear company name or ticker, return it as-is. "
                f"If it's a sentence mentioning a company, extract just the company name. "
                f"Examples: 'analyze microsoft' -> 'microsoft', 'AAPL stock analysis' -> 'AAPL', "
                f"'what do you think about Apple?' -> 'Apple'"
            )
            
            # Extract the company name from the agent response
            if hasattr(response, 'content'):
                extracted = response.content.strip()
            else:
                extracted = str(response).strip()
            
            # Clean up common response patterns
            extracted = extracted.replace('"', '').replace("'", "")
            if extracted.lower().startswith('the company is '):
                extracted = extracted[15:]
            elif extracted.lower().startswith('company: '):
                extracted = extracted[9:]
            
            logger.info(f"Extracted '{extracted}' from input '{message}'")
            return extracted
            
        except Exception as e:
            logger.warning(f"Failed to extract company from message using TickerAgent: {e}")
            # Fallback to original message if extraction fails
            return message

# Global instance
chat_service = ChatService()
