from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import httpx
from dotenv import load_dotenv

from auth.auth_service import AuthService
from mood_agent.mood_parser import MoodParser
from music_engine.spotify_service import SpotifyService
from music_engine.youtube_service import YouTubeService
from user_db.user_service import UserService
from models.schemas import (
    UserCreate, UserLogin, MoodInput, PlaylistRequest, 
    PlaylistResponse, UserPreferences, MoodSuggestionResponse
)

load_dotenv()

app = FastAPI(
    title="SafeSpace Music Peeker API",
    description="Backend API for mood-based music recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Services
auth_service = AuthService()
mood_parser = MoodParser()
spotify_service = SpotifyService()
youtube_service = YouTubeService()
user_service = UserService()

# LLM Service client
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8001")

@app.get("/")
async def root():
    return {"message": "SafeSpace Music Peeker API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["auth", "mood", "music", "user"]}

# Auth endpoints
@app.post("/auth/register")
async def register(user_data: UserCreate):
    try:
        user = await auth_service.create_user(user_data)
        return {"message": "User created successfully", "user_id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(credentials: UserLogin):
    try:
        token = await auth_service.authenticate_user(credentials)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Protected route helper
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = await auth_service.verify_token(credentials.credentials)
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Enhanced mood analysis with LLM integration
@app.post("/mood/analyze", response_model=MoodSuggestionResponse)
async def analyze_mood(
    mood_input: MoodInput,
    current_user = Depends(get_current_user)
):
    try:
        # Parse mood from various inputs
        parsed_mood = await mood_parser.parse_mood(mood_input)
        
        # Get AI-enhanced suggestions from LLM service
        try:
            async with httpx.AsyncClient() as client:
                llm_response = await client.post(
                    f"{LLM_SERVICE_URL}/analyze-mood",
                    json={
                        "mood_type": parsed_mood.mood_type.value,
                        "intensity": parsed_mood.intensity,
                        "user_preferences": current_user.preferences.dict(),
                        "context": mood_input.text_input
                    },
                    timeout=10.0
                )
                if llm_response.status_code == 200:
                    llm_data = llm_response.json()
                    # Enhance suggestions with AI insights
                    ai_insights = llm_data.get("ai_insights", "")
                    parsed_mood.ai_message = f"{parsed_mood.ai_message} {ai_insights}"
        except Exception as e:
            print(f"LLM service unavailable: {e}")
            # Continue with regular suggestions
        
        # Get intelligent suggestions based on mood and intensity
        suggestions = await mood_parser.get_intelligent_suggestions(
            parsed_mood.mood_type, 
            parsed_mood.intensity,
            current_user.preferences
        )
        
        # Save mood entry
        await user_service.save_mood_entry(current_user.id, parsed_mood)
        
        return MoodSuggestionResponse(
            mood_type=parsed_mood.mood_type,
            intensity=parsed_mood.intensity,
            suggestions=suggestions,
            message=parsed_mood.ai_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced music endpoints with LLM integration
@app.post("/music/playlist", response_model=PlaylistResponse)
async def generate_playlist(
    request: PlaylistRequest,
    current_user = Depends(get_current_user)
):
    try:
        # Get AI-enhanced playlist recommendations from LLM service
        enhanced_request = request
        try:
            async with httpx.AsyncClient() as client:
                llm_response = await client.post(
                    f"{LLM_SERVICE_URL}/generate-playlist",
                    json={
                        "mood_type": request.mood_type.value,
                        "intensity": request.intensity,
                        "genres": request.genres,
                        "user_preferences": current_user.preferences.dict(),
                        "duration_minutes": request.duration_minutes
                    },
                    timeout=15.0
                )
                if llm_response.status_code == 200:
                    llm_data = llm_response.json()
                    # Use AI-suggested genres and search terms
                    enhanced_request.genres = llm_data.get("suggested_genres", request.genres)
        except Exception as e:
            print(f"LLM service unavailable for playlist generation: {e}")
        
        # Generate playlist based on mood and preferences
        if request.source == "spotify":
            playlist = await spotify_service.generate_mood_playlist(
                enhanced_request.mood_type,
                enhanced_request.intensity,
                enhanced_request.genres,
                current_user.preferences
            )
        else:
            playlist = await youtube_service.generate_mood_playlist(
                enhanced_request.mood_type,
                enhanced_request.intensity,
                enhanced_request.genres,
                current_user.preferences
            )
        
        # Save playlist to user history
        await user_service.save_playlist(current_user.id, playlist)
        
        return playlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New AI-powered affirmations endpoint
@app.post("/ai/affirmations")
async def get_ai_affirmations(
    mood_type: str,
    intensity: int,
    current_user = Depends(get_current_user)
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE_URL}/generate-affirmations",
                json={
                    "mood_type": mood_type,
                    "intensity": intensity,
                    "user_name": current_user.name,
                    "context": f"User feeling {mood_type} at intensity {intensity}"
                },
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=500, detail="AI service unavailable")
    except Exception as e:
        # Fallback affirmations
        fallback_affirmations = {
            "affirmations": [
                "You are worthy of love and compassion",
                "This feeling is temporary and will pass",
                "You have the strength to get through this"
            ],
            "personalized_message": "You're taking great care of yourself by being here.",
            "breathing_instruction": "Take a slow, deep breath in for 4 counts, hold for 4, then exhale for 6 counts"
        }
        return fallback_affirmations

# User preferences
@app.get("/user/preferences")
async def get_user_preferences(current_user = Depends(get_current_user)):
    try:
        preferences = await user_service.get_user_preferences(current_user.id)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/user/preferences")
async def update_user_preferences(
    preferences: UserPreferences,
    current_user = Depends(get_current_user)
):
    try:
        updated_preferences = await user_service.update_user_preferences(
            current_user.id, 
            preferences
        )
        return updated_preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User history
@app.get("/user/mood-history")
async def get_mood_history(current_user = Depends(get_current_user)):
    try:
        history = await user_service.get_mood_history(current_user.id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/playlist-history")
async def get_playlist_history(current_user = Depends(get_current_user)):
    try:
        history = await user_service.get_playlist_history(current_user.id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)