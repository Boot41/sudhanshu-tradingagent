"""Orchestrator agent that routes user requests to the appropriate agent."""
from typing import Dict, Any, Optional
import json

from google.adk.agents import LlmAgent
from agent.agent_registry import AgentRegistry

class Orchestrator:
    """Orchestrator that routes requests to appropriate agents."""
    
    def __init__(self, agent_registry: AgentRegistry):
        """Initialize the orchestrator with an agent registry."""
        self.registry = agent_registry
        self.llm_agent = self._create_llm_agent()
    
    def _create_llm_agent(self) -> LlmAgent:
        """Create the LLM agent for handling orchestration."""
        return LlmAgent(
            name="orchestrator",
            model="gemini-1.5-flash",
            description="Routes user requests to the most appropriate agent.",
            instruction="""
            You are an intelligent orchestrator that routes user requests to the most appropriate agent.
            
            Your responsibilities:
            1. Analyze the user's request to understand their intent
            2. Determine which specialized agent is best suited to handle the request
            3. Either:
               - Route the request to the appropriate agent, or
               - If no suitable agent is found, provide a helpful response
            
            Available agents and their capabilities:
            {agents_info}
            
            When routing to another agent, use the handoff function with the agent's name and the user's original message.
            
            If the user's request is unclear or you need more information, ask clarifying questions.
            """,
            tools=[self.handoff]
        )
    
    async def handoff(self, agent_name: str, user_message: str) -> str:
        """
        Hand off the conversation to another agent.
        
        Args:
            agent_name: Name of the agent to hand off to
            user_message: The original user message to forward
            
        Returns:
            Response from the target agent
        """
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return f"Error: No agent found with name '{agent_name}'. Available agents: {', '.join(self.registry.list_agents().keys())}"
        
        # Forward the message to the target agent
        response = await agent.chat(user_message)
        return f"[Handed off to {agent_name}]\n{response}"
    
    async def process_message(self, user_message: str) -> str:
        """
        Process a user message by routing it to the appropriate agent.
        
        Args:
            user_message: The user's message
            
        Returns:
            Response from the appropriate agent or the orchestrator
        """
        # First, try to find the best agent using the registry
        best_agent, confidence = self.registry.find_best_agent(user_message)
        
        # If we have high confidence in the match, route directly
        if confidence >= 2 and best_agent:
            return await self.handoff(best_agent, user_message)
        
        # Otherwise, let the LLM agent decide
        agents_info = json.dumps(self.registry.list_agents(), indent=2)
        self.llm_agent.instruction = self.llm_agent.instruction.format(agents_info=agents_info)
        
        # Get the LLM's decision
        response = await self.llm_agent.chat(user_message)
        return response
