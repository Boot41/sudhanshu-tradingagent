#!/usr/bin/env python3
"""Test script to verify agent functionality."""

import asyncio
import sys
import os

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service.chat_service import chat_service

async def test_screener_agent():
    """Test the screener agent with various queries."""
    test_queries = [
        "top 5 tech stocks",
        "best 3 automotive stocks", 
        "technology stocks",
        "auto stocks"
    ]
    
    print("Testing Screener Agent...")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        
        try:
            response = await chat_service.process_message(query)
            print(f"Agent: {response.agent_name}")
            print(f"Message: {response.message}")
            
            if response.data:
                print(f"Stock Data ({len(response.data)} items):")
                for stock in response.data:
                    print(f"  - {stock.ticker}: {stock.name} ({stock.performance})")
            else:
                print("No structured stock data returned")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_screener_agent())
