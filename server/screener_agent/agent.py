"""ADK entrypoint module.

ADK expects `screener_agent.agent.root_agent` to exist.
We re-export the already-defined `root_agent` from `screener_agent.py`.
"""

from .screener_agent import root_agent  # noqa: F401
