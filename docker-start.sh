#!/bin/bash
# Quick start script for Docker deployment

echo "================================"
echo "RAG Chatbot - Docker Quick Start"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed."
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. You can edit it to customize settings."
else
    echo "✅ .env file already exists."
fi

echo ""
echo "🔨 Building Docker images..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to build Docker images."
    exit 1
fi

echo ""
echo "✅ Build complete!"
echo ""
echo "📊 To run the full pipeline:"
echo "   1. Crawl: docker-compose run scraper python scraper/crawl.py"
echo "   2. Chunk: docker-compose run scraper python scraper/clean_chunk.py"
echo "   3. Index: docker-compose exec rag_service python rag_service/indexer.py"
echo ""
echo "🚀 Starting services..."
docker-compose up -d rag_service web

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to start services."
    exit 1
fi

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access points:"
echo "   - Web UI: http://localhost:7860"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
echo ""
echo "================================"


