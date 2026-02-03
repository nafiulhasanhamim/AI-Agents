import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models_to_test = [
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-1.0-pro-latest",
    "models/gemini-1.5-flash-8b", 
    "models/gemini-2.0-flash-lite-001"
]

print("Testing Model Availability & Quotas...\n")

for model in models_to_test:
    print(f"Testing {model}...", end=" ")
    try:
        m = genai.GenerativeModel(model)
        response = m.generate_content("Say hello")
        print(f"✅ SUCCESS! Response: {response.text.strip()}")
    except Exception as e:
        if "404" in str(e):
            print("❌ NOT FOUND")
        elif "429" in str(e) or "RESOURCE" in str(e):
            print("⚠️ RATE LIMITED (Quota Full)")
        else:
            print(f"❌ ERROR: {e}")
