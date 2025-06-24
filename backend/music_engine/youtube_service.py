from youtubesearchpython import VideosSearch
import requests
from typing import List, Dict, Any, Optional
from backend.models.schemas import MoodType, PlaylistResponse, Track, UserPreferences
from datetime import datetime
import random
import re

class YouTubeService:
    def __init__(self):
        # Mood-based search terms
        self.mood_search_terms = {
            MoodType.HAPPY: ["happy music", "upbeat songs", "feel good music", "positive vibes", "joyful music"],
            MoodType.SAD: ["sad music", "emotional songs", "melancholy music", "heartbreak songs", "comfort music"],
            MoodType.ANXIOUS: ["calming music", "relaxing songs", "anxiety relief", "peaceful music", "meditation music"],
            MoodType.ANGRY: ["intense music", "rock music", "powerful songs", "energy music", "release music"],
            MoodType.TIRED: ["sleep music", "ambient music", "chill music", "peaceful sounds", "rest music"],
            MoodType.NEUTRAL: ["popular music", "trending songs", "indie music", "alternative music"],
            MoodType.MIXED: ["indie music", "alternative songs", "experimental music", "diverse playlist"]
        }

    async def generate_mood_playlist(
        self, 
        mood: MoodType, 
        intensity: int, 
        genres: Optional[List[str]] = None,
        user_preferences: Optional[UserPreferences] = None
    ) -> PlaylistResponse:
        """Generate a YouTube playlist based on mood and intensity"""
        
        try:
            # Get search terms for this mood
            search_terms = self.mood_search_terms.get(mood, ["music"])
            
            # Add genre-specific terms if provided
            if genres:
                search_terms.extend([f"{genre} music" for genre in genres])
            
            # Adjust search terms based on intensity
            if intensity >= 8:
                search_terms = [f"intense {term}" for term in search_terms]
            elif intensity <= 3:
                search_terms = [f"gentle {term}" for term in search_terms]
            
            tracks = []
            
            # Search for videos
            for search_term in search_terms[:3]:  # Limit search terms
                try:
                    videos_search = VideosSearch(search_term, limit=10)
                    results = videos_search.result()
                    
                    for video in results["result"]:
                        if len(tracks) >= 25:  # Limit total tracks
                            break
                        
                        # Filter out non-music content
                        if self._is_music_video(video):
                            # Parse duration
                            duration = self._parse_duration(video.get("duration", "0:00"))
                            
                            # Skip very long videos (likely not songs)
                            if duration > 600:  # 10 minutes
                                continue
                            
                            track = Track(
                                id=video["id"],
                                title=self._clean_title(video["title"]),
                                artist=video["channel"]["name"],
                                duration=duration,
                                url=video["link"],
                                preview_url=None,  # YouTube doesn't provide preview URLs
                                image_url=video["thumbnails"][0]["url"] if video["thumbnails"] else None
                            )
                            tracks.append(track)
                
                except Exception as e:
                    print(f"Error searching YouTube for '{search_term}': {e}")
                    continue
            
            # If no tracks found, get fallback tracks
            if not tracks:
                tracks = await self._get_fallback_tracks(mood)
            
            # Shuffle and limit tracks
            random.shuffle(tracks)
            tracks = tracks[:20]
            
            # Calculate total duration
            total_duration = sum(track.duration for track in tracks)
            
            # Generate playlist name and description
            playlist_name = self._generate_playlist_name(mood, intensity)
            playlist_description = self._generate_playlist_description(mood, intensity)
            
            return PlaylistResponse(
                id=f"yt_playlist_{datetime.utcnow().timestamp()}",
                name=playlist_name,
                description=playlist_description,
                tracks=tracks,
                total_duration=total_duration,
                mood_type=mood,
                intensity=intensity,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            print(f"Error generating YouTube playlist: {e}")
            return await self._get_fallback_playlist(mood, intensity)

    def _is_music_video(self, video: Dict[str, Any]) -> bool:
        """Check if a video is likely a music video"""
        title = video.get("title", "").lower()
        channel = video.get("channel", {}).get("name", "").lower()
        
        # Music indicators
        music_indicators = [
            "official", "music", "audio", "song", "album", "single",
            "lyrics", "acoustic", "live", "cover", "remix"
        ]
        
        # Non-music indicators
        non_music_indicators = [
            "tutorial", "how to", "review", "reaction", "interview",
            "documentary", "news", "podcast", "vlog"
        ]
        
        # Check for music indicators
        has_music_indicator = any(indicator in title or indicator in channel for indicator in music_indicators)
        
        # Check for non-music indicators
        has_non_music_indicator = any(indicator in title for indicator in non_music_indicators)
        
        return has_music_indicator and not has_non_music_indicator

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        try:
            # Handle formats like "3:45" or "1:23:45"
            parts = duration_str.split(":")
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            else:
                return 0
        except:
            return 0

    def _clean_title(self, title: str) -> str:
        """Clean video title to extract song name"""
        # Remove common YouTube title additions
        title = re.sub(r'\[.*?\]', '', title)  # Remove [Official Video], etc.
        title = re.sub(r'\(.*?Official.*?\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\(.*?Video.*?\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\(.*?Audio.*?\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'HD|4K|Official|Video|Audio', '', title, flags=re.IGNORECASE)
        
        return title.strip()

    async def _get_fallback_tracks(self, mood: MoodType) -> List[Track]:
        """Get fallback tracks when search fails"""
        try:
            # Simple search with mood name
            videos_search = VideosSearch(f"{mood.value} music", limit=15)
            results = videos_search.result()
            
            tracks = []
            for video in results["result"]:
                duration = self._parse_duration(video.get("duration", "0:00"))
                if duration > 0 and duration <= 600:  # Valid duration
                    track = Track(
                        id=video["id"],
                        title=self._clean_title(video["title"]),
                        artist=video["channel"]["name"],
                        duration=duration,
                        url=video["link"],
                        preview_url=None,
                        image_url=video["thumbnails"][0]["url"] if video["thumbnails"] else None
                    )
                    tracks.append(track)
            
            return tracks
            
        except Exception as e:
            print(f"Error getting fallback tracks: {e}")
            return []

    async def _get_fallback_playlist(self, mood: MoodType, intensity: int) -> PlaylistResponse:
        """Return a basic fallback playlist when all else fails"""
        return PlaylistResponse(
            id=f"yt_fallback_{datetime.utcnow().timestamp()}",
            name=f"SafeSpace {mood.value.title()} Mix",
            description=f"A curated YouTube playlist for your {mood.value} mood",
            tracks=[],
            total_duration=0,
            mood_type=mood,
            intensity=intensity,
            created_at=datetime.utcnow()
        )

    def _generate_playlist_name(self, mood: MoodType, intensity: int) -> str:
        """Generate a creative playlist name"""
        intensity_words = {
            "low": ["Gentle", "Soft", "Light"],
            "medium": ["Balanced", "Steady"],
            "high": ["Intense", "Deep", "Strong"]
        }
        
        mood_words = {
            MoodType.HAPPY: ["Vibes", "Energy", "Joy"],
            MoodType.SAD: ["Feels", "Comfort", "Solace"],
            MoodType.ANXIOUS: ["Calm", "Peace", "Zen"],
            MoodType.ANGRY: ["Power", "Release", "Energy"],
            MoodType.TIRED: ["Rest", "Chill", "Peaceful"],
            MoodType.NEUTRAL: ["Flow", "Balance", "Steady"],
            MoodType.MIXED: ["Journey", "Spectrum", "Layers"]
        }
        
        intensity_level = "low" if intensity <= 3 else "medium" if intensity <= 7 else "high"
        intensity_word = random.choice(intensity_words[intensity_level])
        mood_word = random.choice(mood_words[mood])
        
        return f"{intensity_word} {mood_word} Mix"

    def _generate_playlist_description(self, mood: MoodType, intensity: int) -> str:
        """Generate playlist description"""
        return f"YouTube music curated for your {mood.value} mood (intensity: {intensity}/10)"