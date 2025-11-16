#!/bin/bash
# Script to run the chunker

cd "$(dirname "$0")/.."
python scraper/clean_chunk.py

