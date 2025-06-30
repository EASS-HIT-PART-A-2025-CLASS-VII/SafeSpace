import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from mood_agent.mood_parser import MoodParser
from models.schemas import MoodInput, MoodType


class TestBackendLogicOnly:

    @pytest.fixture
    def mood_parser(self):
        return MoodParser()

    def test_mood_parser_initialization(self, mood_parser):
        assert isinstance(mood_parser.mood_keywords, dict)
        assert MoodType.HAPPY in mood_parser.mood_keywords
        assert MoodType.SAD in mood_parser.mood_keywords
        assert MoodType.ANXIOUS in mood_parser.mood_keywords

    @pytest.mark.asyncio
    async def test_mood_parser_text_analysis(self, mood_parser):
        mood_input = MoodInput(text_input="I feel really happy today!")
        result = await mood_parser.parse_mood(mood_input)

        assert result.mood_type == MoodType.HAPPY
        assert 0 < result.intensity <= 10
        assert isinstance(result.ai_message, str)
        assert len(result.ai_message) > 0

    @pytest.mark.asyncio
    async def test_mood_parser_direct_input(self, mood_parser):
        mood_input = MoodInput(mood_type=MoodType.SAD, intensity=7)
        result = await mood_parser.parse_mood(mood_input)

        assert result.mood_type == MoodType.SAD
        assert result.intensity == 7
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_mood_suggestions_generation(self, mood_parser):
        suggestions = await mood_parser.get_intelligent_suggestions(
            MoodType.ANXIOUS, 8
        )

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert len(suggestions) <= 4

        for suggestion in suggestions:
            assert hasattr(suggestion, 'title')
            assert hasattr(suggestion, 'description')
            assert hasattr(suggestion, 'priority')
            assert isinstance(suggestion.title, str)
            assert isinstance(suggestion.description, str)
            assert suggestion.priority > 0

    @pytest.mark.asyncio
    async def test_mood_intensity_validation(self, mood_parser):
        test_cases = [
            ("I feel extremely happy", 8, 10),
            ("I'm a bit sad", 1, 4),
            ("I feel quite anxious", 5, 7)
        ]

        for text, min_expected, max_expected in test_cases:
            mood_input = MoodInput(text_input=text)
            result = await mood_parser.parse_mood(mood_input)
            assert min_expected <= result.intensity <= max_expected


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
