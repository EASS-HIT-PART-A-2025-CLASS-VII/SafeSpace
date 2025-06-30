import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from main import app, LLMService


class TestLLMService:

    @pytest.fixture
    def llm_service(self):
        """LLM service fixture"""
        return LLMService()

    def test_llm_service_initialization(self, llm_service):
        """Test LLM service initializes with mood contexts"""
        assert isinstance(llm_service.mood_contexts, dict)
        assert "happy" in llm_service.mood_contexts
        assert "sad" in llm_service.mood_contexts
        assert "anxious" in llm_service.mood_contexts
        assert "angry" in llm_service.mood_contexts
        assert "tired" in llm_service.mood_contexts
        assert "neutral" in llm_service.mood_contexts
        assert "mixed" in llm_service.mood_contexts

    def test_mood_context_content(self, llm_service):
        """Test mood contexts contain appropriate descriptors"""
        # Test happy mood context
        happy_context = llm_service.mood_contexts["happy"]
        assert "joyful" in happy_context.lower()
        assert "uplifting" in happy_context.lower()

        # Test sad mood context
        sad_context = llm_service.mood_contexts["sad"]
        assert "comforting" in sad_context.lower()
        assert "gentle" in sad_context.lower()

        # Test anxious mood context
        anxious_context = llm_service.mood_contexts["anxious"]
        assert "calming" in anxious_context.lower()
        assert "peaceful" in anxious_context.lower()

    @patch('subprocess.run')
    def test_ollama_execution(self, mock_subprocess, llm_service):
        """Test Ollama command execution"""
        # Mock successful subprocess execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"test": "response"}'
        mock_subprocess.return_value = mock_result

        result = llm_service._run_ollama("test prompt")

        assert result == '{"test": "response"}'
        mock_subprocess.assert_called_once()

    @patch('subprocess.run')
    def test_ollama_error_handling(self, mock_subprocess, llm_service):
        """Test Ollama error handling"""
        # Mock failed subprocess execution
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        with pytest.raises(Exception):
            llm_service._run_ollama("test prompt")

    def test_json_extraction(self, llm_service):
        """Test JSON extraction from LLM responses"""
        # Test valid JSON extraction
        response_with_json = 'Some text before {"key": "value", "number": 123} some text after'
        result = llm_service._extract_json_from_response(response_with_json)

        assert result["key"] == "value"
        assert result["number"] == 123

        # Test invalid JSON handling
        response_without_json = "This is just plain text without JSON"
        result = llm_service._extract_json_from_response(response_without_json)

        assert result == {}

    def test_fallback_playlist_generation(self, llm_service):
        """Test fallback playlist generation for all moods"""
        moods = ["happy", "sad", "anxious", "angry", "tired", "neutral", "mixed"]

        for mood in moods:
            # Create mock request
            mock_request = Mock()
            mock_request.mood_type = mood
            mock_request.intensity = 5
            mock_request.duration_minutes = 30

            playlist = llm_service._get_fallback_playlist(mock_request)

            # Verify playlist structure
            assert isinstance(playlist.songs, list)
            assert len(playlist.songs) > 0
            assert isinstance(playlist.playlist_name, str)
            assert isinstance(playlist.description, str)
            assert isinstance(playlist.mood_description, str)

            # Verify each song has required fields
            for song in playlist.songs:
                assert "title" in song
                assert "artist" in song
                assert isinstance(song["title"], str)
                assert isinstance(song["artist"], str)

    def test_fallback_affirmations_generation(self, llm_service):
        """Test fallback affirmations generation for all moods"""
        moods = ["happy", "sad", "anxious", "angry", "tired", "neutral", "mixed"]

        for mood in moods:
            # Create mock request
            mock_request = Mock()
            mock_request.mood_type = mood
            mock_request.intensity = 6
            mock_request.user_name = "TestUser"
            mock_request.context = "Test context"

            affirmations = llm_service._get_fallback_affirmations(mock_request)

            # Verify affirmations structure
            assert isinstance(affirmations.affirmations, list)
            assert len(affirmations.affirmations) == 5
            assert isinstance(affirmations.personalized_message, str)

            # Verify each affirmation is a string
            for affirmation in affirmations.affirmations:
                assert isinstance(affirmation, str)
                assert len(affirmation) > 0

    @patch.object(LLMService, '_run_ollama')
    @pytest.mark.asyncio
    async def test_playlist_generation_with_ai(self, mock_ollama, llm_service):
        """Test playlist generation with mocked AI response"""
        # Mock AI response
        mock_response = json.dumps({
            "songs": [
                {"title": "AI Song 1", "artist": "AI Artist 1"},
                {"title": "AI Song 2", "artist": "AI Artist 2"}
            ],
            "playlist_name": "AI Generated Playlist",
            "description": "AI generated description",
            "mood_description": "AI mood description"
        })
        mock_ollama.return_value = mock_response

        # Create mock request
        mock_request = Mock()
        mock_request.mood_type = "happy"
        mock_request.intensity = 7
        mock_request.duration_minutes = 30
        mock_request.genres = None
        mock_request.user_preferences = None

        result = await llm_service.generate_playlist_prompt(mock_request)

        # Verify result
        assert len(result.songs) == 2
        assert result.playlist_name == "AI Generated Playlist"
        assert result.description == "AI generated description"

    @patch.object(LLMService, '_run_ollama')
    @pytest.mark.asyncio
    async def test_affirmations_generation_with_ai(self, mock_ollama, llm_service):
        """Test affirmations generation with mocked AI response"""
        # Mock AI response
        mock_response = json.dumps({
            "affirmations": [
                "I am strong and capable",
                "I deserve happiness",
                "I can overcome challenges"
            ],
            "personalized_message": "You are doing wonderfully",
            "breathing_instruction": "Breathe deeply and slowly"
        })
        mock_ollama.return_value = mock_response

        # Create mock request
        mock_request = Mock()
        mock_request.mood_type = "anxious"
        mock_request.intensity = 8
        mock_request.user_name = "TestUser"
        mock_request.context = "Feeling overwhelmed"

        result = await llm_service.generate_affirmations(mock_request)

        # Verify result
        assert len(result.affirmations) == 3
        assert result.personalized_message == "You are doing wonderfully"
        assert result.breathing_instruction == "Breathe deeply and slowly"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])