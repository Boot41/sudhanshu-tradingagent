from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Import all the specialist agents that this coordinator can command.
from .visualizer_agent import visualizer_agent
from .recommendation_agent import recommendation_agent

# Create a list of 'AgentTool's. This wraps each specialist agent so the
# coordinator's LLM can treat them as callable functions. The LLM will read the
# 'description' of each agent to make its routing decision.
agent_tools = [
    agent_tool.AgentTool(agent=visualizer_agent),
    agent_tool.AgentTool(agent=recommendation_agent),
]

# Define the Coordinator Agent
coordinator_agent = LlmAgent(
    name="CoordinatorAgent",
    model="gemini-1.5-flash",
    description="I am the master stock trading assistant. I understand a user's request and delegate the task to the correct specialist agent from my team.",
    # The coordinator's tools are the other agents.
    tools=agent_tools,
    instruction="""
    You are the central coordinator for a team of specialist financial AI agents.
    Your job is to understand the user's prompt and either respond directly for simple greetings or delegate to the appropriate specialist agent.
    
    For simple greetings like "hi", "hello", or general questions, respond directly with a friendly message about being a trading assistant.
    
    For specific tasks:
    - If the user wants to see a chart, graph, or plot, use the 'VisualizerAgent'.
    - If the user wants a buy/sell/hold signal or recommendation, use the 'RecommendationAgent'.
    
    After calling a specialist agent, directly return its full and exact output. Do not add any extra text, explanation, or commentary. Your response should be ONLY the specialist agent's response.
    """
)

# Export as root_agent for the agent registry
root_agent = coordinator_agent
