@echo off
REM Quick start script for Docker deployment (Windows)

echo ================================
echo RAG Chatbot - Docker Quick Start
echo ================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed.
    echo Please install Docker from https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker Compose is not installed.
    echo Please install Docker Compose from https://docs.docker.com/compose/install/
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo .env file created. You can edit it to customize settings.
) else (
    echo .env file already exists.
)

echo.
echo Building Docker images...
docker-compose build

if %errorlevel% neq 0 (
    echo Error: Failed to build Docker images.
    exit /b 1
)

echo.
echo Build complete!
echo.
echo To run the full pipeline:
echo    1. Crawl: docker-compose run scraper python scraper/crawl.py
echo    2. Chunk: docker-compose run scraper python scraper/clean_chunk.py
echo    3. Index: docker-compose exec rag_service python rag_service/indexer.py
echo.
echo Starting services...
docker-compose up -d rag_service web

if %errorlevel% neq 0 (
    echo Error: Failed to start services.
    exit /b 1
)

echo.
echo Services started successfully!
echo.
echo Access points:
echo    - Web UI: http://localhost:7860
echo    - API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo View logs: docker-compose logs -f
echo Stop services: docker-compose down
echo.
echo ================================


