# Dockerfile — Legal AI Platform API
# Build: docker build -t legal-ai-api:latest .
# Run: docker run -e GEMINI_API_KEY=... -p 8000:8000 legal-ai-api:latest

FROM python:3.13-slim

WORKDIR /app

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir openai>=1.0.0

# Copy aplicação
COPY . .

# Setup logging para Cloud Logging
ENV PYTHONUNBUFFERED=1
ENV LOG_FORMAT=json
ENV LOG_LEVEL=info

# Expose porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/health')" || exit 1

# Comando
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
