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

class ChatResponse(BaseModel):
    message: str
    agent_name: str
    data: Optional[List[StockData]] = None
    timestamp: datetime
    session_id: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
