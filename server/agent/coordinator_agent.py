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

    Here is your workflow:
    1.  **Analyze the user's prompt.**
    2.  **Decision Point:**
        *   If the prompt is a simple greeting (e.g., "hi", "hello"), respond with a friendly message introducing yourself as a trading assistant.
        *   If the prompt is a request for a chart, graph, or plot, delegate to the `VisualizerAgent`.
        *   If the prompt is a request for a recommendation (buy/sell/hold), delegate to the `RecommendationAgent`.
    3.  **Handle Specialist Agent Output:**
        *   After calling a specialist agent, it will return a JSON object.
        *   Your task is to **immediately return the full and exact JSON output** from the specialist agent.
        *   **CRITICAL:** Do not add any text, explanation, or commentary. Your final response must be ONLY the JSON provided by the specialist agent. This is the final step.
    """
)

# Export as root_agent for the agent registry
root_agent = coordinator_agent
