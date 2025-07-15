from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserPreferences(BaseModel):
    """User preferences for personalized experience"""
    favorite_genres: List[str] = Field(default_factory=list)
    explicit_content: bool = True
    preferred_session_length: int = 30  # minutes
    reminder_notifications: bool = False
    theme_preference: str = "auto"  # auto, light, dark


class MoodType(str, Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    SAD = "sad"
    ANGRY = "angry"
    TIRED = "tired"
    MIXED = "mixed"


class User(BaseModel):
    """Main user model"""
    id: Optional[str] = None
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    hashed_password: str
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Model for user response (without password)"""
    id: str
    email: str
    name: str
    preferences: UserPreferences
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool


class MoodEntry(BaseModel):
    """Model for mood tracking entries"""
    id: Optional[str] = None
    user_id: str
    mood_type: MoodType
    intensity: int = Field(..., ge=1, le=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    text_input: Optional[str] = None
    ai_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class JournalEntry(BaseModel):
    """Model for journal entries"""
    id: Optional[str] = None
    user_id: str
    content: str = Field(..., min_length=1)
    prompt: Optional[str] = None
    mood: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class JoyMoment(BaseModel):
    """Model for joy jar moments"""
    id: Optional[str] = None
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Request/Response models for API
class JournalEntryCreate(BaseModel):
    content: str = Field(..., min_length=1)
    prompt: Optional[str] = None
    mood: str


class JoyMomentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)


class UserPreferencesUpdate(BaseModel):
    favorite_genres: Optional[List[str]] = None
    explicit_content: Optional[bool] = None
    preferred_session_length: Optional[int] = None
    reminder_notifications: Optional[bool] = None
    theme_preference: Optional[str] = None