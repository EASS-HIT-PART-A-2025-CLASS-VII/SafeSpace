from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import httpx
from dotenv import load_dotenv

from mood_agent.mood_parser import MoodParser
from models.schemas import (
    MoodInput, PlaylistRequest,
    PlaylistResponse, MoodSuggestionResponse, Track
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
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
mood_parser = MoodParser()

# LLM Service client
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8080")


@app.get("/")
async def root():
    return {"message": "SafeSpace Music Peeker API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["mood", "music", "ai"]}


# Mood analysis with LLM integration
@app.post("/api/mood/analyze", response_model=MoodSuggestionResponse)
async def analyze_mood(mood_input: MoodInput):
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
                    return PlaylistResponse(
                        id=f"ai_playlist_{request.mood_type}_{request.intensity}",
                        name=ai_data.get("playlist_name", f"AI {request.mood_type.title()} Mix"),
                        description=ai_data.get("description", f"AI-curated music for your {request.mood_type} mood"),
                        tracks=tracks,
                        total_duration=sum(track.duration for track in tracks),
                        mood_type=request.mood_type,
                        intensity=request.intensity,
                        created_at=None
                    )

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)