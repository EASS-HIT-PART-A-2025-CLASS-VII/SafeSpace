# SafeSpace LLM Microservice (Local AI Version)

AI-powered microservice for generating personalized playlists and affirmations based on user mood and emotional state — now powered by local LLMs using [Ollama](https://ollama.com).

## Features

- 🎵 **Local AI Playlist Generation**: Uses the `gemma:2b` LLM to generate personalized music recommendations.
- 💬 **Mood-Based Affirmations**: Produces warm, supportive affirmations tailored to the user's current emotional state.
- 🧠 **Mood Analysis**: Lightweight rule-based analysis with suggestions for self-care.
- ✅ **Free & Offline**: Runs fully locally using Ollama — no OpenAI key required.

## API Endpoints

### `POST /generate-playlist`
Generate AI-powered playlist recommendations based on mood and intensity.

### `POST /generate-affirmations`
Create personalized affirmations and supportive messages.

### `POST /analyze-mood`
Analyze mood patterns and suggest self-care activities (non-LLM).

### `GET /health`
Health check endpoint.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
