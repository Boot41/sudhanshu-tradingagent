from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Union

from schemas.chat_schema import ChatRequest, ChatResponse, ErrorResponse
from service.chat_service import chat_service
from core.security import verify_token

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_data = verify_token(token, credentials_exception)
        if not user_data:
            raise credentials_exception
        return {"email": user_data}
    except HTTPException:
        raise credentials_exception

@router.post("/message", response_model=Union[ChatResponse, ErrorResponse])
async def send_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message to the trading agent orchestrator.
    
    Args:
        request: Chat request containing the user message
        current_user: Current authenticated user
        
    Returns:
        Response from the appropriate agent with any structured data
    """
    try:
        # Add user ID from token to request
        user_id = current_user.get("user_id")
        
        # Process message through chat service
        response = await chat_service.process_message(
            message=request.message,
            user_id=user_id,
            session_id=request.session_id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for the chat service."""
    return {"status": "healthy", "service": "chat"}
