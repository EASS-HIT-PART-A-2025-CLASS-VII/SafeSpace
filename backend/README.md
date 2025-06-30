# SafeSpace Backend

A FastAPI backend for mood-based music recommendations and mental health support.

## Features

- **Mood Analysis**: Parse mood from text, voice, or quiz inputs
- **AI Suggestions**: Intelligent activity suggestions based on mood and intensity

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Health

- `POST /health` - Verify the state of the backend

### Mood Analysis
- `POST /api/mood/analyze` - Analyze mood and get suggestions

### Music
- `POST /api/music/playlist` - Generate mood-based playlist

### AI-Powered Affirmations
- `POST /api/ai/affirmations` – Generate affirmations based on mood type and intensity

## Architecture

- **Backend**: FastAPI with Pydantic for request validation
- **Mood Agent**: Parses user intent from multiple sources
