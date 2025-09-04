from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None

class StockData(BaseModel):
    ticker: str
    name: str
    performance: str

class AnalystScores(BaseModel):
    fundamentals: float
    technical: float
    sentiment: float
    news: float

class ResearchAssessment(BaseModel):
    bull_score: float
    bear_score: float
    net_score: float
    stance: str
    confidence: float

class TradingDecision(BaseModel):
    action: str
    position_size: float
    rationale: str
    risk_metrics: Dict[str, Any]

class TradingAnalysisData(BaseModel):
    workflow_id: str
    ticker: str
    company_name: str
    analysis_timestamp: str
    workflow_status: str
    analyst_scores: AnalystScores
    research_assessment: ResearchAssessment
    trading_decision: TradingDecision
    executive_summary: str
    processing_time_ms: float

class ChatResponse(BaseModel):
    message: str
    agent_name: str
    data: Optional[List[StockData]] = None
    trading_analysis: Optional[TradingAnalysisData] = None
    timestamp: datetime
    session_id: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
