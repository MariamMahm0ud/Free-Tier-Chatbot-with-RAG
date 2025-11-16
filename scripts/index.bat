@echo off
REM Script to run the indexer (Windows)

cd /d "%~dp0\.."
python rag_service/indexer.py

