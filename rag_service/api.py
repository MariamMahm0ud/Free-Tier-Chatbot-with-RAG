

from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, AsyncGenerator
import json
import asyncio
try:
    from .retriever import retrieve
    from .llm import synthesize_answer, synthesize_answer_streaming
except ImportError:
    from retriever import retrieve
    from llm import synthesize_answer, synthesize_answer_streaming

app = FastAPI(title="RAG Chatbot API", version="0.1.0")

# CORS middleware for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5


class RetrieveResponse(BaseModel):
    query: str
    results: List[Dict]


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    use_llm: bool = False


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict]
    llm_error: Optional[str] = None


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"ok": True}


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_endpoint(request: RetrieveRequest):
    """
    Retrieve top-k documents for a query.
    """
    try:
        results = retrieve(request.query, top_k=request.top_k)
        
        # Format results
        formatted_results = [
            {
                "text": hit["text"],
                "meta": hit["meta"],
                "score": hit["score"]
            }
            for hit in results
        ]
        
        return RetrieveResponse(
            query=request.query,
            results=formatted_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that retrieves relevant chunks and generates an answer.
    """
    try:
        # Retrieve relevant chunks
        hits = retrieve(request.query, top_k=request.top_k)
        
        if not hits:
            return ChatResponse(
                answer="I couldn't find any relevant information to answer your query.",
                sources=[],
                llm_error=None
            )
        
        # Synthesize answer
        result = synthesize_answer(request.query, hits, use_llm=request.use_llm)
        
        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            llm_error=result.get("llm_error")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint that streams tokens in real-time using Server-Sent Events.
    Returns a stream of JSON objects with incremental tokens and final sources.
    """
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            # Retrieve relevant chunks
            hits = retrieve(request.query, top_k=request.top_k)
            
            if not hits:
                # Send error message
                yield f"data: {json.dumps({'type': 'error', 'content': 'No relevant information found'})}\n\n"
                return
            
            # Send sources first
            sources = [hit['meta'] for hit in hits]
            yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"
            
            # Stream answer tokens
            async for chunk in synthesize_answer_streaming(request.query, hits, use_llm=request.use_llm):
                if chunk.get("type") == "token":
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk['content']})}\n\n"
                elif chunk.get("type") == "error":
                    yield f"data: {json.dumps({'type': 'error', 'content': chunk['content']})}\n\n"
                elif chunk.get("type") == "done":
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
                # Small delay to simulate real-time streaming
                await asyncio.sleep(0.01)
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
