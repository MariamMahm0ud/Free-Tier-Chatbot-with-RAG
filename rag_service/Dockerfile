# RAG Service Dockerfile (FastAPI + ChromaDB + Embeddings)
FROM python:3.11

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY rag_service/requirements.txt /app/rag_service/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/rag_service/requirements.txt

# Copy all service code
COPY rag_service/ /app/rag_service/
#COPY scraper/chunks/ /app/scraper/chunks/

# Create ChromaDB directory
RUN mkdir -p /app/rag_service/chroma_db

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt', quiet=True)" || true

# Expose port
EXPOSE 8000

# Set working directory
WORKDIR /app

# Run FastAPI with uvicorn
CMD ["uvicorn", "rag_service.api:app", "--host", "0.0.0.0", "--port", "8000"]


