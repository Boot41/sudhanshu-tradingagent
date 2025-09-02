"""
Agent wrapper with comprehensive logging for debugging agent execution flow.
"""

import logging
import json
from typing import Any, Dict
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AgentExecutionTracker:
    """Tracks agent execution with detailed logging."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.call_count = 0
    
    def log_agent_call(self, request: Any) -> None:
        """Log when an agent receives a request."""
        self.call_count += 1
        logger.info(f"🚀 {self.agent_name} - Call #{self.call_count}")
        logger.info(f"📥 {self.agent_name} - Request: {str(request)[:500]}...")
    
    def log_agent_response(self, response: Any) -> None:
        """Log agent response."""
        logger.info(f"📤 {self.agent_name} - Response: {str(response)[:500]}...")
    
    def log_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Log when agent calls a tool."""
        logger.info(f"🔧 {self.agent_name} - Calling tool: {tool_name}")
        logger.info(f"🔧 {self.agent_name} - Tool args: {json.dumps(arguments, indent=2)}")
    
    def log_tool_result(self, tool_name: str, result: Any) -> None:
        """Log tool execution result."""
        logger.info(f"✅ {self.agent_name} - Tool {tool_name} completed")
        logger.info(f"✅ {self.agent_name} - Tool result: {str(result)[:500]}...")
    
    def log_error(self, error: Exception) -> None:
        """Log agent errors."""
        logger.error(f"❌ {self.agent_name} - Error: {str(error)}")
        logger.error(f"❌ {self.agent_name} - Error type: {type(error).__name__}")

def create_agent_wrapper(agent, agent_name: str):
    """Create a wrapper around an agent to add logging."""
    tracker = AgentExecutionTracker(agent_name)
    
    # Store original methods
    original_call = getattr(agent, '__call__', None)
    
    if original_call:
        @wraps(original_call)
        def wrapped_call(*args, **kwargs):
            try:
                tracker.log_agent_call(args[0] if args else "No request")
                result = original_call(*args, **kwargs)
                tracker.log_agent_response(result)
                return result
            except Exception as e:
                tracker.log_error(e)
                raise
        
        # Replace the call method
        agent.__call__ = wrapped_call
    
    return agent

# Global trackers for each agent
recommendation_tracker = AgentExecutionTracker("RecommendationAgent")
visualizer_tracker = AgentExecutionTracker("VisualizerAgent")
coordinator_tracker = AgentExecutionTracker("CoordinatorAgent")
