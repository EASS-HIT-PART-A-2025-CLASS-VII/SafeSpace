from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MoodType(str, Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    SAD = "sad"
    ANGRY = "angry"
    TIRED = "tired"
    MIXED = "mixed"

class SuggestionType(str, Enum):
    MUSIC = "music"
    BREATHING = "breathing"
    JOURNAL = "journal"
    GAME = "game"
    AUDIO = "audio"
    AFFIRMATION = "affirmation"

class MoodInput(BaseModel):
    mood_type: Optional[MoodType] = None
    intensity: Optional[int] = None
    text_input: Optional[str] = None
    voice_input: Optional[str] = None  # Base64 encoded audio
    quiz_responses: Optional[Dict[str, Any]] = None

class ParsedMood(BaseModel):
    mood_type: MoodType
    intensity: int
    confidence: float
    ai_message: str

class Suggestion(BaseModel):
    type: SuggestionType
    title: str
    description: str
    priority: int
    duration: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class MoodSuggestionResponse(BaseModel):
    mood_type: MoodType
    intensity: int
    suggestions: List[Suggestion]
    message: str

class PlaylistRequest(BaseModel):
    mood_type: MoodType
    intensity: int
    source: str = "ai"  # Always AI now
    genres: Optional[List[str]] = None
    duration_minutes: Optional[int] = 30

class Track(BaseModel):
    id: str
    title: str
    artist: str
    duration: int
    url: str
    preview_url: Optional[str] = None
    image_url: Optional[str] = None

class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: str
    tracks: List[Track]
    total_duration: int
    mood_type: MoodType
    intensity: int
    created_at: Optional[datetime] = None