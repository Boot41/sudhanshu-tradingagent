import asyncio
from agent.agent_registry import AgentRegistry
from screener_agent.screener_agent import root_agent as screener_agent
from orchestrator import Orchestrator

async def main():
    # Initialize agent registry
    registry = AgentRegistry()
    
    # Register the screener agent
    registry.register_agent(
        name="screener_agent",
        agent=screener_agent,
        description="Screens and lists stocks based on industry or performance metrics.",
        capabilities=["stock", "screener", "stocks", "market", "industry", "performance"]
    )
    
    # Initialize orchestrator
    orchestrator = Orchestrator(registry)
    
    # Example usage
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
                
            response = await orchestrator.process_message(user_input)
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
