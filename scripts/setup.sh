#!/bin/bash

# SafeSpace Setup Script

echo "🚀 Setting up SafeSpace - AI-Powered Mental Health Companion"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "✅ Environment file created. Please edit .env with your API keys."
else
    echo "✅ Environment file already exists."
fi

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend is not responding"
fi

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running at http://localhost:8000"
else
    echo "❌ Backend API is not responding"
fi

# Check LLM service
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ LLM Service is running at http://localhost:8001"
else
    echo "❌ LLM Service is not responding"
fi

echo ""
echo "🎉 SafeSpace setup complete!"
echo ""
echo "📱 Access your app at: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🤖 LLM Service: http://localhost:8001/docs"
echo ""
echo "⚠️  Don't forget to add your API keys to the .env file:"
echo "   - OPENAI_API_KEY (for AI features)"
echo "   - SPOTIFY_CLIENT_ID & SPOTIFY_CLIENT_SECRET (for music)"
echo ""
echo "🔧 To stop services: docker-compose down"
echo "🔄 To restart services: docker-compose restart"
echo "📊 To view logs: docker-compose logs -f"