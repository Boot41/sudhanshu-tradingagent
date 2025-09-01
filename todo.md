# Trading Agent TODO

## Pending Tasks

### MCP Server Enhancements
- [ ] **Add industry peers functionality**: Implement `get_industry_peers` method in `server/service/stock_data_service.py` and register it as a tool in `server/tools/mcp_server.py`
  - Research and implement industry peer comparison logic
  - Add appropriate type hints and documentation
  - Register the new method in the MCP server tools list

- yet to configure mcp server port fastapi port and linking to the front end chat endpoint


## Completed Tasks
- [x] Created tools folder structure
- [x] Set up MCP server with existing stock data service methods
- [x] Registered `get_historical_data` and `get_technical_indicators` as tools
