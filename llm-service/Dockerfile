FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Ollama
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://ollama.ai/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Start Ollama service and pull model, then start the app
CMD ["sh", "-c", "ollama serve & sleep 10 && ollama pull gemma:2b && uvicorn main:app --host 0.0.0.0 --port 8080"]