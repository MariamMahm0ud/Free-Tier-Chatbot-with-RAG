#!/bin/bash
# Script to run the FastAPI server

cd "$(dirname "$0")/.."
uvicorn rag_service.api:app --reload --host 0.0.0.0 --port 8000

