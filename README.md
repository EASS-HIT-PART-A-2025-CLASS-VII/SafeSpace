# SafeSpace - AI-Powered Mental Health Companion

A sophisticated mental health companion app built with modern microservices architecture, featuring AI-powered mood analysis, personalized playlist generation, and therapeutic activities.

## 🏗️ Architecture

### Modern Microservices Design
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend API**: FastAPI + Pydantic + JWT Authentication
- **LLM Microservice**: OpenAI GPT integration for AI-powered features
- **Database**: Redis for caching and session management
- **Containerization**: Docker + Docker Compose for easy deployment

### Key Features
- 🧠 **AI-Powered Mood Analysis**: Intelligent mood detection and personalized suggestions
- 🎵 **Smart Playlist Generation**: AI-curated music based on emotional state
- 💭 **Personalized Affirmations**: AI-generated supportive messages
- 🫁 **Breathing Exercises**: Guided breathing with mood-specific patterns
- 📝 **Journaling Space**: Therapeutic writing with AI-powered prompts
- 🎮 **Grounding Games**: Interactive activities for anxiety and stress
- ✨ **Joy Jar**: Capture and revisit happy moments
- 🎧 **Audio Therapy**: Curated soundscapes for different moods

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (for AI features)
- Spotify API credentials (for music features)

### One-Click Setup
1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
3. Add your API keys to `.env`
4. Start the entire application:
   ```bash
   docker-compose up --build
   ```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **LLM Service**: http://localhost:8001
- **API Documentation**: http://localhost:8000/docs

## 🔧 Development

### Local Development
```bash
# Frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# LLM Service
cd llm-service
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

### Project Structure
```
safespace/
├── frontend/                 # React frontend
├── backend/                  # FastAPI backend
├── llm-service/             # AI microservice
├── docker-compose.yml       # Container orchestration
└── README.md
```

## 🤖 AI Integration

### LLM Microservice Features
- **Intelligent Playlist Generation**: Uses GPT to create mood-appropriate music recommendations
- **Personalized Affirmations**: AI-generated supportive messages based on emotional state
- **Mood Analysis**: Advanced pattern recognition for emotional insights
- **Fallback Systems**: Rule-based alternatives ensure reliability

### API Integration
The LLM service seamlessly integrates with the main backend to provide:
- Enhanced user experience through personalization
- Intelligent content generation
- Adaptive responses based on user patterns

## 🛡️ Safety & Privacy

- **Non-Clinical Approach**: Supportive companion, not medical advice
- **Crisis Detection**: Automatic referral to professional resources
- **Data Privacy**: Local storage with optional cloud sync
- **Secure Authentication**: JWT-based user sessions

## 🎯 Technical Highlights

### Modern Software Engineering
- **Microservices Architecture**: Scalable, maintainable service separation
- **API-First Design**: RESTful APIs with OpenAPI documentation
- **Containerization**: Docker for consistent deployment
- **Type Safety**: TypeScript frontend, Pydantic backend validation
- **AI Integration**: OpenAI GPT for intelligent features

### Production Ready
- **Health Checks**: Service monitoring and status endpoints
- **Error Handling**: Graceful degradation and fallback systems
- **Caching**: Redis for performance optimization
- **CORS Configuration**: Secure cross-origin resource sharing
- **Environment Management**: Configurable for different deployment stages

## 📊 Use Cases

### For Users
- Daily mood check-ins with personalized support
- Anxiety management through breathing and grounding exercises
- Depression support via journaling and affirmations
- Stress relief through curated audio experiences
- Emotional growth tracking and pattern recognition

### For Developers
- Modern full-stack architecture example
- Microservices implementation
- AI/LLM integration patterns
- Docker containerization best practices
- FastAPI + React integration

## 🌟 Innovation

This project showcases cutting-edge software engineering practices:
- **Product Engineering Approach**: User-centric design with technical excellence
- **AI-First Features**: Leveraging LLMs for personalized experiences
- **Microservices Architecture**: Scalable, maintainable system design
- **Modern Tech Stack**: Latest frameworks and best practices
- **Real-World Application**: Addresses genuine mental health needs

## 🚀 Deployment

### Production Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up --scale backend=3 --scale llm-service=2
```

### Cloud Deployment
The application is designed for easy deployment on:
- AWS (ECS, EKS)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Instances, AKS)
- DigitalOcean (App Platform)

## 📈 Future Enhancements

- **Mobile App**: React Native companion
- **Advanced AI**: Fine-tuned models for mental health
- **Social Features**: Anonymous peer support
- **Wearable Integration**: Heart rate and stress monitoring
- **Therapist Dashboard**: Professional oversight tools

---

Built with ❤️ for mental health awareness and modern software engineering excellence.