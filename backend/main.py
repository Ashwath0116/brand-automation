from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import os
import speech_recognition as sr
from pydub import AudioSegment
import io

# Import local modules
from .models import BrandingRequest, BrandNameRequest, ContentGenerationRequest, SentimentAnalysisRequest, ColorPaletteRequest, ChatRequest
from .ai_services import AIService
from .auth import router as auth_router
from .database import init_db

app = FastAPI()

# Initialize database
init_db()

# Initialize AI Service
ai_service = AIService()

# Register auth router
app.include_router(auth_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

# Ensure directories exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.post("/api/generate-logo")
async def generate_logo_endpoint(request: BrandingRequest):
    try:
        # 1. Generate Prompt
        prompt_result = await ai_service.generate_logo_prompt(
            request.brand_name, 
            request.industry or "General",
            request.keywords
        )
        
        # 2. Generate Image (Activity 2.4 - Keeping this as value add, but prompt is key for 2.10)
        image_result = await ai_service.generate_logo_image(prompt_result)
        
        return {
            "success": True, 
            "data": {
                "prompt": prompt_result,
                "image_result": image_result
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-brand")
async def generate_brand_endpoint(request: BrandNameRequest):
    try:
        result = await ai_service.generate_brand_names(
            request.industry,
            request.keywords,
            request.tone,
            request.language
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-content")
async def generate_content_endpoint(request: ContentGenerationRequest):
    try:
        result = await ai_service.generate_marketing_content(
            request.brand_description,
            request.tone,
            request.content_type,
            request.language
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcribe-voice")
async def transcribe_voice(audio_file: UploadFile = File(...)):
    """
    Transcribe audio file using Google Speech-to-Text API (Free fallback)
    Handles MP3/WAV/OGG via pydub conversion if ffmpeg is available.
    """
    temp_filename = "temp_audio.wav"
    try:
        # Read audio file
        audio_content = await audio_file.read()
        
        # Try converting to WAV using pydub (handles mp3, etc.)
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_content))
            audio_segment.export(temp_filename, format="wav")
        except Exception as e:
            print(f"Pydub conversion failed (ffmpeg missing?): {e}")
            # Fallback: Write raw bytes assuming it's already WAV
            with open(temp_filename, "wb") as f:
                f.write(audio_content)
            
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load audio file
        with sr.AudioFile(temp_filename) as source:
            audio_data = recognizer.record(source)
            
        # Transcribe
        text = recognizer.recognize_google(audio_data)
        
        return {"success": True, "text": text}
        
    except sr.UnknownValueError:
        return {"success": False, "error": "Could not understand audio"}
    except sr.RequestError as e:
        return {"success": False, "error": f"Could not request results; {e}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.post("/api/analyze-sentiment")
async def analyze_sentiment_endpoint(request: SentimentAnalysisRequest):
    try:
        result = await ai_service.analyze_sentiment(request.text, request.brand_tone, request.language)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get-colors")
async def get_colors_endpoint(request: ColorPaletteRequest):
    try:
        result = await ai_service.get_color_palette(request.tone, request.industry)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        result = await ai_service.chat_with_ai(request.message, request.language)
        return {"success": True, "data": {"content": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Frontend Routing
@app.get("/{page}.html")
async def serve_page(page: str):
    file_path = FRONTEND_DIR / f"{page}.html"
    if file_path.exists():
        return FileResponse(file_path)
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
