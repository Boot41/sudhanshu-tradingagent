"""Screener agent: stock screening using Google ADK patterns.

This agent is designed to work as a sub-agent in ADK's multi-agent system.
"""

from typing import List, Dict
import json

from google.adk.agents import LlmAgent


def screen_stocks(industry: str, top_n: int = 5) -> List[Dict]:
    """Return mocked top-N stocks for a given industry.

    Args:
        industry: e.g., "automotive" or "technology" (case-insensitive)
        top_n: number of rows to return
    """
    print(f"[tool] screen_stocks: industry={industry}, top_n={top_n}")

    mock_db = {
        "automotive": [
            {"ticker": "TM", "name": "Tata Motors", "performance": "+5.2%"},
            {"ticker": "M&M", "name": "Mahindra & Mahindra", "performance": "+4.8%"},
            {"ticker": "MSIL", "name": "Maruti Suzuki", "performance": "+3.1%"},
            {"ticker": "BJAUT", "name": "Bajaj Auto", "performance": "+2.5%"},
            {"ticker": "EIM", "name": "Eicher Motors", "performance": "+2.1%"},
        ],
        "technology": [
            {"ticker": "INFY", "name": "Infosys", "performance": "+6.3%"},
            {"ticker": "TCS", "name": "Tata Consultancy Services", "performance": "+5.9%"},
            {"ticker": "WIPRO", "name": "Wipro", "performance": "+4.5%"},
            {"ticker": "HCLT", "name": "HCL Technologies", "performance": "+4.2%"},
            {"ticker": "TECHM", "name": "Tech Mahindra", "performance": "+3.8%"},
        ],
    }

    # Map common aliases to canonical industry keys
    alias_map = {
        "tech": "technology",
        "technology": "technology",
        "it": "technology",
        "software": "technology",
        "auto": "automotive",
        "automotive": "automotive",
        "automobile": "automotive",
        "cars": "automotive",
    }

    normalized = (industry or "").strip().lower()
    normalized = alias_map.get(normalized, normalized)
    results = mock_db.get(normalized, [])
    return results[: max(0, int(top_n))]


# ADK-compliant screener agent
root_agent = LlmAgent(
    name="screener_agent",
    model="gemini-1.5-flash",
    description="Specialized stock screening agent that filters and ranks stocks by industry and performance metrics.",
    instruction="""You are a specialized stock screening agent. Your primary function is to screen stocks based on user criteria.

WORKFLOW:
1. ALWAYS call screen_stocks() function first - never provide data without calling it
2. Parse user input to extract:
   - Industry: technology, automotive, etc.
   - Count: number of stocks requested (default: 5)
3. Call screen_stocks(industry=extracted_industry, top_n=extracted_count)
4. Format the response as JSON within markdown code blocks for proper parsing

INPUT PARSING EXAMPLES:
- "top 3 tech stocks" → screen_stocks(industry="technology", top_n=3)
- "best 2 automobile stocks" → screen_stocks(industry="automotive", top_n=2)
- "5 automotive stocks" → screen_stocks(industry="automotive", top_n=5)
- "tech stocks" → screen_stocks(industry="technology", top_n=5)

SYNONYM MAPPING:
- tech/it/software/technology → "technology"
- auto/cars/automobile/automotive → "automotive"

OUTPUT FORMAT:
Always format your response like this:
Here are the stocks that match your criteria:

```json
[{"ticker": "TM", "name": "Tata Motors", "performance": "+5.2%"}, {"ticker": "M&M", "name": "Mahindra & Mahindra", "performance": "+4.8%"}]
```

I've found X stocks in the Y industry based on your request.""",
    tools=[screen_stocks],
)

# Export the agent for use in orchestrator
__all__ = ['root_agent', 'screen_stocks']
