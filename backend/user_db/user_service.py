import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.models.schemas import (
    User, UserPreferences, MoodEntry, PlaylistResponse, 
    ParsedMood, MoodType
)

class UserService:
    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.passwords_file = os.path.join(self.data_dir, "passwords.json")
        self.mood_history_file = os.path.join(self.data_dir, "mood_history.json")
        self.playlist_history_file = os.path.join(self.data_dir, "playlist_history.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        for file_path in [self.users_file, self.passwords_file, self.mood_history_file, self.playlist_history_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return {}

    def _save_json(self, file_path: str, data: Dict[str, Any]):
        """Save JSON data to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    async def create_user(self, user: User, hashed_password: str):
        """Create a new user"""
        # Save user data
        users = self._load_json(self.users_file)
        users[user.id] = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "preferences": user.preferences.dict(),
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        self._save_json(self.users_file, users)
        
        # Save password
        passwords = self._load_json(self.passwords_file)
        passwords[user.id] = hashed_password
        self._save_json(self.passwords_file, passwords)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        users = self._load_json(self.users_file)
        for user_data in users.values():
            if user_data["email"] == email:
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    name=user_data["name"],
                    preferences=UserPreferences(**user_data["preferences"]),
                    created_at=datetime.fromisoformat(user_data["created_at"]),
                    last_login=datetime.fromisoformat(user_data["last_login"]) if user_data["last_login"] else None
                )
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        users = self._load_json(self.users_file)
        if user_id in users:
            user_data = users[user_id]
            return User(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                preferences=UserPreferences(**user_data["preferences"]),
                created_at=datetime.fromisoformat(user_data["created_at"]),
                last_login=datetime.fromisoformat(user_data["last_login"]) if user_data["last_login"] else None
            )
        return None

    async def get_user_password(self, user_id: str) -> Optional[str]:
        """Get user's hashed password"""
        passwords = self._load_json(self.passwords_file)
        return passwords.get(user_id)

    async def update_last_login(self, user_id: str):
        """Update user's last login time"""
        users = self._load_json(self.users_file)
        if user_id in users:
            users[user_id]["last_login"] = datetime.utcnow().isoformat()
            self._save_json(self.users_file, users)

    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences"""
        user = await self.get_user_by_id(user_id)
        return user.preferences if user else UserPreferences()

    async def update_user_preferences(self, user_id: str, preferences: UserPreferences) -> UserPreferences:
        """Update user preferences"""
        users = self._load_json(self.users_file)
        if user_id in users:
            users[user_id]["preferences"] = preferences.dict()
            self._save_json(self.users_file, users)
        return preferences

    async def save_mood_entry(self, user_id: str, mood: ParsedMood):
        """Save a mood entry"""
        mood_history = self._load_json(self.mood_history_file)
        
        if user_id not in mood_history:
            mood_history[user_id] = []
        
        entry = MoodEntry(
            id=f"mood_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            mood_type=mood.mood_type,
            intensity=mood.intensity,
            timestamp=datetime.utcnow(),
            context=mood.ai_message
        )
        
        mood_history[user_id].append({
            "id": entry.id,
            "user_id": entry.user_id,
            "mood_type": entry.mood_type.value,
            "intensity": entry.intensity,
            "timestamp": entry.timestamp.isoformat(),
            "context": entry.context
        })
        
        # Keep only last 100 entries per user
        mood_history[user_id] = mood_history[user_id][-100:]
        
        self._save_json(self.mood_history_file, mood_history)

    async def get_mood_history(self, user_id: str) -> List[MoodEntry]:
        """Get user's mood history"""
        mood_history = self._load_json(self.mood_history_file)
        user_history = mood_history.get(user_id, [])
        
        entries = []
        for entry_data in user_history:
            entry = MoodEntry(
                id=entry_data["id"],
                user_id=entry_data["user_id"],
                mood_type=MoodType(entry_data["mood_type"]),
                intensity=entry_data["intensity"],
                timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                context=entry_data.get("context")
            )
            entries.append(entry)
        
        return sorted(entries, key=lambda x: x.timestamp, reverse=True)

    async def save_playlist(self, user_id: str, playlist: PlaylistResponse):
        """Save a generated playlist"""
        playlist_history = self._load_json(self.playlist_history_file)
        
        if user_id not in playlist_history:
            playlist_history[user_id] = []
        
        playlist_data = {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "tracks": [track.dict() for track in playlist.tracks],
            "total_duration": playlist.total_duration,
            "mood_type": playlist.mood_type.value,
            "intensity": playlist.intensity,
            "created_at": playlist.created_at.isoformat()
        }
        
        playlist_history[user_id].append(playlist_data)
        
        # Keep only last 50 playlists per user
        playlist_history[user_id] = playlist_history[user_id][-50:]
        
        self._save_json(self.playlist_history_file, playlist_history)

    async def get_playlist_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's playlist history"""
        playlist_history = self._load_json(self.playlist_history_file)
        user_history = playlist_history.get(user_id, [])
        
        return sorted(user_history, key=lambda x: x["created_at"], reverse=True)