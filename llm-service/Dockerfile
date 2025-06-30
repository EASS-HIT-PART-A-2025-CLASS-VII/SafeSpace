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

# Copy startup script and make it executable
COPY start.sh .
RUN chmod +x start.sh

# Expose port
EXPOSE 8080

# Use startup script as the container entrypoint
CMD ["./start.sh"]