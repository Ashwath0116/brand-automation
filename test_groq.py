import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Create chat completion
try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Generate 3 creative brand names for an AI startup."}]
    )
    print("Response from Groq:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
