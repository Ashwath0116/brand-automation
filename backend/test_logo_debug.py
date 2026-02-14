import requests
import json

url = "http://127.0.0.1:8001/api/generate-logo"
payload = {
    "brand_name": "TestBrand",
    "industry": "Tech",
    "keywords": ["modern", "minimal"]
}
headers = {'Content-Type': 'application/json'}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw Response: {response.text}")

except Exception as e:
    print(f"Request failed: {e}")
