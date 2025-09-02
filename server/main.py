from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, chat
from db.db import create_tables, test_connection
from tools.mcp_server import initialize_mcp_server
import uvicorn

app = FastAPI(
    title="Trading Agent API",
    description="API for the trading agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:8081", "http://127.0.0.1:8081", "http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    if not test_connection():
        raise Exception("Database connection failed")
    create_tables()
    
    # Initialize the MCP server
    initialize_mcp_server(app)
    print("MCP server initialized and mounted at /mcp with tools: get_historical_data, get_technical_indicators")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Trading Agent API"}


if __name__ == "__main__":
    # The reload=True argument enables auto-reloading
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
