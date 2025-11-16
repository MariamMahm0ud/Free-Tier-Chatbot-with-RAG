#!/bin/bash
# Script to run the web crawler

cd "$(dirname "$0")/.."
python scraper/crawl.py

