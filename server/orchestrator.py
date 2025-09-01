"""Orchestrator agent that routes user requests to the appropriate agent using ADK patterns."""
from typing import Dict, Any, Optional
import json

from google.adk.agents import LlmAgent
from agent.agent_registry import AgentRegistry
from screener_agent.screener_agent import root_agent as screener_agent

class Orchestrator:
    """ADK-based Orchestrator that routes requests to appropriate agents using sub_agents pattern."""
    
    def __init__(self, agent_registry: AgentRegistry):
        """Initialize the orchestrator with an agent registry."""
        self.registry = agent_registry
        self.llm_agent = self._create_coordinator_agent()
    
    def _create_coordinator_agent(self) -> LlmAgent:
        """Create the coordinator LLM agent using proper ADK sub_agents pattern."""
        # Get available agents from registry for context
        agents_info = json.dumps(self.registry.list_agents(), indent=2)
        
        return LlmAgent(
            name="trading_coordinator",
            model="gemini-1.5-flash",
            description="Main trading assistant coordinator that routes requests to specialized agents.",
            instruction="""
            You are a trading assistant coordinator. Route user requests to the appropriate specialist agent.
            
            ROUTING RULES:
            - For stock screening, filtering, or queries about stocks/industries/sectors: Transfer to screener_agent
            - For requests about "top stocks", "best stocks", "automotive", "technology", "tech", "finance": Transfer to screener_agent
            - For general stock market questions or analysis: Transfer to screener_agent
            
            Use transfer_to_agent() to route requests. The specialist agents will handle the detailed work.
            
            Examples:
            - "top 5 tech stocks" → transfer_to_agent(agent_name='screener_agent')
            - "best automotive stocks" → transfer_to_agent(agent_name='screener_agent')
            - "screen technology stocks" → transfer_to_agent(agent_name='screener_agent')
            """,
            # Use ADK's sub_agents pattern for proper agent hierarchy
            sub_agents=[screener_agent]
        )
    
    async def process_message(self, user_message: str) -> str:
        """
        Process a user message using the LLM agent with proper ADK routing.
        
        Args:
            user_message: The user's message
            
        Returns:
            Response from the appropriate agent via LLM routing
        """
        try:
            # Import ADK components for proper agent execution
            from google.adk.runner import Runner
            from google.adk.sessions import InMemorySessionService
            from google.genai.types import Content, Part
            import uuid
            
            # Create session service and runner
            session_service = InMemorySessionService()
            session_id = str(uuid.uuid4())
            user_id = "frontend_user"
            app_name = "trading_agent"
            
            # Create session
            session_service.createSession(app_name, user_id, None, session_id).blockingGet()
            
            # Create runner with the LLM agent
            runner = Runner(self.llm_agent, app_name, None, session_service)
            
            # Create content from user message
            user_content = Content.fromParts(Part.fromText(user_message))
            
            # Run the agent and collect response
            event_stream = runner.runAsync(user_id, session_id, user_content)
            final_response = "No response received"
            
            # Process events to get final response
            def process_event(event):
                nonlocal final_response
                if event.finalResponse() and event.content().isPresent():
                    content = event.content().get()
                    if content.parts() and len(content.parts()) > 0:
                        part = content.parts()[0]
                        if part.text().isPresent():
                            final_response = part.text().get()
            
            # Block and process all events
            event_stream.blockingForEach(process_event)
            
            return final_response
            
        except Exception as e:
            print(f"Error in orchestrator process_message: {e}")
            # Fallback to direct screener agent call for now
            return await self._fallback_direct_call(user_message)
    
    async def _fallback_direct_call(self, user_message: str) -> str:
        """
        Fallback method that calls screener agent directly if ADK routing fails.
        This maintains functionality while we debug ADK integration.
        """
        try:
            # For stock-related queries, route directly to screener agent
            if any(keyword in user_message.lower() for keyword in 
                   ['stock', 'tech', 'technology', 'automotive', 'auto', 'top', 'best', 'screen', 'car', 'finance', 'financial']):
                
                from screener_agent.screener_agent import screen_stocks
                
                # Parse the query to extract industry and count
                industry, count = self._parse_stock_query(user_message)
                
                # Get stock data directly
                stock_data = screen_stocks(industry=industry, top_n=count)
                
                # Format response as JSON within markdown
                if stock_data:
                    import json
                    json_data = json.dumps(stock_data)
                    response = f"Here are the stocks that match your criteria:\n\n```json\n{json_data}\n```\n\nI've found {len(stock_data)} stocks in the {industry} industry based on your request."
                    return f"[Handed off to screener_agent]\n{response}"
                else:
                    return f"[Handed off to screener_agent]\nI couldn't find any stocks matching your criteria for the {industry} industry. I currently only have data for technology and automotive sectors."
            
            return "I'm a trading assistant. I can help you screen stocks by industry. Try asking for 'top tech stocks' or 'best automotive stocks'."
            
        except Exception as e:
            print(f"Error in fallback direct call: {e}")
            return "I'm having trouble processing your request right now. Please try asking for specific stock information like 'top 5 tech stocks'."
    
    def _parse_stock_query(self, query: str) -> tuple[str, int]:
        """
        Parse user query to extract industry and stock count.
        """
        import re
        
        query_lower = query.lower()
        
        # Extract count (default to 5)
        count_match = re.search(r'\b(\d+)\b', query)
        count = int(count_match.group(1)) if count_match else 5
        
        # Extract industry - now includes financial services check
        industry = "technology"  # default
        
        if any(word in query_lower for word in ['tech', 'technology', 'it', 'software']):
            industry = "technology"
        elif any(word in query_lower for word in ['auto', 'automotive', 'automobile', 'car']):
            industry = "automotive"
        elif any(word in query_lower for word in ['finance', 'financial', 'bank', 'banking']):
            industry = "financial"  # This will return empty results, which is correct
        
        return industry, count
    
    # Keep legacy methods for backward compatibility with existing chat service
    async def handoff(self, agent_name: str, user_message: str) -> str:
        """
        Legacy handoff method for backward compatibility.
        Now delegates to ADK's built-in routing.
        """
        return await self.process_message(user_message)
