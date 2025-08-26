"""Screener app: mocked tool and root agent.

Run from parent directory `server/`:
    adk web screener_agent
"""

from typing import List, Dict

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


# Root agent that uses the mocked tool
root_agent = LlmAgent(
    name="screener_agent",
    model="gemini-1.5-flash",
    description=(
        "Screens and lists stocks based on user-defined criteria such as industry or performance metrics."
    ),
    instruction=
    """
    You are a specialized stock screening agent.
    Your goal is to call the `screen_stocks(industry, top_n)` tool with the best possible
    arguments inferred from the user's message.

    Rules:
    - Infer parameters from free text (e.g., "top 3 tech stock" -> industry=technology, top_n=3).
    - Map synonyms: tech/it/software -> technology; auto/cars/automobile -> automotive.
    - If any parameter is missing, ask a short clarifying question. If the user doesn't clarify,
      pick sensible defaults: industry=technology, top_n=5.
    - Always call `screen_stocks` to produce the final answer. Do not fabricate data.
    - Respond concisely with a list of {ticker, name, performance}.

    Examples:
    - User: "top 3 tech stock"
      Action: screen_stocks(industry="technology", top_n=3)

    - User: "screen automotive industry, top 5"
      Action: screen_stocks(industry="automotive", top_n=5)
    """,
    tools=[screen_stocks],
)
