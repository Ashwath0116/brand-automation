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
from .models import BrandingRequest, BrandNameRequest, ContentGenerationRequest, SentimentAnalysisRequest, ColorPaletteRequest, ChatRequest, BrandKitRequest
from .ai_services import AIService
from .auth import router as auth_router, get_current_user
from .database import init_db, get_db, BrandingLog, User
from sqlalchemy.orm import Session as DBSession
from fastapi import Depends

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

# --- Helper: Log AI Usage ---
async def log_ai_usage(db: DBSession, user, tool_type: str, prompt: str, result: str):
    try:
        user_id = user.id if user else None
        log = BrandingLog(
            user_id=user_id,
            tool_type=tool_type,
            prompt=str(prompt)[:1000],
            result_summary=str(result)[:500]
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Logging failed: {e}")

# Ensure directories exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.post("/api/generate-logo")
async def generate_logo_endpoint(request: BrandingRequest, db: DBSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        # 1. Generate Prompt
        prompt_result = await ai_service.generate_logo_prompt(
            request.brand_name, 
            request.industry or "General",
            request.keywords
        )
        
        # 2. Generate Image
        image_result = await ai_service.generate_logo_image(prompt_result)
        
        await log_ai_usage(db, user, "logo", request.brand_name, f"Prompt: {prompt_result[:100]}...")
        
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
async def generate_brand_endpoint(request: BrandNameRequest, db: DBSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await ai_service.generate_brand_names(
            request.industry,
            request.keywords,
            request.tone,
            request.language
        )
        await log_ai_usage(db, user, "brand", f"{request.industry} | {request.keywords}", f"Got {len(result)} names")
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-content")
async def generate_content_endpoint(request: ContentGenerationRequest, db: DBSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await ai_service.generate_marketing_content(
            request.brand_description,
            request.tone,
            request.content_type,
            request.language
        )
        await log_ai_usage(db, user, "content", request.content_type, f"{result[:100]}...")
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
async def analyze_sentiment_endpoint(request: SentimentAnalysisRequest, db: DBSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await ai_service.analyze_sentiment(request.text, request.brand_tone, request.language)
        await log_ai_usage(db, user, "sentiment", request.text[:100], result.get("sentiment"))
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get-colors")
async def get_colors_endpoint(request: ColorPaletteRequest, db: DBSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await ai_service.get_color_palette(request.tone, request.industry)
        await log_ai_usage(db, user, "color", f"{request.tone} | {request.industry}", ",".join(result.get("palette", [])))
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: DBSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        result = await ai_service.chat_with_ai(request.message, request.language)
        await log_ai_usage(db, user, "chat", request.message, result[:100])
        return {"success": True, "data": {"content": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New Endpoint: Brand Kit Generator
@app.post("/api/generate-brand-kit")
async def generate_brand_kit(request: BrandKitRequest, db: DBSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        # 1. Names
        names = await ai_service.generate_brand_names(request.industry, request.keywords, request.tone, request.language)
        
        # 2. Colors
        colors = await ai_service.get_color_palette(request.tone, request.industry)
        
        # 3. Logo Prompt
        logo_prompt = await ai_service.generate_logo_prompt(request.brand_name, request.industry, request.keywords)
        
        # 4. Tagline
        tagline = await ai_service.generate_marketing_content(f"A {request.tone} brand in {request.industry} called {request.brand_name}", request.tone, "tagline", request.language)

        result = {
            "names": names[:5],
            "colors": colors,
            "logo_prompt": logo_prompt,
            "tagline": tagline
        }
        await log_ai_usage(db, user, "kit", request.brand_name, "Complete kit generated")
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New Endpoint: Admin Stats
@app.get("/api/auth/admin/stats")
async def admin_stats(request: Request, db: DBSession = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_admin:
        raise HTTPException(403, "Admin access required")

    total_users = db.query(User).count()
    total_logs = db.query(BrandingLog).count()
    
    # Tool breakdown
    from sqlalchemy import func
    usage_breakdown = db.query(BrandingLog.tool_type, func.count(BrandingLog.tool_type)).group_by(BrandingLog.tool_type).all()
    tool_usage = {tool: count for tool, count in usage_breakdown}
    
    # Recent activity
    recent = db.query(BrandingLog, User.name).join(User, User.id == BrandingLog.user_id, isouter=True).order_by(BrandingLog.created_at.desc()).limit(10).all()
    
    recent_logs = []
    for log, uname in recent:
        recent_logs.append({
            "id": log.id,
            "user": uname or "Guest",
            "tool": log.tool_type,
            "prompt": log.prompt,
            "result": log.result_summary,
            "time": log.created_at.isoformat()
        })

    return {
        "success": True,
        "total_users": total_users,
        "total_logs": total_logs,
        "tool_usage": tool_usage,
        "recent_logs": recent_logs
    }

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
