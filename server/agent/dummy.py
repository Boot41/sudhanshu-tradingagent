from google.adk import Agent
from service.stock_data_service import get_technical_indicators

dummy_agent = Agent(
    name="dummy_agent",
    model="gemini-2.0-flash",
    description="Agent that always calls the technical indicators tool and returns its result directly.",
    tools=[get_technical_indicators],
    instruction="""
You must ALWAYS call the `get_technical_indicators` tool with the stock ticker extracted from the user request.
Do not guess or fabricate values.
Do not add explanations or extra formatting.

Return ONLY the tool’s JSON response, unchanged.
"""
)
