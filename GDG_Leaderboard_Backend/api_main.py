from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables (ensure this is before db is imported if db relies on them)
load_dotenv()

# Import our custom database operations after dotenv is loaded
from database import db 

app = FastAPI(
    title="GDG Leaderboard API (CSV-Driven)",
    description="API for Google Cloud Study Jams 2025 Leaderboard, populated from CSV data, with no Discord dependency.",
    version="1.0.0",
)

# Load CORS_ORIGINS from .env
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()] # Handle empty strings

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/custom/leaderboard", summary="Get top performers leaderboard")
async def get_leaderboard_endpoint():
    """
    Retrieves the top performers for the Google Cloud Study Jams 2025 leaderboard,
    displaying specific CSV-derived columns.
    """
    leaderboard_data = db.get_leaderboard()
    if not leaderboard_data:
        raise HTTPException(status_code=500, detail="Could not retrieve leaderboard data")
    return leaderboard_data

@app.get("/custom/all_progress", summary="Get all users' progress data")
async def get_all_progress_endpoint():
    """
    Retrieves progress data for all verified users, displaying specific CSV-derived columns.
    """
    all_progress_data = db.get_all_user_progress()
    if not all_progress_data:
        raise HTTPException(status_code=500, detail="Could not retrieve all user progress data")
    return all_progress_data

@app.get("/custom/stats", summary="Get overall program statistics")
async def get_stats_endpoint():
    """
    Retrieves overall statistics for the program.
    """
    stats_data = db.get_stats()
    if not stats_data:
        raise HTTPException(status_code=500, detail="Could not retrieve statistics data")
    return stats_data

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "GDG Leaderboard API (CSV-Driven) is running. Access docs at /docs or custom endpoints like /custom/leaderboard"}

if __name__ == "__main__":
    port = int(os.getenv("FASTAPI_PORT", 8000))
    print(f"🚀 Starting FastAPI Server on http://0.0.0.0:{port}")
    print(f"📚 FastAPI docs: http://127.0.0.1:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)