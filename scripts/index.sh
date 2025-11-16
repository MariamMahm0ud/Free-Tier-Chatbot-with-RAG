#!/bin/bash
# Script to run the indexer

cd "$(dirname "$0")/.."
python rag_service/indexer.py

