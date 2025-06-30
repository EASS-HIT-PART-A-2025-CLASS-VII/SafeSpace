#!/bin/bash

echo "🚀 Starting Ollama and FastAPI LLM Service..."

# Start Ollama server in the background
ollama serve &

# Wait a bit for Ollama to be ready
sleep 10

# Pull the model
ollama pull gemma:2b

# Warm up the model to avoid timeout on first request
ollama run gemma:2b "Say hello" > /dev/null 2>&1

# Start FastAPI app
exec uvicorn main:app --host 0.0.0.0 --port 8080
