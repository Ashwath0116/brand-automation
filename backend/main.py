from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import os
import json
import speech_recognition as sr
from pydub import AudioSegment
import io

# Import local modules
from .models import BrandingRequest, BrandNameRequest, ContentGenerationRequest, SentimentAnalysisRequest, ColorPaletteRequest, ChatRequest
from .ai_services import AIService
from .auth import router as auth_router, get_current_user
from .database import init_db, get_db, ActivityLog, SessionLocal

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

# ── Helper: Log user activity ──
def log_activity(request: Request, action: str, request_data: dict, response_data: dict, status: str = "success"):
    """Save a user action to the database."""
    try:
        db = SessionLocal()
        # Try to get current user from cookie
        user_id = None
        user_email = None
        token = request.cookies.get("session_token")
        if token:
            from .database import Session as DBSession, User
            session = db.query(DBSession).filter(DBSession.token == token).first()
            if session:
                user = db.query(User).filter(User.id == session.user_id).first()
                if user:
                    user_id = user.id
                    user_email = user.email
        
        ip = request.client.host if request.client else "unknown"
        
        log = ActivityLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            request_data=json.dumps(request_data, default=str)[:10000],
            response_data=json.dumps(response_data, default=str)[:10000],
            status=status,
            ip_address=ip
        )
        db.add(log)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Activity log error: {e}")

@app.post("/api/generate-logo")
async def generate_logo_endpoint(request: Request, req: BrandingRequest):
    req_data = {"brand_name": req.brand_name, "industry": req.industry or "General", "keywords": req.keywords}
    try:
        prompt_result = await ai_service.generate_logo_prompt(
            req.brand_name, 
            req.industry or "General",
            req.keywords
        )
        image_result = await ai_service.generate_logo_image(prompt_result)
        
        resp = {
            "success": True, 
            "data": {
                "prompt": prompt_result,
                "image_result": image_result
            }
        }
        log_activity(request, "generate_logo", req_data, {"prompt": prompt_result, "image_url": image_result})
        return resp
    except Exception as e:
        log_activity(request, "generate_logo", req_data, {"error": str(e)}, status="error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-brand")
async def generate_brand_endpoint(request: Request, req: BrandNameRequest):
    req_data = {"industry": req.industry, "keywords": req.keywords, "tone": req.tone, "language": req.language}
    try:
        result = await ai_service.generate_brand_names(
            req.industry, req.keywords, req.tone, req.language
        )
        resp = {"success": True, "data": result}
        log_activity(request, "generate_brand", req_data, {"brand_names": result})
        return resp
    except Exception as e:
        log_activity(request, "generate_brand", req_data, {"error": str(e)}, status="error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-content")
async def generate_content_endpoint(request: Request, req: ContentGenerationRequest):
    req_data = {"brand_description": req.brand_description, "tone": req.tone, "content_type": req.content_type, "language": req.language}
    try:
        result = await ai_service.generate_marketing_content(
            req.brand_description, req.tone, req.content_type, req.language
        )
        resp = {"success": True, "data": result}
        log_activity(request, "generate_content", req_data, {"generated_content": result})
        return resp
    except Exception as e:
        log_activity(request, "generate_content", req_data, {"error": str(e)}, status="error")
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
async def analyze_sentiment_endpoint(request: Request, req: SentimentAnalysisRequest):
    req_data = {"text": req.text, "brand_tone": req.brand_tone, "language": req.language}
    try:
        result = await ai_service.analyze_sentiment(req.text, req.brand_tone, req.language)
        resp = {"success": True, "data": result}
        log_activity(request, "analyze_sentiment", req_data, {"analysis_result": result})
        return resp
    except Exception as e:
        log_activity(request, "analyze_sentiment", req_data, {"error": str(e)}, status="error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get-colors")
async def get_colors_endpoint(request: Request, req: ColorPaletteRequest):
    req_data = {"tone": req.tone, "industry": req.industry}
    try:
        result = await ai_service.get_color_palette(req.tone, req.industry)
        resp = {"success": True, "data": result}
        log_activity(request, "get_colors", req_data, {"palette": result})
        return resp
    except Exception as e:
        log_activity(request, "get_colors", req_data, {"error": str(e)}, status="error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: Request, req: ChatRequest):
    req_data = {"message": req.message, "language": req.language}
    try:
        result = await ai_service.chat_with_ai(req.message, req.language)
        resp = {"success": True, "data": {"content": result}}
        log_activity(request, "chat", req_data, {"ai_response": result})
        return resp
    except Exception as e:
        log_activity(request, "chat", req_data, {"error": str(e)}, status="error")
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
