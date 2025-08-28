# Agent System

This directory contains the agent system for the trading application, including the agent registry and orchestration logic.

## Architecture

- `agent_registry.py`: Manages registration and lookup of agents
- `orchestrator.py`: Routes user requests to the appropriate agent

## Adding a New Agent

1. Create your agent in its own module (e.g., `screener_agent.py`)
2. Register it in `main.py`:

```python
from my_agent import my_agent

registry.register_agent(
    name="my_agent",
    agent=my_agent,
    description="Description of what the agent does",
    capabilities=["keyword1", "keyword2", "etc"]
)
```

## How It Works

1. The `AgentRegistry` maintains a list of available agents and their capabilities
2. The `Orchestrator` receives user messages and decides which agent should handle them
3. Routing is done using:
   - Direct keyword matching in the user's message
   - LLM-based routing for more complex queries
4. The `handoff` function is used to transfer control to another agent

## Example Usage

```python
# Initialize registry and register agents
registry = AgentRegistry()
registry.register_agent(
    name="screener_agent",
    agent=screener_agent,
    description="Screens stocks based on industry",
    capabilities=["stocks", "screener", "market"]
)

# Initialize orchestrator
orchestrator = Orchestrator(registry)

# Process a message
response = await orchestrator.process_message("Show me top tech stocks")
```
