import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from typing import List, Dict, Any, Optional
from backend.models.schemas import MoodType, PlaylistResponse, Track, UserPreferences
from datetime import datetime
import random

class SpotifyService:
    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Mood-based genre mappings
        self.mood_genres = {
            MoodType.HAPPY: ["pop", "dance", "funk", "soul", "reggae", "indie-pop"],
            MoodType.SAD: ["indie", "folk", "acoustic", "blues", "singer-songwriter", "ambient"],
            MoodType.ANXIOUS: ["ambient", "classical", "new-age", "meditation", "nature"],
            MoodType.ANGRY: ["rock", "metal", "punk", "alternative", "grunge"],
            MoodType.TIRED: ["ambient", "classical", "jazz", "lo-fi", "chill", "sleep"],
            MoodType.NEUTRAL: ["indie", "alternative", "pop", "rock", "electronic"],
            MoodType.MIXED: ["indie", "alternative", "experimental", "art-rock"]
        }
        
        # Energy level mappings based on intensity
        self.energy_mappings = {
            "low": {"energy": (0.0, 0.4), "valence": (0.0, 0.5)},
            "medium": {"energy": (0.3, 0.7), "valence": (0.3, 0.7)},
            "high": {"energy": (0.6, 1.0), "valence": (0.6, 1.0)}
        }

    async def generate_mood_playlist(
        self, 
        mood: MoodType, 
        intensity: int, 
        genres: Optional[List[str]] = None,
        user_preferences: Optional[UserPreferences] = None
    ) -> PlaylistResponse:
        """Generate a Spotify playlist based on mood and intensity"""
        
        try:
            # Determine energy level
            energy_level = "low" if intensity <= 3 else "medium" if intensity <= 7 else "high"
            
            # Get genres for this mood
            mood_genres = genres or self.mood_genres.get(mood, ["pop"])
            
            # Add user's favorite genres if available
            if user_preferences and user_preferences.favorite_genres:
                mood_genres.extend(user_preferences.favorite_genres)
            
            # Remove duplicates and limit
            mood_genres = list(set(mood_genres))[:5]
            
            # Get audio features for filtering
            energy_range = self.energy_mappings[energy_level]["energy"]
            valence_range = self.energy_mappings[energy_level]["valence"]
            
            # Search for tracks
            tracks = []
            for genre in mood_genres:
                try:
                    # Search for tracks in this genre
                    results = self.sp.search(
                        q=f"genre:{genre}",
                        type="track",
                        limit=20,
                        market="US"
                    )
                    
                    for track in results["tracks"]["items"]:
                        if len(tracks) >= 30:  # Limit total tracks
                            break
                            
                        # Get audio features
                        audio_features = self.sp.audio_features([track["id"]])[0]
                        if audio_features:
                            # Filter by energy and valence
                            if (energy_range[0] <= audio_features["energy"] <= energy_range[1] and
                                valence_range[0] <= audio_features["valence"] <= valence_range[1]):
                                
                                # Filter explicit content if needed
                                if user_preferences and not user_preferences.explicit_content and track["explicit"]:
                                    continue
                                
                                track_obj = Track(
                                    id=track["id"],
                                    title=track["name"],
                                    artist=", ".join([artist["name"] for artist in track["artists"]]),
                                    duration=track["duration_ms"] // 1000,
                                    url=track["external_urls"]["spotify"],
                                    preview_url=track["preview_url"],
                                    image_url=track["album"]["images"][0]["url"] if track["album"]["images"] else None
                                )
                                tracks.append(track_obj)
                
                except Exception as e:
                    print(f"Error searching genre {genre}: {e}")
                    continue
            
            # If no tracks found, get popular tracks
            if not tracks:
                tracks = await self._get_fallback_tracks(mood, intensity)
            
            # Shuffle and limit tracks
            random.shuffle(tracks)
            tracks = tracks[:20]
            
            # Calculate total duration
            total_duration = sum(track.duration for track in tracks)
            
            # Generate playlist name and description
            playlist_name = self._generate_playlist_name(mood, intensity)
            playlist_description = self._generate_playlist_description(mood, intensity)
            
            return PlaylistResponse(
                id=f"playlist_{datetime.utcnow().timestamp()}",
                name=playlist_name,
                description=playlist_description,
                tracks=tracks,
                total_duration=total_duration,
                mood_type=mood,
                intensity=intensity,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generating Spotify playlist: {e}")
            # Return fallback playlist
            return await self._get_fallback_playlist(mood, intensity)

    async def _get_fallback_tracks(self, mood: MoodType, intensity: int) -> List[Track]:
        """Get fallback tracks when genre search fails"""
        try:
            # Search for popular tracks with mood-related keywords
            mood_keywords = {
                MoodType.HAPPY: "happy upbeat positive",
                MoodType.SAD: "sad melancholy emotional",
                MoodType.ANXIOUS: "calm peaceful relaxing",
                MoodType.ANGRY: "intense powerful energetic",
                MoodType.TIRED: "chill ambient peaceful",
                MoodType.NEUTRAL: "popular trending",
                MoodType.MIXED: "indie alternative"
            }
            
            keyword = mood_keywords.get(mood, "popular")
            results = self.sp.search(q=keyword, type="track", limit=20, market="US")
            
            tracks = []
            for track in results["tracks"]["items"]:
                track_obj = Track(
                    id=track["id"],
                    title=track["name"],
                    artist=", ".join([artist["name"] for artist in track["artists"]]),
                    duration=track["duration_ms"] // 1000,
                    url=track["external_urls"]["spotify"],
                    preview_url=track["preview_url"],
                    image_url=track["album"]["images"][0]["url"] if track["album"]["images"] else None
                )
                tracks.append(track_obj)
            
            return tracks
            
        except Exception as e:
            print(f"Error getting fallback tracks: {e}")
            return []

    async def _get_fallback_playlist(self, mood: MoodType, intensity: int) -> PlaylistResponse:
        """Return a basic fallback playlist when all else fails"""
        return PlaylistResponse(
            id=f"fallback_{datetime.utcnow().timestamp()}",
            name=f"SafeSpace {mood.value.title()} Mix",
            description=f"A curated playlist for your {mood.value} mood",
            tracks=[],
            total_duration=0,
            mood_type=mood,
            intensity=intensity,
            created_at=datetime.utcnow()
        )

    def _generate_playlist_name(self, mood: MoodType, intensity: int) -> str:
        """Generate a creative playlist name"""
        intensity_words = {
            "low": ["Gentle", "Soft", "Light", "Mild"],
            "medium": ["Balanced", "Steady", "Moderate"],
            "high": ["Intense", "Deep", "Strong", "Powerful"]
        }
        
        mood_words = {
            MoodType.HAPPY: ["Joy", "Sunshine", "Bliss", "Celebration"],
            MoodType.SAD: ["Reflection", "Solace", "Comfort", "Healing"],
            MoodType.ANXIOUS: ["Calm", "Peace", "Serenity", "Tranquil"],
            MoodType.ANGRY: ["Release", "Power", "Energy", "Strength"],
            MoodType.TIRED: ["Rest", "Restore", "Recharge", "Peaceful"],
            MoodType.NEUTRAL: ["Balance", "Harmony", "Steady", "Flow"],
            MoodType.MIXED: ["Journey", "Complexity", "Layers", "Spectrum"]
        }
        
        intensity_level = "low" if intensity <= 3 else "medium" if intensity <= 7 else "high"
        intensity_word = random.choice(intensity_words[intensity_level])
        mood_word = random.choice(mood_words[mood])
        
        return f"{intensity_word} {mood_word}"

    def _generate_playlist_description(self, mood: MoodType, intensity: int) -> str:
        """Generate playlist description"""
        descriptions = {
            MoodType.HAPPY: f"Uplifting music to celebrate your joy (intensity: {intensity}/10)",
            MoodType.SAD: f"Gentle melodies for comfort and healing (intensity: {intensity}/10)",
            MoodType.ANXIOUS: f"Calming sounds to ease your mind (intensity: {intensity}/10)",
            MoodType.ANGRY: f"Powerful music to channel your energy (intensity: {intensity}/10)",
            MoodType.TIRED: f"Peaceful sounds for rest and restoration (intensity: {intensity}/10)",
            MoodType.NEUTRAL: f"Balanced music for your current mood (intensity: {intensity}/10)",
            MoodType.MIXED: f"Diverse sounds for complex emotions (intensity: {intensity}/10)"
        }
        
        return descriptions.get(mood, f"Music curated for your {mood.value} mood")