

import os
from typing import List, Dict, AsyncGenerator
import asyncio

GPT4ALL_MODEL_PATH = os.getenv("GPT4ALL_MODEL", "")



def remove_duplicate_sentences(text: str) -> str:
    seen = set()
    unique = []
    for sentence in text.split("."):
        s = sentence.strip()
        if s and s not in seen:
            seen.add(s)
            unique.append(s)
    return ". ".join(unique)

def generate_with_gpt4all(prompt: str, max_tokens: int = 200) -> str:
    if not GPT4ALL_MODEL_PATH:
        raise Exception("GPT4ALL_MODEL environment variable not set")
    if not os.path.exists(GPT4ALL_MODEL_PATH):
        raise Exception(f"GPT4All model file not found: {GPT4ALL_MODEL_PATH}")
    try:
        from gpt4all import GPT4All
        model = GPT4All(GPT4ALL_MODEL_PATH)
        response = model.generate(prompt, max_tokens=max_tokens, temp=0.7)
        return response.strip()
    except ImportError:
        raise Exception("gpt4all package not installed. Install with: pip install gpt4all")
    except Exception as e:
        raise Exception(f"Error generating with GPT4All: {str(e)}")

def synthesize_answer(query: str, hits: List[Dict], use_llm: bool = False) -> Dict:
    if not hits:
        return {"answer": "I couldn't find any relevant information to answer your query.", "sources": []}
    if use_llm:
        try:
            context = "\n\n".join([f"Source {i+1} (from {hit['meta'].get('url', 'unknown')}):\n{hit['text']}" for i, hit in enumerate(hits[:3])])
            prompt = f"""Based on the following context, answer the question. If the answer is not in the context, say so.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"""
            answer = generate_with_gpt4all(prompt, max_tokens=300)
            sources = [hit['meta'] for hit in hits]
            return {"answer": answer, "sources": sources}
        except Exception as e:
            error_msg = str(e)
            print(f"LLM generation failed: {error_msg}")
            fallback = _generate_fallback_answer(query, hits)
            fallback["llm_error"] = error_msg
            return fallback
    return _generate_fallback_answer(query, hits)

def _generate_fallback_answer(query: str, hits: List[Dict]) -> Dict:
    top_hits = hits[:3]
    snippets = []
    for hit in top_hits:
        text = hit['text']
        if len(text) > 300:
            text = text[:300] + "..."
        snippets.append(text)
    combined = " ".join(snippets)
    combined = remove_duplicate_sentences(combined)
    if len(combined) > 1500:
        combined = combined[:1500] + "..."
    answer = f"Based on the retrieved information:\n\n{combined}"
    sources = [hit['meta'] for hit in hits]
    return {"answer": answer, "sources": sources}


async def synthesize_answer_streaming(query: str, hits: List[Dict], use_llm: bool = False):
    """
    Final version that bypasses the library's streaming bug.
    It generates the full response first, then streams it word by word.
    """
    print("\n--- Starting FINAL synthesize_answer_streaming ---")
    print(f"Query: '{query}'")
    print(f"Use LLM requested: {use_llm}")

    if not hits:
        yield {"type": "error", "content": "No relevant information found"}
        return

    if use_llm:
        print("\n[STEP 1] Attempting to use the LLM...")
        try:
            if not GPT4ALL_MODEL_PATH or not os.path.exists(GPT4ALL_MODEL_PATH):
                raise FileNotFoundError("GPT4ALL_MODEL path is not set or file not found.")

            from gpt4all import GPT4All
            model = GPT4All(GPT4ALL_MODEL_PATH)
            print("   -> Model loaded.")

            context = hits[0]['text']
            prompt = f"Using the following text, answer the user's question.\n\nText: {context}\n\nQuestion: {query}\n\nAnswer:"
            print(f"[STEP 2] Generating full response (non-streaming)...")

         
            full_response = model.generate(prompt, max_tokens=350, temp=0.7, streaming=False)

            if not full_response.strip():
                raise RuntimeError("LLM generated an empty response.")

            print(f"[SUCCESS] LLM generated a full response: '{full_response[:100]}...'")
            
            print("[STEP 3] Now streaming the generated response word by word...")
            
            words = full_response.split()
            for word in words:
                print(f"Streaming word: '{word}'") 
                yield {"type": "token", "content": word + " "}
                await asyncio.sleep(0.01) 

            
            yield {"type": "done"}
            return

        except Exception as e:
            error_message = f"LLM FAILED: {type(e).__name__}: {e}. Switching to fallback mode."
            print(f"\n[ERROR] {error_message}")
            yield {"type": "token", "content": f"\n\n[DEBUGGER: {error_message}]\n\n"}

    print("\n[FALLBACK] Using the fallback answer generation method.")
    fallback_result = _generate_fallback_answer(query, hits)
    answer_text = fallback_result["answer"]
    
    words = answer_text.split()
    for word in words:
        yield {"type": "token", "content": word + " "}
    
    yield {"type": "done"}
    print("--- Stream finished using fallback. ---")
