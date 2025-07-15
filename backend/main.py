from fastapi import FastAPI, HTTPException
from fastapi import Depends
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import uvicorn
import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from database.mongodb import db
from auth.auth_service import auth_service
from mood_agent.mood_parser import MoodParser
from models.user import (
    UserCreate, UserLogin, JournalEntryCreate, JoyMomentCreate,
    UserPreferencesUpdate, UserResponse
)
from models.schemas import (
    MoodInput, PlaylistRequest,
    PlaylistResponse, MoodSuggestionResponse, Track
)

load_dotenv()

app = FastAPI(
    title="SafeSpace Mental Health API",
    description="Backend API for mood-based music recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
mood_parser = MoodParser()

# LLM Service client
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8080")


# Dependency to get current user from token
async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        token = authorization.replace("Bearer ", "")
        user = await auth_service.verify_token(token)
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await db.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from MongoDB on shutdown"""
    await db.disconnect()


@app.get("/")
async def root():
    return {"message": "SafeSpace Music Peeker API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["mood", "music", "ai"]}


# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await auth_service.create_user(user_data)

        # Create access token
        from models.user import UserLogin
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        auth_result = await auth_service.authenticate_user(login_data)

        return auth_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/api/auth/login")
async def login(user_login: UserLogin):
    """Login user"""
    try:
        result = await auth_service.authenticate_user(user_login)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login failed")


# Mood analysis with LLM integration
@app.post("/api/mood/analyze", response_model=MoodSuggestionResponse)
async def analyze_mood(mood_input: MoodInput, current_user: dict = Depends(get_current_user)):
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
            parsed_mood.intensity
        )

        # Save mood entry to database
        await db.save_mood_entry(current_user["id"], {
            "mood_type": parsed_mood.mood_type.value,
            "intensity": parsed_mood.intensity,
            "confidence": parsed_mood.confidence,
            "text_input": mood_input.text_input,
            "ai_message": parsed_mood.ai_message
        })

        return MoodSuggestionResponse(
            mood_type=parsed_mood.mood_type,
            intensity=parsed_mood.intensity,
            suggestions=suggestions,
            message=parsed_mood.ai_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AI-powered music playlist generation
@app.post("/api/music/playlist", response_model=PlaylistResponse)
async def generate_playlist(request: PlaylistRequest):
    try:
        # Always try to get playlist from LLM service first
        async with httpx.AsyncClient() as client:
            llm_response = await client.post(
                f"{LLM_SERVICE_URL}/generate-playlist",
                json={
                    "mood_type": request.mood_type.value,
                    "intensity": request.intensity,
                    "genres": request.genres,
                    "duration_minutes": request.duration_minutes or 30
                },
                timeout=300
            )

            if llm_response.status_code == 200:
                ai_data = llm_response.json()

                # Convert LLM response to our playlist format
                tracks = []
                if "songs" in ai_data and ai_data["songs"]:
                    for i, song in enumerate(ai_data["songs"][:12]):  # Limit to 12 songs
                        track = Track(
                            id=f"ai_track_{i}",
                            title=song.get("title", "Unknown Title"),
                            artist=song.get("artist", "Unknown Artist"),
                            duration=180,  # Default 3 minutes
                            url=f"#track_{i}",  # Placeholder URL
                            preview_url=None,
                            image_url=None
                        )
                        tracks.append(track)

                    # Create AI playlist response
                    playlist_response = PlaylistResponse(
                        id=f"ai_playlist_{request.mood_type}_{request.intensity}",
                        name=ai_data.get("playlist_name", f"AI {request.mood_type.title()} Mix"),
                        description=ai_data.get("description", f"AI-curated music for your {request.mood_type} mood"),
                        tracks=tracks,
                        total_duration=sum(track.duration for track in tracks),
                        mood_type=request.mood_type,
                        intensity=request.intensity,
                        created_at=None
                    )

                    return playlist_response

            # If we get here, the LLM service responded but didn't have songs
            # The LLM service should handle its own fallbacks, so this is an error
            raise HTTPException(status_code=500, detail="LLM service returned empty playlist")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="LLM service timeout - please try again")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="LLM service unavailable - please check if it's running")
    except Exception as e:
        print(f"Playlist generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate playlist: {str(e)}")


# AI-powered affirmations endpoint
@app.post("/api/ai/affirmations")
async def get_ai_affirmations(mood_type: str, intensity: int):
    try:
        # Always try to get affirmations from LLM service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE_URL}/generate-affirmations",
                json={
                    "mood_type": mood_type,
                    "intensity": intensity,
                    "user_name": "Friend",
                    "context": f"User feeling {mood_type} at intensity {intensity}"
                },
                timeout=300
            )

            if response.status_code == 200:
                return response.json()
            else:
                # LLM service responded with error
                raise HTTPException(status_code=response.status_code, detail="LLM service error")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="LLM service timeout - please try again")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="LLM service unavailable - please check if it's running")
    except Exception as e:
        print(f"Affirmations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmations: {str(e)}")


# Journal endpoints
@app.post("/api/journal/entries")
async def create_journal_entry(entry: JournalEntryCreate, current_user: dict = Depends(get_current_user)):
    """Create a new journal entry"""
    try:
        await db.save_journal_entry(current_user["id"], {
            "content": entry.content,
            "prompt": entry.prompt,
            "mood": entry.mood
        })
        return {"message": "Journal entry saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save journal entry")


@app.get("/api/journal/entries")
async def get_journal_entries(current_user: dict = Depends(get_current_user)):
    """Get user's journal entries"""
    try:
        entries = await db.get_journal_entries(current_user["id"])
        return {"entries": entries}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get journal entries")


# Joy Jar endpoints
@app.post("/api/joy/moments")
async def create_joy_moment(moment: JoyMomentCreate, current_user: dict = Depends(get_current_user)):
    """Create a new joy moment"""
    try:
        await db.save_joy_moment(current_user["id"], {
            "title": moment.title,
            "description": moment.description
        })
        return {"message": "Joy moment saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save joy moment")


@app.get("/api/joy/moments")
async def get_joy_moments(current_user: dict = Depends(get_current_user)):
    """Get user's joy moments"""
    try:
        moments = await db.get_joy_moments(current_user["id"])
        return {"moments": moments}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get joy moments")


@app.delete("/api/joy/moments/{moment_id}")
async def delete_joy_moment(moment_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a joy moment"""
    try:
        await db.delete_joy_moment(current_user["id"], moment_id)
        return {"message": "Joy moment deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete joy moment")


# User data endpoints
@app.get("/api/user/mood-history")
async def get_mood_history(current_user: dict = Depends(get_current_user)):
    """Get user's mood history"""
    try:
        history = await db.get_mood_history(current_user["id"])
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get mood history")


@app.get("/api/user/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    try:
        profile = await auth_service.get_user_profile(current_user["id"])
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user profile")


@app.put("/api/user/preferences")
async def update_user_preferences(
        preferences: UserPreferencesUpdate,
        current_user: dict = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        # Get current preferences
        user = await db.get_user_by_id(current_user["id"])
        current_prefs = user.get("preferences", {})

        # Update only provided fields
        update_data = preferences.dict(exclude_unset=True)
        current_prefs.update(update_data)

        await db.update_user_preferences(current_user["id"], current_prefs)
        return {"message": "Preferences updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update preferences")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)