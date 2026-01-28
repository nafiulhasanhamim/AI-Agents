"""
Thorough Google Gemini Model Discovery Script
Lists all models available to your specific API key and saves to a UTF-8 file.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key or "YOUR_NEW_KEY" in api_key:
    output = "Error: GOOGLE_API_KEY is not set correctly in .env!\n"
    output += f"Current value: {api_key}\n"
    with open("model_discovery_output.txt", "w", encoding="utf-8") as f:
        f.write(output)
    exit(1)

output = f"Using API Key: {api_key[:10]}...{api_key[-5:]}\n\n"

try:
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    
    output += "Querying Google AI for available models...\n"
    output += "=" * 60 + "\n"
    
    found_any = False
    for m in genai.list_models():
        found_any = True
        # Check if it supports generateContent
        support = "[YES]" if "generateContent" in m.supported_generation_methods else "[NO]"
        output += f"{support} Name: {m.name}\n"
        output += f"   Display: {m.display_name}\n"
        output += f"   Description: {m.description[:100]}...\n"
        output += "-" * 40 + "\n"
        
    if not found_any:
        output += "Error: No models returned. This key might not have access to the Generative AI API yet.\n"
        
except Exception as e:
    output += f"Error listing models: {str(e)}\n"
    output += "\nTroubleshooting:\n"
    output += "1. Check if your API key is correct in the .env file\n"
    output += "2. Ensure you are not behind a restrictive proxy\n"
    output += "3. Verify the key is from Google AI Studio (not Vertex AI)\n"

with open("model_discovery_output.txt", "w", encoding="utf-8") as f:
    f.write(output)

print("Discovery complete. Results saved to model_discovery_output.txt")
