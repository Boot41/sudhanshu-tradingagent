from fastapi import FastAPI
from api import auth
from db.db import create_tables, test_connection

app = FastAPI(
    title="Trading Agent API",
    description="API for the trading agent",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    if not test_connection():
        raise Exception("Database connection failed")
    create_tables()

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Trading Agent API"}
