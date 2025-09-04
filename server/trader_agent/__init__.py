"""
Trading Agent System - Root Agent Export

This module exports the coordinator agent as the root agent for Google ADK.
The coordinator agent contains the complete trading analysis workflow.
"""

from .coordinator_agent import CoordinatorAgent

# Export the coordinator agent as root_agent for Google ADK
root_agent = CoordinatorAgent

__all__ = ['root_agent', 'CoordinatorAgent']
