"""
Vector indexer using sentence-transformers and ChromaDB.
Loads chunk JSON files, creates embeddings, and stores in Chroma with persistence.
"""

import os
import json
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb import PersistentClient
from chromadb.config import Settings

# Configuration
CHUNKS_DIR = os.path.join(os.path.dirname(__file__), "..", "scraper", "chunks")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 16
COLLECTION_NAME = "website_chunks"

# Ensure chroma directory exists
os.makedirs(CHROMA_DIR, exist_ok=True)


def load_chunks() -> List[Dict]:
    """Load all chunk JSON files from CHUNKS_DIR."""
    if not os.path.exists(CHUNKS_DIR):
        print(f"Error: Chunks directory {CHUNKS_DIR} does not exist")
        return []
    
    json_files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith('.json')]
    
    if not json_files:
        print(f"No chunk JSON files found in {CHUNKS_DIR}")
        return []
    
    chunks = []
    for filename in json_files:
        filepath = os.path.join(CHUNKS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
                chunks.append(chunk_data)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_DIR}")
    return chunks


def index_chunks(chunks: List[Dict], model: SentenceTransformer, client: chromadb.ClientAPI):
    """
    Index chunks into Chroma collection.
    Creates embeddings in batches and adds to collection.
    """
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Website content chunks"}
    )
    
    # Prepare data
    texts = [chunk["text"] for chunk in chunks]
    ids = [chunk["chunk_id"] for chunk in chunks]
    metadatas = []
    for chunk in chunks:
        clean_meta = {
            "url": str(chunk.get("url", "")),
            "title": str(chunk.get("title", "")),
            "chunk_id": str(chunk.get("chunk_id", "")),  # MUST be string
            "source_file": str(chunk.get("source_file", ""))  # MUST be string
        }

        # remove any internal fields like _type
        clean_meta = {k: v for k, v in clean_meta.items() if not k.startswith("_")}
        
        metadatas.append(clean_meta)

    print(f"Creating embeddings with model {MODEL_NAME} (batch_size={BATCH_SIZE})...")
    
    # Create embeddings in batches
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        batch_embeddings = model.encode(batch_texts, show_progress_bar=False)
        all_embeddings.extend(batch_embeddings.tolist())
        print(f"Processed batch {i // BATCH_SIZE + 1}/{(len(texts) + BATCH_SIZE - 1) // BATCH_SIZE}")
    
    print(f"Adding {len(ids)} documents to Chroma collection...")
    
    # Add to collection
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=all_embeddings
    )
    
    # Persist
    print(f"Data successfully added to Chroma collection and persisted.")



    
    # Verify count
    count = collection.count()
    print(f"Collection '{COLLECTION_NAME}' now contains {count} items")
    
    return count


def main():
    """Main indexing function."""
    print("Starting indexing process...")
    
    # Load chunks
    chunks = load_chunks()
    if not chunks:
        print("No chunks to index. Exiting.")
        return
    
    # Load embedding model
    print(f"Loading embedding model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    # Initialize Chroma client with persistence
    print(f"Initializing Chroma client (persistence: {CHROMA_DIR})...")
    client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Index chunks
    count = index_chunks(chunks, model, client)
    
    print(f"\nIndexing completed. Total indexed: {count}")


if __name__ == "__main__":
    main()

