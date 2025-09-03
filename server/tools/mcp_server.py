"""
MCP Server for Trading Agent Tools.

This module sets up an MCP (Model Context Protocol) server that exposes
stock data service functions as tools for AI agents to use.
"""

import logging
import json
import asyncio
from typing import Any, Dict, List
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from mcp import types as mcp_types
from mcp.server.lowlevel import Server
from mcp.server.models import InitializationOptions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from service import stock_data_service

# Configure logging
logger = logging.getLogger(__name__)

# Global variable to hold the MCP server instance
mcp_server = None

class MCPStockDataServer:
    """MCP Server for stock data tools."""
    
    def __init__(self):
        self.server = Server("stock-data-mcp-server")
        self._setup_handlers()
    
    async def list_tools(self) -> List[mcp_types.Tool]:
        """List available tools."""
        return [
            mcp_types.Tool(
                name="get_historical_data",
                description="Get historical stock data for a given ticker",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, MSFT)"
                        },
                        "period": {
                            "type": "string",
                            "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                            "default": "1y"
                        },
                        "interval": {
                            "type": "string",
                            "description": "Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)",
                            "default": "1d"
                        }
                    },
                    "required": ["ticker"]
                }
            ),
            mcp_types.Tool(
                name="get_technical_indicators",
                description="Get technical indicators for a given ticker",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, MSFT)"
                        },
                        "period": {
                            "type": "string",
                            "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                            "default": "1y"
                        },
                        "indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of indicators to calculate (sma, ema, rsi, macd, bollinger)",
                            "default": ["sma", "rsi"]
                        }
                    },
                    "required": ["ticker"]
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[mcp_types.TextContent]:
        """Execute a tool call."""
        logger.info(f"🔧 MCP Server: TOOL CALL RECEIVED - {name}")
        logger.info(f"🔧 MCP Server: Tool arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            if name == "get_historical_data":
                ticker = arguments.get("ticker")
                period = arguments.get("period", "1y")
                interval = arguments.get("interval", "1d")
                
                logger.info(f"📊 MCP Server: Calling stock_data_service.get_historical_data({ticker}, {period}, {interval})")
                logger.info(f"📊 MCP Server: About to execute service call...")
                
                result = stock_data_service.get_historical_data(ticker, period, interval)   
                
                logger.info(f"✅ MCP Server: get_historical_data completed successfully")
                logger.info(f"✅ MCP Server: Result type: {type(result)}")
                logger.info(f"✅ MCP Server: Result preview: {str(result)[:300]}...")
                
                # Ensure the result is a JSON string if it's a dictionary
                if isinstance(result, dict):
                    result_text = json.dumps(result)
                else:
                    result_text = str(result) # It could be an error string
                    
                logger.info(f"📤 MCP Server: Returning result to agent (length: {len(result_text)})")
                return [mcp_types.TextContent(type="text", text=result_text)]
            
            elif name == "get_technical_indicators":
                ticker = arguments.get("ticker")
                period = arguments.get("period", "1y")
                indicators = arguments.get("indicators", ["sma", "rsi"])
                
                logger.info(f"📈 MCP Server: Calling stock_data_service.get_technical_indicators({ticker}, {period}, {indicators})")
                logger.info(f"📈 MCP Server: About to execute service call...")
                
                result = stock_data_service.get_technical_indicators(ticker, period, indicators)
                
                logger.info(f"✅ MCP Server: get_technical_indicators completed successfully")
                logger.info(f"✅ MCP Server: Result type: {type(result)}")
                logger.info(f"✅ MCP Server: Result preview: {str(result)[:300]}...")
                
                result_text = json.dumps(result)
                logger.info(f"📤 MCP Server: Returning result to agent (length: {len(result_text)})")
                return [mcp_types.TextContent(type="text", text=result_text)]
            
            else:
                logger.error(f"❌ MCP Server: Unknown tool requested: {name}")
                return [mcp_types.TextContent(
                    type="text", 
                    text=json.dumps({"error": f"Tool '{name}' not found"})
                )]
                
        except Exception as e:
            logger.error(f"❌ MCP Server: Error executing tool {name}: {e}")
            logger.error(f"❌ MCP Server: Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ MCP Server: Full traceback: {traceback.format_exc()}")
            return [mcp_types.TextContent(
                type="text", 
                text=json.dumps({"error": str(e)})
            )]
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[mcp_types.Tool]:
            return await self.list_tools()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[mcp_types.TextContent]:
            logger.info(f"🎯 MCP Handler: Tool call intercepted - {name}")
            logger.info(f"🎯 MCP Handler: Arguments: {json.dumps(arguments, indent=2)}")
            result = await self.call_tool(name, arguments)
            logger.info(f"🎯 MCP Handler: Tool execution completed")
            logger.info(f"🎯 MCP Handler: Result: {str(result)[:200]}...")
            return result

def initialize_mcp_server(main_app: FastAPI) -> None:
    """
    Initialize the MCP server with stock data tools.
    
    Args:
        main_app: The main FastAPI application instance
    """
    global mcp_server
    
    if mcp_server is not None:
        return
    
    try:
        # Create the MCP server instance
        mcp_server = MCPStockDataServer()
        
        # Add MCP endpoint to FastAPI app
        @main_app.post("/mcp")
        @main_app.get("/mcp")
        @main_app.options("/mcp")
        async def mcp_endpoint(request: Request):
            """Handle MCP requests via HTTP."""
            
            # Handle SSE connection for Google ADK
            #if request.headers.get("accept") == "text/event-stream":
            # Handle SSE connection for Google ADK (accept variations)
            accept = (request.headers.get("accept") or "").lower()
            if "text/event-stream" in accept:

                async def event_stream():
                    try:
                        # Send server capabilities immediately
                        capabilities_response = {
                            "jsonrpc": "2.0",
                            "method": "notifications/initialized",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {
                                    "tools": {
                                        "listChanged": True
                                    }
                                },
                                "serverInfo": {
                                    "name": "stock-data-mcp-server",
                                    "version": "1.0.0"
                                }
                            }
                        }
                        yield f"data: {json.dumps(capabilities_response)}\n\n"
                        
                        # Send available tools list
                        tools = await mcp_server.list_tools()
                        tools_response = {
                            "jsonrpc": "2.0",
                            "method": "notifications/tools/list_changed",
                            "params": {
                                "tools": [tool.model_dump() for tool in tools]
                            }
                        }
                        yield f"data: {json.dumps(tools_response)}\n\n"
                        
                        # Keep connection alive with heartbeat
                        while True:
                            await asyncio.sleep(30)
                            heartbeat = {
                                "jsonrpc": "2.0",
                                "method": "notifications/ping",
                                "params": {"timestamp": int(asyncio.get_event_loop().time())}
                            }
                            yield f"data: {json.dumps(heartbeat)}\n\n"
                    except Exception as e:
                        logger.error(f"Error in SSE stream: {e}")
                        error_response = {
                            "jsonrpc": "2.0",
                            "method": "notifications/error",
                            "params": {"error": str(e)}
                        }
                        yield f"data: {json.dumps(error_response)}\n\n"
                
                return StreamingResponse(
                    event_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    }
                )
            
            # Handle CORS preflight requests
            if request.method == "OPTIONS":
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Max-Age": "86400",
                    }
                )
            
            # Handle regular MCP protocol messages
            try:
                if request.method == "POST":
                    body = await request.json()
                    
                    # Handle different MCP methods
                    method = body.get("method")
                    request_id = body.get("id")
                    
                    if method == "initialize":
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {
                                    "tools": {}
                                },
                                "serverInfo": {
                                    "name": "stock-data-mcp-server",
                                    "version": "1.0.0"
                                }
                            }
                        }
                    elif method == "tools/list":
                        tools = await mcp_server.list_tools()
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "tools": [tool.model_dump() for tool in tools]
                            }
                        }
                    elif method == "tools/call":
                        params = body.get("params", {})
                        name = params.get("name")
                        arguments = params.get("arguments", {})
                        
                        logger.info(f"🚀 MCP Endpoint: Received tool call request - {name}")
                        logger.info(f"🚀 MCP Endpoint: Tool arguments: {json.dumps(arguments, indent=2)}")
                        
                        result = await mcp_server.call_tool(name, arguments)
                        
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [content.model_dump() for content in result]
                            }
                        }
                        
                        logger.info(f"📤 MCP Endpoint: Sending response back to agent")
                        logger.info(f"📤 MCP Endpoint: Response preview: {str(response_data)[:300]}...")
                    else:
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                else:
                    # GET request - return server info
                    response_data = {
                        "jsonrpc": "2.0", 
                        "id": "info", 
                        "result": {
                            "server": "stock-data-mcp-server",
                            "version": "1.0.0",
                            "capabilities": ["tools"],
                            "protocolVersion": "2024-11-05"
                        }
                    }
                
                return Response(
                    content=json.dumps(response_data),
                    media_type="application/json"
                )
                
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                return Response(
                    content=json.dumps({
                        "jsonrpc": "2.0",
                        "id": body.get("id", "error") if 'body' in locals() else "error",
                        "error": {"code": -32600, "message": str(e)}
                    }),
                    media_type="application/json",
                    status_code=400
                )
        
        logger.info("Successfully initialized MCP server with stock data tools")
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {e}")
        raise e
