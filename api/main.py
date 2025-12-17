from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import os
import json
import time
from typing import Generator

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Warm up the model on startup to ensure first response is fast"""
    print("Pre-loading Llama 3.2 model...")
    try:
        # Just tell Ollama to load the model without generating anything
        requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama3.2",
                "keep_alive": -1  # Load indefinitely
            },
            timeout=5
        )
        print("Model pre-load request sent.")
    except Exception as e:
        print(f"Model pre-load failed (Ollama might not be ready): {e}")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Request model
class ChatRequest(BaseModel):
    prompt: str

# Health check endpoint
@app.get("/health")
def health_check():
    try:
        # Check if Ollama is accessible
        res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        
        # Try to check if model is loaded
        model_loaded = False
        try:
            tags_data = res.json()
            models = tags_data.get("models", [])
            model_loaded = any(m.get("name", "").startswith("llama3.2") for m in models)
        except:
            pass
        
        return {
            "status": "healthy" if res.status_code == 200 else "unhealthy",
            "ollama_url": OLLAMA_URL,
            "ollama_accessible": res.status_code == 200,
            "model_loaded": model_loaded
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama_url": OLLAMA_URL,
            "error": str(e),
            "ollama_accessible": False,
            "model_loaded": False
        }

def check_model_loading(error_message: str) -> bool:
    """Check if error is due to model loading"""
    loading_indicators = [
        "loading",
        "pulling",
        "downloading",
        "not found",
        "model not loaded"
    ]
    return any(indicator in error_message.lower() for indicator in loading_indicators)

def stream_ollama_response(prompt: str) -> Generator[str, None, None]:
    """Stream response from Ollama with retry logic"""
    
    for attempt in range(MAX_RETRIES):
        try:
            # Make streaming request to Ollama
            res = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": True,
                    "keep_alive": -1,  # Load indefinitely
                    "options": {
                        "temperature": 0.7,
                        "num_predict": -1,
                        "num_thread": 4
                    }
                },
                timeout=300,  # 5 minute timeout
                stream=True
            )
            
            if res.status_code != 200:
                error_text = res.text
                
                # Check if model is loading
                if check_model_loading(error_text) and attempt < MAX_RETRIES - 1:
                    yield f"data: {json.dumps({'status': 'loading', 'message': f'Model sedang loading, mencoba lagi dalam {RETRY_DELAY} detik... (percobaan {attempt + 1}/{MAX_RETRIES})'})}\n\n"
                    time.sleep(RETRY_DELAY)
                    continue
                
                yield f"data: {json.dumps({'error': f'Ollama API error: {error_text}'})}\n\n"
                return
            
            # Stream the response
            for line in res.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        
                        if "error" in chunk:
                            yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                            return
                        
                        if "response" in chunk:
                            yield f"data: {json.dumps({'token': chunk['response']})}\n\n"
                        
                        # Check if done
                        if chunk.get("done", False):
                            yield f"data: {json.dumps({'status': 'done'})}\n\n"
                            return
                            
                    except json.JSONDecodeError:
                        continue
            
            # If we got here, streaming completed successfully
            return
            
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                yield f"data: {json.dumps({'status': 'timeout', 'message': f'Request timeout, mencoba lagi... (percobaan {attempt + 1}/{MAX_RETRIES})'})}\n\n"
                time.sleep(RETRY_DELAY)
                continue
            else:
                yield f"data: {json.dumps({'error': 'Request timeout setelah beberapa percobaan. Pertanyaan mungkin terlalu kompleks. Coba dengan pertanyaan yang lebih sederhana atau lebih spesifik.'})}\n\n"
                return
                
        except requests.exceptions.ConnectionError:
            yield f"data: {json.dumps({'error': f'Tidak dapat terhubung ke Ollama di {OLLAMA_URL}. Pastikan container Ollama sedang berjalan.'})}\n\n"
            return
            
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Internal server error: {str(e)}'})}\n\n"
            return

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint using Server-Sent Events"""
    try:
        # Validate that prompt is not empty
        if not request.prompt or request.prompt.strip() == "":
            raise HTTPException(status_code=400, detail="Prompt tidak boleh kosong")
        
        # Warn if prompt is too long
        if len(request.prompt) > 2000:
            raise HTTPException(
                status_code=400, 
                detail="Prompt terlalu panjang (maksimal 2000 karakter). Coba perpendek pertanyaan Anda."
            )
        
        return StreamingResponse(
            stream_ollama_response(request.prompt),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/chat")
def chat(request: ChatRequest):
    """Non-streaming chat endpoint (backward compatibility)"""
    try:
        # Validate that prompt is not empty
        if not request.prompt or request.prompt.strip() == "":
            raise HTTPException(status_code=400, detail="Prompt tidak boleh kosong")
        
        # Warn if prompt is too long
        if len(request.prompt) > 2000:
            raise HTTPException(
                status_code=400, 
                detail="Prompt terlalu panjang (maksimal 2000 karakter). Coba perpendek pertanyaan Anda."
            )
        
        # Try with retry logic
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                # Make request to Ollama with increased timeout and keep_alive
                res = requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": request.prompt,
                        "stream": False,
                        "keep_alive": -1,  # Load indefinitely
                        "options": {
                            "temperature": 0.7,
                            "num_predict": -1,
                            "num_thread": 4
                        }
                    },
                    timeout=300  # 5 minute timeout for longer responses
                )
                
                # Check if request was successful
                if res.status_code != 200:
                    error_text = res.text
                    
                    # Check if model is loading
                    if check_model_loading(error_text) and attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    
                    raise HTTPException(
                        status_code=res.status_code,
                        detail=f"Ollama API error: {error_text}"
                    )
                
                response_data = res.json()
                
                # Check if response contains the expected field
                if "response" not in response_data:
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid response from Ollama API"
                    )
                
                return {"response": response_data["response"]}
                
            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Tidak dapat terhubung ke Ollama di {OLLAMA_URL}. Pastikan container Ollama sedang berjalan."
                )
        
        # If we exhausted all retries
        raise HTTPException(
            status_code=504,
            detail="Request timeout setelah beberapa percobaan. Pertanyaan mungkin terlalu kompleks. Coba gunakan endpoint streaming (/chat/stream) atau perpendek pertanyaan Anda."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
