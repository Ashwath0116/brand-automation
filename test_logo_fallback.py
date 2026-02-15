
import requests
import json
import time

url = "http://127.0.0.1:8000/api/generate-logo"

payload = {
    "brand_name": "FrontendTestBrand",
    "industry": "Technology",
    "keywords": ["innovation", "cloud"]
}

try:
    print("Testing backend logic...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    image_url = data.get("data", {}).get("image_result", {}).get("image_url")
    print(f"Returned Image URL: {image_url}")
    
    if "pollinations.ai" in image_url:
        print("Success: Backend returned external Pollinations URL as fallback.")
    elif "test_logo_api" in image_url or "logo_" in image_url:
        print("Success: File was downloaded locally.")
    else:
        print("Warning: Unexpected URL format.")

except Exception as e:
    print(f"Request failed: {e}")
