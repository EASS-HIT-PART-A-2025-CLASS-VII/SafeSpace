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
    songs: List[Dict[str, str]]
    playlist_name: str
    description: str
    mood_description: str


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

    def _run_ollama(self, prompt: str) -> str:
        try:
            result = subprocess.run(
                ["ollama", "run", "gemma:2b", prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300
            )
            if result.returncode != 0:
                raise Exception("LLM process failed")
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise Exception("LLM service unavailable")

    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}')
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end + 1]
                return json.loads(json_str)
        except:
            pass

        # If no JSON found, return empty dict
        return {}

    async def generate_playlist_prompt(self, request: PlaylistRequest) -> PlaylistResponse:
        mood_context = self.mood_contexts.get(request.mood_type, "balanced")
        intensity_modifier = (
            "very intense, deep, powerful" if request.intensity >= 8 else
            "moderate, noticeable, present" if request.intensity >= 6 else
            "mild, gentle, subtle" if request.intensity >= 4 else
            "very light, barely noticeable, soft"
        )

        prompt = f"""
You are a music recommendation assistant. Create a playlist for someone feeling {request.mood_type} with intensity {request.intensity}/10.

Context: {mood_context}, {intensity_modifier}
Duration: {request.duration_minutes} minutes

Generate 8-12 real songs (from 1980-2025) that fit this mood. Include both popular and lesser-known songs.

Respond with ONLY a JSON object in this exact format:
{{
  "songs": [
    {{"title": "Song Title", "artist": "Artist Name"}},
    {{"title": "Another Song", "artist": "Another Artist"}}
  ],
  "playlist_name": "Playlist Name",
  "description": "Brief description",
  "mood_description": "How this music helps with the mood"
}}
"""

        try:
            response = self._run_ollama(prompt)
            data = self._extract_json_from_response(response)

            if not data or "songs" not in data:
                # Fallback response
                return self._get_fallback_playlist(request)

            return PlaylistResponse(**data)

        except Exception as e:
            logger.error(f"Playlist generation error: {e}")
            return self._get_fallback_playlist(request)

    async def generate_affirmations(self, request: AffirmationRequest) -> AffirmationResponse:
        mood_context = self.mood_contexts.get(request.mood_type, "balanced")

        prompt = f"""
You are a kind mental health support assistant. Create personalized affirmations for someone feeling {request.mood_type} at intensity {request.intensity}/10.

User context: {request.context or 'General support needed'}
Name: {request.user_name or 'Friend'}

Create 5 supportive affirmations using "I" statements. Also provide a personalized message and breathing instruction if needed.

Respond with ONLY a JSON object in this exact format:
{{
  "affirmations": [
    "affirmation 1",
    "affirmation 2",
    "affirmation 3",
    "affirmation 4",
    "affirmation 5"
  ],
  "personalized_message": "A warm, supportive message",
  "breathing_instruction": "Breathing instruction if helpful"
}}
"""

        try:
            response = self._run_ollama(prompt)
            data = self._extract_json_from_response(response)

            if not data or "affirmations" not in data:
                return self._get_fallback_affirmations(request)

            return AffirmationResponse(**data)

        except Exception as e:
            logger.error(f"Affirmations generation error: {e}")
            return self._get_fallback_affirmations(request)

    def _get_fallback_playlist(self, request: PlaylistRequest) -> PlaylistResponse:
        """Fallback playlist when AI fails"""
        fallback_songs = {
            "happy": [
                {"title": "Happy", "artist": "Pharrell Williams"},
                {"title": "Good as Hell", "artist": "Lizzo"},
                {"title": "Can't Stop the Feeling", "artist": "Justin Timberlake"},
                {"title": "Walking on Sunshine", "artist": "Katrina and the Waves"}
            ],
            "sad": [
                {"title": "Someone Like You", "artist": "Adele"},
                {"title": "Mad World", "artist": "Gary Jules"},
                {"title": "Hurt", "artist": "Johnny Cash"},
                {"title": "Black", "artist": "Pearl Jam"}
            ],
            "anxious": [
                {"title": "Weightless", "artist": "Marconi Union"},
                {"title": "Clair de Lune", "artist": "Claude Debussy"},
                {"title": "Aqueous Transmission", "artist": "Incubus"},
                {"title": "Spiegel im Spiegel", "artist": "Arvo Pärt"}
            ],
            "angry": [
                {"title": "Break Stuff", "artist": "Limp Bizkit"},
                {"title": "Bodies", "artist": "Drowning Pool"},
                {"title": "Killing in the Name", "artist": "Rage Against the Machine"},
                {"title": "Chop Suey!", "artist": "System of a Down"}
            ],
            "tired": [
                {"title": "Sleepyhead", "artist": "Passion Pit"},
                {"title": "Dream a Little Dream", "artist": "Ella Fitzgerald"},
                {"title": "Weightless", "artist": "Marconi Union"},
                {"title": "Gymnopédie No. 1", "artist": "Erik Satie"}
            ],
            "neutral": [
                {"title": "Breathe", "artist": "Pink Floyd"},
                {"title": "Comfortably Numb", "artist": "Pink Floyd"},
                {"title": "The Sound of Silence", "artist": "Simon & Garfunkel"},
                {"title": "Mad World", "artist": "Tears for Fears"}
            ],
            "mixed": [
                {"title": "Everybody Hurts", "artist": "R.E.M."},
                {"title": "Losing Religion", "artist": "R.E.M."},
                {"title": "Creep", "artist": "Radiohead"},
                {"title": "Black", "artist": "Pearl Jam"}
            ]
        }

        songs = fallback_songs.get(request.mood_type, fallback_songs["neutral"])

        return PlaylistResponse(
            songs=songs,
            playlist_name=f"AI {request.mood_type.title()} Mix",
            description=f"A curated playlist for your {request.mood_type} mood",
            mood_description=f"Music to support your {request.mood_type} feelings"
        )

    def _get_fallback_affirmations(self, request: AffirmationRequest) -> AffirmationResponse:
        """Fallback affirmations when AI fails"""
        mood_affirmations = {
            "happy": [
                "I deserve this happiness and joy",
                "I am grateful for this beautiful moment",
                "I radiate positivity and light",
                "I celebrate my achievements and growth",
                "I share my joy with the world around me"
            ],
            "sad": [
                "I allow myself to feel and process my emotions",
                "I am worthy of love and compassion",
                "This sadness is temporary and will pass",
                "I am stronger than I know",
                "I give myself permission to heal at my own pace"
            ],
            "anxious": [
                "I am safe in this moment",
                "I can handle whatever comes my way",
                "I breathe deeply and find my center",
                "I trust in my ability to cope",
                "I am grounded and present"
            ],
            "angry": [
                "I acknowledge my anger without judgment",
                "I can express my feelings in healthy ways",
                "I have the power to choose my response",
                "I release what I cannot control",
                "I channel my energy toward positive change"
            ],
            "tired": [
                "I deserve rest and restoration",
                "I honor my body's need for peace",
                "I am gentle with myself today",
                "I have done enough for today",
                "I allow myself to simply be"
            ],
            "neutral": [
                "I am exactly where I need to be",
                "I trust the process of life",
                "I am open to whatever this moment brings",
                "I find peace in the present",
                "I am enough, just as I am"
            ],
            "mixed": [
                "I can hold multiple feelings at once",
                "I am complex and that's perfectly okay",
                "I give myself space to feel everything",
                "I trust my emotional wisdom",
                "I am learning and growing through this experience"
            ]
        }

        affirmations = mood_affirmations.get(request.mood_type, mood_affirmations["neutral"])

        return AffirmationResponse(
            affirmations=affirmations,
            personalized_message=f"You're being so brave by acknowledging your {request.mood_type} feelings. That takes real courage.",
            breathing_instruction="Take a slow, deep breath in for 4 counts, hold for 4, then exhale for 6 counts" if request.mood_type in [
                "anxious", "angry", "sad"] else None
        )


# --- Initialize service ---
llm_service = LLMService()


@app.get("/")
async def root():
    return {"message": "SafeSpace LLM Service (Ollama)", "status": "running"}


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

    uvicorn.run(app, host="0.0.0.0", port=8080)