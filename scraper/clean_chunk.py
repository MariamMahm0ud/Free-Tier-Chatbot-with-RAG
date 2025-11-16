"""
Text cleaning and chunking module.
Reads scraped JSON files, cleans text, and chunks into ~300-word chunks with overlap.
"""

import os
import json
import re
from typing import List, Dict
import nltk

# Try to download punkt tokenizer, fallback to simple word split if fails
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        print("Warning: NLTK punkt not available, using simple word split")

INPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "chunks")

# Configuration
CHUNK_SIZE_WORDS = 300
CHUNK_OVERLAP_WORDS = 50

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clean_text(text: str) -> str:
    """Clean text: strip blank lines, collapse whitespace."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def word_count(text: str) -> int:
    """Count words in text (simple split)."""
    return len(text.split())


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into chunks of approximately chunk_size words with overlap.
    Uses simple word splitting (fallback if NLTK unavailable).
    """
    words = text.split()
    chunks = []
    
    if len(words) <= chunk_size:
        return [text]
    
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)
        
        # Move start forward by (chunk_size - overlap)
        start += (chunk_size - overlap)
    
    return chunks


def process_file(filepath: str) -> List[Dict]:
    """Process a single JSON file and return list of chunk dictionaries."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        url = data.get("url", "")
        title = data.get("title", "Untitled")
        #text = data.get("text", "")
        text = data.get("text") or data.get("content") or data.get("body") or ""

        source_file = os.path.basename(filepath)
        
        # Clean text
        cleaned_text = clean_text(text)
        
        if not cleaned_text:
            return []
        
        # Chunk text
        chunks = chunk_text(cleaned_text, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS)
        
        # Create chunk dictionaries
        chunk_list = []
        for idx, chunk_content  in enumerate(chunks):
            chunk_dict = {
                "url": url,
                "title": title,
                "chunk_id": f"{source_file}_{idx}",
                "text": chunk_content , 
                "source_file": source_file
            }
            chunk_list.append(chunk_dict)
        
        return chunk_list
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []


def process_all_files() -> int:
    """Process all JSON files in INPUT_DIR and save chunks to OUTPUT_DIR."""
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory {INPUT_DIR} does not exist")
        return 0
    
    json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {INPUT_DIR}")
        return 0
    
    print(f"Processing {len(json_files)} files from {INPUT_DIR}")
    
    total_chunks = 0
    
    for filename in json_files:
        filepath = os.path.join(INPUT_DIR, filename)
        chunks = process_file(filepath)
        
        # Save each chunk as separate JSON file
        for chunk in chunks:
            chunk_filename = f"{chunk['chunk_id']}.json"
            chunk_filepath = os.path.join(OUTPUT_DIR, chunk_filename)
            
            with open(chunk_filepath, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
            
            total_chunks += 1
    
    print(f"\nChunking completed. Created {total_chunks} chunks in {OUTPUT_DIR}")
    return total_chunks


if __name__ == "__main__":
    count = process_all_files()
    print(f"Total chunks created: {count}")

