from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any, Union
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

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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
    source: str = "spotify"  # "spotify" or "youtube"
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
    created_at: datetime

class UserPreferences(BaseModel):
    favorite_genres: List[str] = []
    preferred_music_source: str = "spotify"
    language: str = "en"
    explicit_content: bool = False
    preferred_activities: List[SuggestionType] = []
    notification_settings: Dict[str, bool] = {}

class MoodEntry(BaseModel):
    id: str
    user_id: str
    mood_type: MoodType
    intensity: int
    timestamp: datetime
    context: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    name: str
    preferences: UserPreferences
    created_at: datetime
    last_login: Optional[datetime] = None