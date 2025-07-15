# SafeSpace Music Peeker Backend

A FastAPI backend for mood-based music recommendations and mental health support.

## Features

- **Authentication**: User registration and login with JWT tokens
- **Mood Analysis**: Parse mood from text, voice, or quiz inputs
- **AI Suggestions**: Intelligent activity suggestions based on mood and intensity
- **Music Engine**: Generate playlists from Spotify and YouTube
- **User Database**: Store preferences, mood history, and playlist history

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the server:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Mood Analysis
- `POST /mood/analyze` - Analyze mood and get suggestions

### Music
- `POST /music/playlist` - Generate mood-based playlist

### User Management
- `GET /user/preferences` - Get user preferences
- `PUT /user/preferences` - Update user preferences
- `GET /user/mood-history` - Get mood history

## Architecture

- **Backend**: FastAPI with Pydantic for request validation
- **Mood Agent**: Parses user intent from multiple sources
- **Music Engine**: Queries Spotify/YouTube APIs
- **User DB Service**: Stores user data and history using MongoDB

## Environment Variables

- `SECRET_KEY`: JWT secret key