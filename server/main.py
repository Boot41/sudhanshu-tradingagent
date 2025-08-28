from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth
from db.db import create_tables, test_connection

app = FastAPI(
    title="Trading Agent API",
    description="API for the trading agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
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

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Trading Agent API"}
