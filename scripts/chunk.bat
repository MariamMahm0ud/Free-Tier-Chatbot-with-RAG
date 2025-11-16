@echo off
REM Script to run the chunker (Windows)

cd /d "%~dp0\.."
python scraper/clean_chunk.py

