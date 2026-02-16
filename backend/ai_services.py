import os
import json
import random
import time
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

# AI Libraries
import re
from groq import Groq
from huggingface_hub import InferenceClient
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

class AIService:
    def __init__(self):
        # 1. Groq Setup
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.groq_api_key:
             self.groq_client = Groq(api_key=self.groq_api_key)
        else:
             self.groq_client = None
             print("⚠️ Warning: GROQ_API_KEY not set.")

        # 2. Hugging Face Setup (for SDXL)
        self.hf_api_key = os.getenv("HF_API_KEY")
        if self.hf_api_key:
            self.hf_client = InferenceClient(token=self.hf_api_key)
        else:
            self.hf_client = None
            print("⚠️ Warning: HF_API_KEY not set.")

        # 3. IBM Granite Setup (Local)
        self.granite_model = None
        self.granite_tokenizer = None
        self.device = "cpu" # Default to CPU as per request
        
        # Lazy load Granite to avoid long startup if not needed immediately, 
        # or load now if preferred. The snippet showed loading on init.
        # I'll add a method to load it to keep startup fast, or load in a separate thread.
        # For now, I'll put it in a try-block but maybe comment it out or make it optional
        # to prevent startup freeze if the model is large.
        # However, the user snippet showed it running. I will implement a `load_granite` method.
    
    def load_granite(self):
        if self.granite_model:
            return
        
        print("🔹 Loading IBM Granite 4.0-h-350m...")
        try:
            model_id = "ibm-granite/granite-4.0-h-350m"
            self.granite_tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            self.granite_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float32,
                trust_remote_code=True
            ).to(self.device)
            self.granite_model.eval()
            print("✅ IBM Granite loaded!")
        except Exception as e:
            print(f"❌ Granite load failed: {e}")

    async def generate_with_groq(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> str:
        if not self.groq_client:
            return "❌ Error: GROQ_API_KEY not set."
            
        try:
            message = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
            )
            return message.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in Groq generation: {e}")
            return f"Error: {e}"

    # --- Feature: Brand Name Generator (Activity 2.5) ---
    async def generate_brand_names(self, industry: str, keywords: List[str], tone: str, language: str = "en") -> List[Dict]:
        prompt = f"""
        You are BizForge. Generate 10-20 unique, memorable, and brand-ready names for a business.
        
        Industry: {industry}
        Keywords: {', '.join(keywords)}
        Tone: {tone}
        Target Language: {language}
        
        IMPORTANT: Provide the "explanation" strictly in the target language ({language}). 
        
        Script Rules:
        - If language is Hindi (hi): Name AND Explanation MUST be in Devanagari script.
        - If language is Telugu (te): Name AND Explanation MUST be in Telugu script. do NOT use English characters.
        - Other languages: Name in Latin alphabet, Explanation in target language.
        
        Return ONLY a JSON list of objects with keys "name" and "explanation".
        Example for Hindi:
        [
            {{"name": "ऊर्जा", "explanation": "यह नाम शक्ति और गति को दर्शाता है।"}},
            {{"name": "नवप्रवर्तन", "explanation": "नयापन और विकास का प्रतीक।"}}
        ]
        Example for Telugu:
        [
            {{"name": "వేగం", "explanation": "ఇది వేగం మరియు శక్తిని సూచిస్తుంది."}},
            {{"name": "నవీకరణ", "explanation": "క్రొత్తదనం మరియు అభివృద్ధికి చిహ్నం."}}
        ]
        """
        response = await self.generate_with_groq(prompt, max_tokens=1000)
        try:
            # 1. Try to find JSON array using regex
            cleaned = response.strip()
            match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if match:
                potential_json = match.group(0)
                return json.loads(potential_json)
            
            # 2. Try parsing the whole string if regex didn't match
            return json.loads(cleaned)
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            # 3. Fallback: Try to parse line-by-line as individual JSON objects
            results = []
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue
                # Remove trailing commas
                if line.endswith(','): line = line[:-1]
                try:
                    obj = json.loads(line)
                    if "name" in obj and "explanation" in obj:
                        results.append(obj)
                except:
                    pass
            
            if results:
                return results

            # 4. Old Fallback (last resort)
            print("Using manual string splitting fallback")
            lines = [line.strip() for line in response.split('\n') if line.strip() and ('-' in line or ':' in line)]
            results = []
            for line in lines[:15]:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    name_part = parts[0].strip(' -*"{}')
                    expl_part = parts[1].strip(' ,}"')
                    results.append({"name": name_part, "explanation": expl_part})
            return results

    # --- Feature: Logo Prompt Generation (Text) ---
    async def generate_logo_prompt(self, brand_name: str, industry: str, keywords: List[str], description: str = None) -> str:
        user_vision = f'- User Vision: "{description}"' if description else ""
        
        prompt = f"""
        You are an expert logo designer. Create a precise text-to-image prompt for a modern logo.
        
        Context:
        - Brand: "{brand_name}"
        - Industry: {industry}
        - Keywords: {', '.join(keywords)}
        {user_vision}
        
        Guidelines:
        1. VISUAL SYMBOL: Describe a clear, central pictorial mark or icon representing the brand.
        2. STYLE: Request "vector art", "minimalist", "geometric", or "abstract" as appropriate for the industry.
        3. COMPOSITION: Ensure the logo is centered on a white background.
        4. COLORS: Suggest a professional color palette.
        5. NO TEXT: Do not ask for the brand name to be written in the image (generators struggle with text). Focus on the icon.
        6. USER VISION: If a user vision is provided, prioritize it above other suggestions.
        
        Output ONLY the prompt string.
        """
        return await self.generate_with_groq(prompt, max_tokens=200)

    # --- Feature: Marketing Content Generation (Activity 2.6) ---
    async def generate_marketing_content(self, brand_description: str, tone: str, content_type: str, language: str = "en") -> str:
        prompt = f"""
        You are an expert marketing copywriter for BizForge.
        Generate high-quality {content_type} for the following brand.
        
        Brand Description: {brand_description}
        Tone: {tone}
        Target Language: {language}
        
        IMPORTANT: Write the content STRICTLY in the target language ({language}).
        If the language is Hindi (hi), use Devanagari script.
        If the language is Telugu (te), use Telugu script. Do NOT use English.
        
        Ensure the content is engaging, conversion-optimized, and strictly adheres to the requested tone.
        Return ONLY the generated content text.
        """
        return await self.generate_with_groq(prompt, max_tokens=800)

    # --- Feature: Logo Image Generation ---
    async def generate_logo_image(self, logo_prompt: str) -> Dict:
        hf_error = None
        # 1. Try Hugging Face (Primary)
        if self.hf_client:
            try:
                print(f"Generating image with Hugging Face (SDXL)...")
                # Use a specific model
                model = "stabilityai/stable-diffusion-xl-base-1.0"
                # Enhanced Prompt for HF
                enhanced_hf_prompt = f"minimalist vector logo, flat design, white background, simple, iconic, {logo_prompt}, dribbble style, 8k, no text"
                negative_prompt = "text, watermark, realistic, photo, 3d render, complex, busy, gradient, shadow, low quality, blurry"
                
                # text_to_image is a helper in InferenceClient
                image = self.hf_client.text_to_image(
                    enhanced_hf_prompt, 
                    model=model,
                    negative_prompt=negative_prompt
                )
                
                # Save image
                timestamp = int(time.time())
                filename = f"logo_{timestamp}.png"
                output_dir = Path(__file__).resolve().parent.parent / "frontend" / "static" / "generated_logos"
                output_dir.mkdir(parents=True, exist_ok=True)
                filepath = output_dir / filename
                
                image.save(filepath)
                print(f"Image saved to: {filepath}")
                
                return {
                    "image_url": f"/static/generated_logos/{filename}",
                    "success": True,
                    "error": None
                }
            except Exception as e:
                print(f"HF Generation failed: {e}")
                hf_error = str(e)
                # Fallthrough to backup
        else:
            print("HF Client not initialized. Skipping HF generation.")

        # 2. Pollinations.ai (Backup)
        try:
            print(f"Generating image with Pollinations.ai (Free Backup)...")
            
            # Encoded prompt for URL
            import urllib.parse
            import requests

            # Enhanced prompt
            seed = random.randint(1, 100000)
            enhanced_prompt = (
                f"Logo design, {logo_prompt}, "
                f"vector graphics, white background, centered, high quality, 4k, professional, sharp lines, minimalism, no text"
            )
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Pollinations URL (Direct Image Endpoint)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&model=flux"
            
            # Fetch the image
            response = requests.get(image_url, timeout=30)
            
            if response.status_code != 200:
                 raise Exception(f"Pollinations API Status: {response.status_code}")
                 
            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                raise Exception(f"Pollinations returned non-image content: {content_type}")

            # Save image
            output_dir = Path(__file__).resolve().parent.parent / "frontend" / "static" / "generated_logos"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = int(time.time())
            filename = f"logo_{timestamp}.png"
            filepath = output_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(response.content)
                
            print(f"Image saved to: {filepath}")
            
            return {
                "image_url": f"/static/generated_logos/{filename}",
                "success": True,
                "error": None
            }
        except Exception as e:
            print(f"Image Download failed: {e}")
            # If backend download fails (e.g. 403/530 blocking), try returning the URL 
            # for the frontend to load directly.
            print("Attempting to return external URL for frontend to load directly...")
            return {
                "image_url": image_url,
                "success": True,
                "error": None
            }

    # --- Feature: Chatbot (Activity 2.9) ---
    async def chat_with_ai(self, message: str, language: str = "en") -> str:
        system_prompt = f"You are BizForge, an expert branding assistant. Provide strategic and actionable branding insights. Answer in {language}."
        full_prompt = f"{system_prompt}\n\nUser: {message}\nBizForge:"

        # 1. Try Granite (if loaded or loadable)
        if self.granite_model:
             try:
                inputs = self.granite_tokenizer(full_prompt, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    outputs = self.granite_model.generate(**inputs, max_new_tokens=150)
                return self.granite_tokenizer.decode(outputs[0], skip_special_tokens=True).split("BizForge:")[-1].strip()
             except Exception as e:
                print(f"Granite failed, falling back to Groq: {e}")
        
        # 2. Fallback to Groq
        if self.groq_client:
            try:
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=200
                )
                return completion.choices[0].message.content
            except Exception as e:
                return f"Error: {e}"
        
        return "Error: No AI model available."

    async def chat_with_granite(self, message: str) -> str:
        # Deprecated/Internal use, redirected to main chat function
        return await self.chat_with_ai(message)

    async def analyze_sentiment(self, text: str, tone: str, language: str = "en") -> Dict:
        prompt = f"""
        Analyze the sentiment of the following text against the brand tone '{tone}'.
        Provide the analysis in {language}.
        
        Text: "{text}"
        
        Return ONLY a JSON object with:
        - "sentiment": "Positive", "Neutral", "Negative" (Keep these English keys/values for logic, but translates descriptions/suggestions if applicable)
        - "confidence": Float (0.0 - 1.0)
        - "tone_alignment": String (One sentence insight on how well it matches the '{tone}' tone, in {language})
        - "suggestions": String (Suggestions for improvement, in {language})
        - "rewritten_text": String (Rewrite the text to match the tone better, in {language})
        """
        res = await self.generate_with_groq(prompt)
        try:
             # Basic cleanup
            cleaned = res.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:-3]
            elif cleaned.startswith("```"): cleaned = cleaned[3:-3]
            return json.loads(cleaned)
        except:
            return {
                "sentiment": "Neutral", 
                "confidence": 0.5, 
                "tone_alignment": "Could not analyze alignment.",
                "suggestions": "Validation failed.",
                "rewritten_text": None
            }

    async def get_color_palette(self, tone: str, industry: str) -> Dict:
        prompt = f"""
        Generate a professional color palette for a {tone} brand in the {industry} industry.
        Return ONLY a JSON object with:
        - "palette": List of 3-5 HEX color codes (strings).
        - "explanation": Brief explanation of why these colors fit the tone/industry.
        """
        res = await self.generate_with_groq(prompt)
        try:
            cleaned = res.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:-3]
            elif cleaned.startswith("```"): cleaned = cleaned[3:-3]
            return json.loads(cleaned)
        except:
            return {
                "palette": ["#2C3E50", "#E74C3C", "#ECF0F1", "#3498DB", "#2980B9"],
                "explanation": "Fallback palette due to generation error."
            }
