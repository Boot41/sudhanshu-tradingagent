# /server/trader_agent/__init__.py

"""
ADK entrypoint for the screener app.

We expose a single `root_agent` from `.screener_agent` so ADK Web can load it.
Run from the parent directory (`server/`):
    adk web screener_agent
"""

from .screener_agent import root_agent  # re-export for ADK discovery
# Ensure screener_agent.agent is importable as an attribute on the package
from . import agent  # noqa: F401

__all__ = ["root_agent", "agent"]
