import json
import re
from typing import List, Dict, Any, Optional
from models.schemas import MoodInput, ParsedMood, MoodType, Suggestion, SuggestionType


class MoodParser:
    def __init__(self):
        # Mood keywords for text analysis
        self.mood_keywords = {
            MoodType.HAPPY: ["happy", "joy", "excited", "great", "amazing", "wonderful", "fantastic", "cheerful",
                             "elated"],
            MoodType.SAD: ["sad", "depressed", "down", "blue", "melancholy", "upset", "crying", "tears", "heartbroken"],
            MoodType.ANXIOUS: ["anxious", "worried", "nervous", "stressed", "panic", "fear", "overwhelmed", "tense"],
            MoodType.ANGRY: ["angry", "mad", "furious", "irritated", "frustrated", "rage", "annoyed", "pissed"],
            MoodType.TIRED: ["tired", "exhausted", "drained", "weary", "sleepy", "fatigue", "worn out", "depleted"],
            MoodType.NEUTRAL: ["okay", "fine", "normal", "average", "meh", "alright"],
            MoodType.MIXED: ["confused", "mixed", "complicated", "conflicted", "unsure", "complex"]
        }

    async def parse_mood(self, mood_input: MoodInput) -> ParsedMood:
        """Parse mood from various input sources"""

        # If mood_type and intensity are directly provided
        if mood_input.mood_type and mood_input.intensity:
            return ParsedMood(
                mood_type=mood_input.mood_type,
                intensity=mood_input.intensity,
                confidence=1.0,
                ai_message=self._generate_mood_message(mood_input.mood_type, mood_input.intensity)
            )

        # Parse from text input
        if mood_input.text_input:
            return await self._parse_from_text(mood_input.text_input)

        # Parse from quiz responses
        if mood_input.quiz_responses:
            return await self._parse_from_quiz(mood_input.quiz_responses)

        # Default fallback
        return ParsedMood(
            mood_type=MoodType.NEUTRAL,
            intensity=5,
            confidence=0.5,
            ai_message="I'm here to support you. How are you feeling today?"
        )

    async def _parse_from_text(self, text: str) -> ParsedMood:
        """Analyze text to determine mood"""
        text_lower = text.lower()
        mood_scores = {}

        # Score each mood based on keyword matches
        for mood, keywords in self.mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                mood_scores[mood] = score

        # Determine primary mood
        if mood_scores:
            primary_mood = max(mood_scores, key=mood_scores.get)
            confidence = min(mood_scores[primary_mood] / 3, 1.0)
        else:
            primary_mood = MoodType.NEUTRAL
            confidence = 0.3

        # Estimate intensity based on text intensity
        intensity = self._estimate_intensity_from_text(text_lower, primary_mood)

        return ParsedMood(
            mood_type=primary_mood,
            intensity=intensity,
            confidence=confidence,
            ai_message=self._generate_mood_message(primary_mood, intensity)
        )

    async def _parse_from_quiz(self, quiz_responses: Dict[str, Any]) -> ParsedMood:
        """Parse mood from quiz responses"""
        # Simple quiz scoring logic
        mood_scores = {mood: 0 for mood in MoodType}

        for question, answer in quiz_responses.items():
            if isinstance(answer, str):
                for mood, keywords in self.mood_keywords.items():
                    if any(keyword in answer.lower() for keyword in keywords):
                        mood_scores[mood] += 1
            elif isinstance(answer, int):
                # Assume numeric answers contribute to intensity
                pass

        primary_mood = max(mood_scores, key=mood_scores.get) if any(mood_scores.values()) else MoodType.NEUTRAL
        intensity = min(max(sum(mood_scores.values()), 1), 10)

        return ParsedMood(
            mood_type=primary_mood,
            intensity=intensity,
            confidence=0.8,
            ai_message=self._generate_mood_message(primary_mood, intensity)
        )

    def _estimate_intensity_from_text(self, text: str, mood: MoodType) -> int:
        """Estimate intensity based on text analysis"""
        intensity_indicators = {
            "extremely": 10, "very": 8, "really": 7, "quite": 6,
            "somewhat": 4, "a bit": 3, "slightly": 2, "barely": 1
        }

        base_intensity = 5
        for indicator, value in intensity_indicators.items():
            if indicator in text:
                base_intensity = value
                break

        # Adjust based on punctuation and caps
        if "!!!" in text or text.isupper():
            base_intensity = min(base_intensity + 2, 10)
        elif "!" in text:
            base_intensity = min(base_intensity + 1, 10)

        return base_intensity

    def _generate_mood_message(self, mood: MoodType, intensity: int) -> str:
        """Generate appropriate AI message based on mood and intensity"""
        messages = {
            MoodType.HAPPY: {
                "low": "I can sense some happiness in you today. That's wonderful!",
                "medium": "You're feeling pretty good! I love seeing your positive energy.",
                "high": "You're radiating joy! This is beautiful to witness."
            },
            MoodType.SAD: {
                "low": "I can feel a bit of sadness. I'm here with you.",
                "medium": "You're going through a tough time. You're not alone in this.",
                "high": "I can feel your deep sadness. Please know that you're cared for."
            },
            MoodType.ANXIOUS: {
                "low": "I sense some worry. Let's find some calm together.",
                "medium": "Your anxiety is understandable. We can work through this.",
                "high": "I can feel your intense anxiety. You're safe right now."
            },
            MoodType.ANGRY: {
                "low": "I can sense some frustration. Your feelings are valid.",
                "medium": "You're feeling quite angry. Let's find a healthy way to process this.",
                "high": "Your anger is intense right now. Let's channel this energy safely."
            },
            MoodType.TIRED: {
                "low": "You seem a bit tired. Rest is important.",
                "medium": "You're feeling quite drained. You deserve care and rest.",
                "high": "You're completely exhausted. Please be gentle with yourself."
            },
            MoodType.NEUTRAL: {
                "low": "You're feeling pretty balanced today.",
                "medium": "You seem to be in a neutral space. How can I support you?",
                "high": "You're feeling steady. What would be helpful right now?"
            },
            MoodType.MIXED: {
                "low": "You're experiencing some complex feelings.",
                "medium": "There's a lot going on emotionally. That's completely normal.",
                "high": "You're feeling many things at once. Let's take this step by step."
            }
        }

        intensity_level = "low" if intensity <= 3 else "medium" if intensity <= 7 else "high"
        return messages[mood][intensity_level]

    async def get_intelligent_suggestions(
            self,
            mood: MoodType,
            intensity: int
    ) -> List[Suggestion]:
        """Generate intelligent suggestions based on mood and intensity"""

        suggestions = []

        # Define suggestion logic based on mood and intensity
        if mood == MoodType.HAPPY:
            if intensity >= 7:
                suggestions.extend([
                    Suggestion(type=SuggestionType.MUSIC, title="AI Celebration Playlist",
                               description="AI-curated upbeat music to match your joy", priority=1),
                    Suggestion(type=SuggestionType.JOURNAL, title="Joy Jar Entry",
                               description="Capture this moment forever", priority=2),
                ])
            else:
                suggestions.extend([
                    Suggestion(type=SuggestionType.MUSIC, title="Feel-Good AI Music",
                               description="Light, positive tunes from AI", priority=1),
                    Suggestion(type=SuggestionType.AFFIRMATION, title="Positive Affirmations",
                               description="AI-generated positive intentions", priority=2),
                ])

        elif mood == MoodType.TIRED:
            if intensity >= 8:
                suggestions.extend([
                    Suggestion(type=SuggestionType.AUDIO, title="Sleep Sounds",
                               description="Gentle sounds for deep rest", priority=1, duration=1800),
                    Suggestion(type=SuggestionType.BREATHING, title="Restorative Breathing",
                               description="Breathing for exhaustion", priority=2, duration=600),
                ])
            elif intensity >= 5:
                suggestions.extend([
                    Suggestion(type=SuggestionType.MUSIC, title="AI Calming Music",
                               description="Soft AI-generated music for tired souls", priority=1),
                    Suggestion(type=SuggestionType.JOURNAL, title="Gentle Reflection",
                               description="What's one thing you're proud of today?", priority=2),
                ])
            else:
                suggestions.extend([
                    Suggestion(type=SuggestionType.MUSIC, title="Gentle AI Energy",
                               description="Soft AI music to lift your spirits", priority=1),
                    Suggestion(type=SuggestionType.BREATHING, title="Energizing Breath",
                               description="Gentle breathing to restore energy", priority=2, duration=300),
                ])

        elif mood == MoodType.ANXIOUS:
            if intensity >= 8:
                suggestions.extend([
                    Suggestion(type=SuggestionType.BREATHING, title="4-7-8 Breathing",
                               description="Immediate anxiety relief", priority=1, duration=480),
                    Suggestion(type=SuggestionType.AFFIRMATION, title="AI Calming Affirmations",
                               description="AI-powered anxiety relief", priority=2),
                ])
            elif intensity >= 5:
                suggestions.extend([
                    Suggestion(type=SuggestionType.AUDIO, title="Calming Sounds",
                               description="Nature sounds to soothe anxiety", priority=1),
                    Suggestion(type=SuggestionType.BREATHING, title="Box Breathing",
                               description="Structured breathing for calm", priority=2, duration=360),
                ])
            else:
                suggestions.extend([
                    Suggestion(type=SuggestionType.MUSIC, title="AI Peaceful Music",
                               description="Gentle AI music for mild anxiety", priority=1),
                    Suggestion(type=SuggestionType.JOURNAL, title="Worry Journal",
                               description="Write down what's on your mind", priority=2),
                ])

        elif mood == MoodType.SAD:
            if intensity >= 7:
                suggestions.extend([
                    Suggestion(type=SuggestionType.AFFIRMATION, title="AI Comfort Affirmations",
                               description="Warm, AI-generated supportive messages", priority=1),
                    Suggestion(type=SuggestionType.AUDIO, title="Comforting Sounds",
                               description="Warm, supportive audio", priority=2),
                ])
            else:
                suggestions.extend([
                    Suggestion(type=SuggestionType.MUSIC, title="AI Gentle Music",
                               description="Soft, understanding AI melodies", priority=1),
                    Suggestion(type=SuggestionType.JOURNAL, title="Express Feelings",
                               description="Sometimes writing helps", priority=2),
                ])

        elif mood == MoodType.ANGRY:
            if intensity >= 7:
                suggestions.extend([
                    Suggestion(type=SuggestionType.BREATHING, title="Cooling Breath",
                               description="Box breathing to release tension", priority=1, duration=360),
                    Suggestion(type=SuggestionType.AFFIRMATION, title="AI Grounding Affirmations",
                               description="AI messages to channel energy", priority=2),
                ])
            else:
                suggestions.extend([
                    Suggestion(type=SuggestionType.JOURNAL, title="Vent Writing",
                               description="Write out your frustrations", priority=1),
                    Suggestion(type=SuggestionType.MUSIC, title="AI Grounding Music",
                               description="AI music to center yourself", priority=2),
                ])

        elif mood == MoodType.NEUTRAL:
            suggestions.extend([
                Suggestion(type=SuggestionType.MUSIC, title="AI Ambient Music",
                           description="AI background music for reflection", priority=1),
                Suggestion(type=SuggestionType.JOURNAL, title="Daily Check-in", description="How was your day really?",
                           priority=2),
                Suggestion(type=SuggestionType.GAME, title="Gratitude Game",
                           description="Find three things you're grateful for", priority=3),
            ])

        elif mood == MoodType.MIXED:
            suggestions.extend([
                Suggestion(type=SuggestionType.JOURNAL, title="Free Writing",
                           description="Write whatever comes to mind", priority=1),
                Suggestion(type=SuggestionType.BREATHING, title="Centering Breath",
                           description="Find your center in complexity", priority=2, duration=450),
                Suggestion(type=SuggestionType.AFFIRMATION, title="AI Understanding Affirmations",
                           description="AI support for complex emotions", priority=3),
            ])

        return suggestions[:4]  # Return top 4 suggestions