"""
Retriever module for querying Chroma vector store.
Encodes queries and retrieves top-k similar chunks.
"""

import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Configuration
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "website_chunks"

# Global model and client (lazy loaded)
_model: Optional[SentenceTransformer] = None
_client: Optional[chromadb.ClientAPI] = None


def get_model() -> SentenceTransformer:
    """Lazy load embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_client() -> chromadb.ClientAPI:
    """Lazy load Chroma client."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
    return _client


def retrieve(query: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve top-k most similar chunks for a query.
    
    Args:
        query: Search query string
        top_k: Number of results to return
    
    Returns:
        List of dictionaries with keys: text, meta, score
    """
    try:
        model = get_model()
        client = get_client()
        
        # Get collection
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
        except Exception as e:
            print(f"Error getting collection: {e}")
            return []
        
        # Encode query
        query_embedding = model.encode(query, show_progress_bar=False).tolist()
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )
        
        # Format results
        hits = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                hit = {
                    "text": results['documents'][0][i],
                    "meta": results['metadatas'][0][i],
                    "score": 1.0 - results['distances'][0][i]  # Convert distance to similarity
                }
                hits.append(hit)
        
        return hits
    
    except Exception as e:
        print(f"Error in retrieve: {e}")
        return []


if __name__ == "__main__":
    # Test retrieval
    test_query = "What is the main topic?"
    print(f"Testing retrieval with query: '{test_query}'")
    results = retrieve(test_query, top_k=3)
    print(f"Retrieved {len(results)} results:")
    for i, hit in enumerate(results, 1):
        print(f"\n{i}. Score: {hit['score']:.4f}")
        print(f"   Title: {hit['meta'].get('title', 'N/A')}")
        print(f"   URL: {hit['meta'].get('url', 'N/A')}")
        print(f"   Text preview: {hit['text'][:100]}...")

