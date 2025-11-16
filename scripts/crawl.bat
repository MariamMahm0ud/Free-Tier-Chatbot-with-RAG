@echo off
REM Script to run the web crawler (Windows)

cd /d "%~dp0\.."
python scraper/crawl.py

