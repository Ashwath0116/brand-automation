import requests
import json
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

url = "http://127.0.0.1:8001/api/generate-brand"
payload = {
    "industry": "technology",
    "keywords": ["fast", "innovation"],
    "tone": "Professional",
    "language": "hi"  # Requesting Hindi
}
headers = {'Content-Type': 'application/json'}

try:
    print(f"Sending request to {url} with language='hi'...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    # Print raw text first to see if it's garbled
    # print(f"Raw Text: {response.text}")

    data = response.json()
    print("Response JSON (Formatted):")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    if data.get("success") and data.get("data"):
        print("\n✅ Success! Check if the above text looks like Hindi.")
    else:
        print("\n❌ Failure: Structure incorrect.")

except Exception as e:
    print(f"Request failed: {e}")
