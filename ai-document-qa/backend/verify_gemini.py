"""
Final Verification for Google Gemini Models
Tests the most promising models found in the discovery phase.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GOOGLE_API_KEY")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    test_models = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]
    
    results = []
    for model_name in test_models:
        print(f"Testing {model_name}...", end=" ", flush=True)
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0
            )
            response = llm.invoke("Hello, respond with 'OK'")
            print(f"✅ Success: {response.content}")
            results.append((model_name, True))
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}...")
            results.append((model_name, False))
            
    print("\nFinal Recommendation:")
    valid_models = [m for m, s in results if s]
    if valid_models:
        print(f"Use: {valid_models[0]}")
    else:
        print("No models worked. Please check API key status in AI Studio.")
        
except Exception as e:
    print(f"Error: {e}")
