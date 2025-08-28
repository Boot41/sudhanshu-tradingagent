"""Agent registry for managing and routing to different agents."""
from typing import Dict, Type, Optional, Any

class AgentRegistry:
    """Registry for managing different agents."""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
    
    def register_agent(self, name: str, agent: Any, description: str, 
                      capabilities: list[str]) -> None:
        """Register a new agent with its metadata."""
        self.agents[name] = {
            'agent': agent,
            'description': description,
            'capabilities': capabilities
        }
    
    def get_agent(self, name: str) -> Optional[Any]:
        """Retrieve an agent by name."""
        agent_info = self.agents.get(name)
        return agent_info['agent'] if agent_info else None
    
    def list_agents(self) -> Dict[str, dict]:
        """List all registered agents with their metadata."""
        return {name: {
            'description': info['description'],
            'capabilities': info['capabilities']
        } for name, info in self.agents.items()}
    
    def find_best_agent(self, user_prompt: str) -> tuple[Optional[str], float]:
        """Find the best matching agent for the given user prompt."""
        # Simple keyword-based routing - can be enhanced with embeddings/ML later
        prompt_lower = user_prompt.lower()
        
        best_agent = None
        best_score = 0.0
        
        for agent_name, agent_info in self.agents.items():
            score = 0
            # Check for keywords in capabilities
            for capability in agent_info['capabilities']:
                if capability.lower() in prompt_lower:
                    score += 1
            
            # Check for agent name in prompt
            if agent_name.lower() in prompt_lower:
                score += 2
                
            if score > best_score:
                best_score = score
                best_agent = agent_name
        
        return best_agent, best_score
