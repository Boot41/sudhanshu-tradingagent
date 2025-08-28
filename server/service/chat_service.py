from typing import Optional, List
from datetime import datetime
import uuid
import json
import re

from orchestrator import Orchestrator
from agent.agent_registry import AgentRegistry
from screener_agent.screener_agent import root_agent, screen_stocks
from schemas.chat_schema import ChatResponse, StockData, ErrorResponse

class ChatService:
    """Service for handling chat interactions with the orchestrator."""
    
    def __init__(self):
        """Initialize the chat service with orchestrator and agents."""
        self.registry = AgentRegistry()
        self._register_agents()
        self.orchestrator = Orchestrator(self.registry)
    
    def _register_agents(self):
        """Register all available agents with the registry."""
        # Register screener agent
        self.registry.register_agent(
            name="screener_agent",
            agent=root_agent,
            description="Screens and lists stocks based on user-defined criteria such as industry or performance metrics",
            capabilities=[
                "screen", "filter", "stocks", "industry", "performance", 
                "top", "best", "automotive", "technology", "tech", "auto"
            ]
        )
    
    async def process_message(self, message: str, user_id: Optional[int] = None, 
                            session_id: Optional[str] = None) -> ChatResponse:
        """
        Process a user message through the orchestrator.
        
        Args:
            message: User's message
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            ChatResponse with agent's response and any structured data
        """
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Process message through orchestrator
            response = await self.orchestrator.process_message(message)
            
            # Parse response to extract structured data if it's from screener agent
            agent_name, clean_response, stock_data = self._parse_agent_response(response)
            
            return ChatResponse(
                message=clean_response,
                agent_name=agent_name,
                data=stock_data,
                timestamp=datetime.utcnow(),
                session_id=session_id
            )
            
        except Exception as e:
            return ErrorResponse(
                error="processing_error",
                message=f"Error processing message: {str(e)}",
                timestamp=datetime.utcnow()
            )
    
    def _parse_agent_response(self, response: str) -> tuple[str, str, Optional[List[StockData]]]:
        """
        Parse agent response to extract agent name, clean message, and structured data.
        
        Args:
            response: Raw response from orchestrator
            
        Returns:
            Tuple of (agent_name, clean_response, stock_data)
        """
        agent_name = "Trading Assistant"
        stock_data = None
        clean_response = response
        
        # Check if response indicates handoff to screener agent
        if "[Handed off to screener_agent]" in response:
            agent_name = "Stock Screener"
            # Remove handoff indicator
            clean_response = response.replace("[Handed off to screener_agent]\n", "")
        
        # Always try to extract stock data from any response
        stock_data = self._extract_stock_data_from_response(clean_response)
        
        # If we found stock data, provide a clean user-friendly message
        if stock_data:
            agent_name = "Stock Screener"
            clean_response = f"I've screened the market and found {len(stock_data)} stocks that match your criteria:"
        else:
            # Clean up the response by removing agent instructions and technical details
            lines = clean_response.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip empty lines, agent instructions, and technical details
                if (not line or 
                    line.startswith('You are') or 
                    line.startswith('CRITICAL RULES:') or 
                    line.startswith('ALWAYS call') or
                    line.startswith('Extract industry') or
                    line.startswith('After calling') or
                    line.startswith('Do NOT provide') or
                    line.startswith('Return ONLY') or
                    line.startswith('Map synonyms:') or
                    line.startswith('Response format') or
                    line.startswith('WORKFLOW:') or
                    line.startswith('INPUT PARSING') or
                    line.startswith('SYNONYM MAPPING:') or
                    line.startswith('OUTPUT FORMAT:') or
                    line.startswith('[') or
                    'screen_stocks' in line.lower() or
                    'function' in line.lower() or
                    line.startswith('Here are the stocks') or
                    line.startswith('I\'ve found')):
                    continue
                cleaned_lines.append(line)
            
            clean_response = '\n'.join(cleaned_lines).strip()
            if not clean_response:
                clean_response = "I've processed your request. Please try asking for specific stock information."
        
        return agent_name, clean_response, stock_data
    
    def _extract_stock_data_from_response(self, response: str) -> Optional[List[StockData]]:
        """
        Extract structured stock data from screener agent response.
        
        Args:
            response: Response text from screener agent
            
        Returns:
            List of StockData objects if found, None otherwise
        """
        try:
            print(f"DEBUG: Parsing response: {response}")
            
            # First, handle markdown code blocks - extract content between ```json and ```
            markdown_json_pattern = r'```json\s*(\[.*?\])\s*```'
            markdown_match = re.search(markdown_json_pattern, response, re.DOTALL)
            if markdown_match:
                json_content = markdown_match.group(1).strip()
                print(f"DEBUG: Found markdown JSON: {json_content}")
                try:
                    data = json.loads(json_content)
                    if isinstance(data, list) and len(data) > 0:
                        stocks = []
                        for item in data:
                            if isinstance(item, dict):
                                # Handle both "ticker" and "name" as keys
                                ticker = item.get('ticker', '')
                                name = item.get('name', '')
                                performance = item.get('performance', 'N/A')
                                if ticker and name:
                                    stocks.append(StockData(
                                        ticker=ticker,
                                        name=name,
                                        performance=performance
                                    ))
                        print(f"DEBUG: Successfully parsed {len(stocks)} stocks from markdown JSON")
                        return stocks if stocks else None
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Markdown JSON decode error: {e}")
            
            # Second, try to find complete JSON arrays in the response
            # Look for patterns like [{"ticker": ...}, {"ticker": ...}]
            json_arrays = re.findall(r'\[(?:[^[\]]*(?:\{[^}]*\}[^[\]]*)*)*\]', response, re.DOTALL)
            
            for json_str in json_arrays:
                json_str = json_str.strip()
                if not json_str:
                    continue
                    
                try:
                    data = json.loads(json_str)
                    if isinstance(data, list) and len(data) > 0:
                        # Check if items look like stock data
                        first_item = data[0]
                        if isinstance(first_item, dict) and 'ticker' in first_item:
                            stocks = []
                            for item in data:
                                if isinstance(item, dict) and 'ticker' in item:
                                    stocks.append(StockData(
                                        ticker=item.get('ticker', ''),
                                        name=item.get('name', ''),
                                        performance=item.get('performance', 'N/A')
                                    ))
                            print(f"DEBUG: Successfully parsed {len(stocks)} stocks from JSON")
                            return stocks if stocks else None
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON decode error for: {json_str[:100]}... Error: {e}")
                    continue
            
            # Fallback: Look for specific JSON pattern with ticker
            json_pattern = r'\[\s*\{[^}]*"ticker"[^}]*\}(?:\s*,\s*\{[^}]*"ticker"[^}]*\})*\s*\]'
            json_match = re.search(json_pattern, response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                try:
                    stock_list = json.loads(json_str)
                    stocks = []
                    for item in stock_list:
                        if isinstance(item, dict) and 'ticker' in item:
                            stocks.append(StockData(
                                ticker=item.get('ticker', ''),
                                name=item.get('name', ''),
                                performance=item.get('performance', 'N/A')
                            ))
                    print(f"DEBUG: Fallback parsing found {len(stocks)} stocks")
                    return stocks if stocks else None
                except json.JSONDecodeError:
                    print(f"DEBUG: Fallback JSON parsing failed for: {json_str}")
                    pass
            
            # Fallback: Look for patterns in text (for backward compatibility)
            lines = response.split('\n')
            stocks = []
            
            for line in lines:
                # Look for ticker patterns (e.g., "TM", "INFY")
                ticker_match = re.search(r'\b([A-Z&]{2,6})\b', line)
                if ticker_match:
                    ticker = ticker_match.group(1)
                    
                    # Try to extract company name and performance
                    name_match = re.search(r'([A-Za-z\s&]+(?:Motors|Technologies|Consultancy|Services|Auto|Mahindra|Suzuki|Infosys|Wipro|HCL|Tech))', line)
                    perf_match = re.search(r'([+-]?\d+\.?\d*%)', line)
                    
                    if name_match:
                        name = name_match.group(1).strip()
                        performance = perf_match.group(1) if perf_match else "N/A"
                        
                        stocks.append(StockData(
                            ticker=ticker,
                            name=name,
                            performance=performance
                        ))
            
            return stocks if stocks else None
            
        except Exception as e:
            print(f"Error extracting stock data: {e}")
            return None

# Global instance
chat_service = ChatService()
