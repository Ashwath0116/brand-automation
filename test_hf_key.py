
from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

load_dotenv('backend/.env')
key = os.getenv('HF_API_KEY')
print(f"Key loaded: {key[:4] if key else 'None'}...")

if not key or key == "PASTE_YOUR_NEW_KEY_HERE":
    print("Invalid Key format")
    exit()

client = InferenceClient(token=key)
try:
    print("Testing stable-diffusion-xl-base-1.0...")
    client.text_to_image("test logo", model="stabilityai/stable-diffusion-xl-base-1.0")
    print("Success")
except Exception as e:
    print("Fail:", e)
