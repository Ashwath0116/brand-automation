import requests
import json

url = "http://127.0.0.1:8001/api/generate-brand"
payload = {
    "industry": "tech",
    "keywords": ["fast"],
    "tone": "Professional",
    "language": "es"  # Requesting Spanish
}
headers = {'Content-Type': 'application/json'}

try:
    print(f"Sending request to {url} with language='es'...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print("Response JSON:")
    print(json.dumps(data, indent=2))
    
    # Simple check if response looks Spanish-ish
    if data.get("success") and data.get("data"):
        first_explanation = data["data"][0]["explanation"]
        print(f"\nFirst Explanation: {first_explanation}")
        if "velocidad" in first_explanation.lower() or "rápido" in first_explanation.lower() or "tecnología" in first_explanation.lower():
             print("✅ Potential Spanish detected.")
        else:
             print("⚠️ Response might still be in English.")

except Exception as e:
    print(f"Request failed: {e}")
