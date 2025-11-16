@echo off
REM Script to run the FastAPI server (Windows)

cd /d "%~dp0\.."
uvicorn rag_service.api:app --reload --host 0.0.0.0 --port 8000

