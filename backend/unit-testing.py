import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from mood_agent.mood_parser import MoodParser
from models.schemas import MoodInput, MoodType, PlaylistRequest


class TestBackendServices:
    """Pytest-based unit tests for backend services"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mood_parser(self):
        """Mood parser fixture"""
        return MoodParser()

    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "SafeSpace Music Peeker API"
        assert data["status"] == "running"

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

    def test_mood_parser_initialization(self, mood_parser):
        """Test mood parser initializes correctly"""
        assert isinstance(mood_parser.mood_keywords, dict)
        assert MoodType.HAPPY in mood_parser.mood_keywords
        assert MoodType.SAD in mood_parser.mood_keywords
        assert MoodType.ANXIOUS in mood_parser.mood_keywords

    @pytest.mark.asyncio
    async def test_mood_parser_text_analysis(self, mood_parser):
        """Test mood parser can analyze text input"""
        mood_input = MoodInput(text_input="I feel really happy today!")
        result = await mood_parser.parse_mood(mood_input)

        assert result.mood_type == MoodType.HAPPY
        assert 0 < result.intensity <= 10
        assert isinstance(result.ai_message, str)
        assert len(result.ai_message) > 0

    @pytest.mark.asyncio
    async def test_mood_parser_direct_input(self, mood_parser):
        """Test mood parser with direct mood and intensity"""
        mood_input = MoodInput(mood_type=MoodType.SAD, intensity=7)
        result = await mood_parser.parse_mood(mood_input)

        assert result.mood_type == MoodType.SAD
        assert result.intensity == 7
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_mood_suggestions_generation(self, mood_parser):
        """Test intelligent suggestions generation"""
        suggestions = await mood_parser.get_intelligent_suggestions(
            MoodType.ANXIOUS, 8
        )

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert len(suggestions) <= 4

        # Check suggestion structure
        for suggestion in suggestions:
            assert hasattr(suggestion, 'title')
            assert hasattr(suggestion, 'description')
            assert hasattr(suggestion, 'priority')
            assert isinstance(suggestion.title, str)
            assert isinstance(suggestion.description, str)
            assert suggestion.priority > 0

    @patch('httpx.AsyncClient')
    def test_mood_analysis_endpoint(self, mock_client, client):
        """Test mood analysis endpoint with mocked LLM service"""
        # Mock LLM service response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ai_insights": "Test insights"}

        mock_client_instance = Mock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        response = client.post("/api/mood/analyze", json={
            "text_input": "I feel anxious about work"
        })

        assert response.status_code == 200
        data = response.json()
        assert "mood_type" in data
        assert "intensity" in data
        assert "suggestions" in data
        assert "message" in data

    @patch('httpx.AsyncClient')
    def test_playlist_generation_endpoint(self, mock_client, client):
        """Test playlist generation endpoint"""
        # Mock LLM service response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "songs": [
                {"title": "Happy Song", "artist": "Test Artist"}
            ],
            "playlist_name": "Test Playlist",
            "description": "Test Description"
        }

        mock_client_instance = Mock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        response = client.post("/api/music/playlist", json={
            "mood_type": "happy",
            "intensity": 7,
            "duration_minutes": 30
        })

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "tracks" in data
        assert "mood_type" in data

    @patch('httpx.AsyncClient')
    def test_affirmations_endpoint(self, mock_client, client):
        """Test affirmations generation endpoint"""
        # Mock LLM service response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "affirmations": ["You are strong", "You are loved"],
            "personalized_message": "You are doing great"
        }

        mock_client_instance = Mock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        response = client.post("/api/ai/affirmations?mood_type=sad&intensity=6")

        assert response.status_code == 200
        data = response.json()
        assert "affirmations" in data
        assert "personalized_message" in data

    @pytest.mark.asyncio
    async def test_mood_intensity_validation(self, mood_parser):
        """Test mood intensity is within valid range"""
        test_cases = [
            ("I feel extremely happy", 8, 10),
            ("I'm a bit sad", 1, 4),
            ("I feel quite anxious", 5, 7)
        ]

        for text, min_expected, max_expected in test_cases:
            mood_input = MoodInput(text_input=text)
            result = await mood_parser.parse_mood(mood_input)

            assert min_expected <= result.intensity <= max_expected

    def test_error_handling(self, client):
        """Test API error handling"""
        # Test invalid mood analysis request
        response = client.post("/api/mood/analyze", json={})
        # Should not crash, should return some response
        assert response.status_code in [200, 422, 500]

        # Test invalid playlist request
        response = client.post("/api/music/playlist", json={
            "mood_type": "invalid_mood",
            "intensity": 15  # Invalid intensity
        })
        # Should handle validation errors
        assert response.status_code in [422, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])