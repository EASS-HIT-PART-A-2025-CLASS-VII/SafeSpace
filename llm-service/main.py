from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import subprocess
import json
import logging

app = FastAPI(
    title="SafeSpace LLM Service (Ollama Edition)",
    description="AI-powered playlist generation and affirmation service using local LLMs",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# --- Pydantic Models ---
class MoodRequest(BaseModel):
    mood_type: str
    intensity: int
    user_preferences: Optional[Dict[str, Any]] = None
    context: Optional[str] = None

class PlaylistRequest(BaseModel):
    mood_type: str
    intensity: int
    genres: Optional[List[str]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    duration_minutes: Optional[int] = 30

class AffirmationRequest(BaseModel):
    mood_type: str
    intensity: int
    user_name: Optional[str] = None
    context: Optional[str] = None

class PlaylistResponse(BaseModel):
    playlist_prompt: str
    suggested_genres: List[str]
    energy_level: str
    mood_description: str
    search_terms: List[str]

class AffirmationResponse(BaseModel):
    affirmations: List[str]
    personalized_message: str
    breathing_instruction: Optional[str] = None

# --- LLMService class ---
class LLMService:
    def __init__(self):
        self.mood_contexts = {
            "happy": "joyful, celebratory, uplifting, energetic",
            "sad": "comforting, gentle, healing, supportive",
            "anxious": "calming, peaceful, grounding, soothing",
            "angry": "releasing, powerful, channeling, grounding",
            "tired": "restful, peaceful, restorative, gentle",
            "neutral": "balanced, contemplative, steady, versatile",
            "mixed": "complex, understanding, adaptive, supportive"
        }

    def _run_ollama(self, prompt: str) -> Dict:
        result = subprocess.run(
            ["ollama", "run", "gemma:2b", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise Exception("LLM process failed")
        output = result.stdout
        logger.info(f"Raw LLM Output: {output}")
        json_start = output.find('{')
        json_end = output.rfind('}')
        if json_start == -1 or json_end == -1:
            raise Exception("No valid JSON found")
        return json.loads(output[json_start:json_end + 1])

    async def generate_playlist_prompt(self, request: PlaylistRequest) -> PlaylistResponse:
        mood_context = self.mood_contexts.get(request.mood_type, "balanced")
        intensity_modifier = (
            "very intense, deep, powerful" if request.intensity >= 8 else
            "moderate, noticeable, present" if request.intensity >= 6 else
            "mild, gentle, subtle" if request.intensity >= 4 else
            "very light, barely noticeable, soft"
        )

        prompt = f"""
You are a music recommendation assistant.
User's current mood is {request.mood_type} with intensity {request.intensity}/10.
Context: {mood_context}, Duration: {request.duration_minutes} mins.
Suggest 8–12 real songs (1980–2025) fitting the mood. Include popular + lesser-known songs.
Return ONLY JSON array of: [{{ "title": "Song Title", "artist": "Artist Name" }}]
"""
        songs = self._run_ollama(prompt)
        genres = ["pop", "indie", "ambient", "electronic"][:5]
        energy_level = "high" if request.intensity >= 6 else "medium"
        search_terms = [request.mood_type, "music", "playlist"]

        return PlaylistResponse(
            playlist_prompt=f"A {intensity_modifier} playlist for a {request.mood_type} mood",
            suggested_genres=genres,
            energy_level=energy_level,
            mood_description=f"{intensity_modifier} {mood_context} music",
            search_terms=search_terms
        )

    async def generate_affirmations(self, request: AffirmationRequest) -> AffirmationResponse:
        mood_context = self.mood_contexts.get(request.mood_type, "balanced")
        prompt = f"""
You are a kind mental health support assistant.

Given this mood:
- Mood: {request.mood_type}
- Intensity: {request.intensity}
- Name: {request.user_name or 'Friend'}
- Context: {request.context or 'None'}

Provide JSON:
{{
  "affirmations": ["..."],
  "personalized_message": "...",
  "breathing_instruction": "..."
}}
"""
        data = self._run_ollama(prompt)
        return AffirmationResponse(**data)

# --- Initialize service ---
llm_service = LLMService()

@app.get("/")
async def root():
    return {"message": "SafeSpace LLM Service (Gemma)", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm-service"}

@app.post("/generate-playlist", response_model=PlaylistResponse)
async def generate_playlist(request: PlaylistRequest):
    try:
        return await llm_service.generate_playlist_prompt(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate playlist: {str(e)}")

@app.post("/generate-affirmations", response_model=AffirmationResponse)
async def generate_affirmations(request: AffirmationRequest):
    try:
        return await llm_service.generate_affirmations(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmations: {str(e)}")

@app.post("/analyze-mood")
async def analyze_mood(request: MoodRequest):
    return {
        "mood_analysis": f"Detected {request.mood_type} mood at intensity {request.intensity}",
        "ai_insights": f"Focus on self-care activities based on {request.mood_type} mood.",
        "suggested_activities": ["music", "breathing", "journaling"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
