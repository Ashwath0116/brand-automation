from pydantic import BaseModel
from typing import Optional, List, Dict

class BrandingRequest(BaseModel):
    brand_name: str
    brand_description: Optional[str] = None
    keywords: List[str] = []
    tone: Optional[str] = "Professional"
    industry: Optional[str] = None

class BrandNameRequest(BaseModel):
    industry: str
    keywords: List[str]
    tone: Optional[str] = "Professional"
    language: Optional[str] = "en"

class ContentGenerationRequest(BaseModel):
    brand_description: str
    tone: Optional[str] = "Professional"
    content_type: str = "product_description"
    language: Optional[str] = "en"

class SentimentAnalysisRequest(BaseModel):
    text: str
    brand_tone: Optional[str] = "Professional"
    language: Optional[str] = "en"

class ColorPaletteRequest(BaseModel):
    tone: str = "Professional"
    industry: str = "General"

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"

class BrandingResponse(BaseModel):
    brand_names: List[str]
    slogans: List[str]
    logo_prompt: str
    brand_story: Optional[str] = None
    sentiment_analysis: Optional[str] = None

class BrandKitRequest(BaseModel):
    brand_name: str
    industry: str
    keywords: List[str]
    tone: Optional[str] = "Professional"
    language: Optional[str] = "en"

class AdminStatsResponse(BaseModel):
    total_users: int
    total_logs: int
    tool_usage: Dict[str, int]
    recent_logs: List[Dict]
