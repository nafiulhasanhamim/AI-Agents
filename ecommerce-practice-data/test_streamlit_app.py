#!/usr/bin/env python3
"""
Test script to verify the updated Streamlit app works with the enhanced system
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_imports():
    """Test that the app can import all required modules"""
    print("🧪 Testing Streamlit App Imports...")
    
    try:
        # Test enhanced assistant import
        from enhanced_assistant import EnhancedAssistant
        print("✅ Enhanced Assistant import successful")
        
        # Test streamlit import
        import streamlit as st
        print("✅ Streamlit import successful")
        
        # Test assistant initialization
        assistant = EnhancedAssistant()
        print("✅ Enhanced Assistant initialization successful")
        
        # Test a simple query
        response = assistant.query("What products do you have?")
        print(f"✅ Sample query successful: {response[:100]}...")
        
        print("\n🎉 All tests passed! The Streamlit app is ready to run.")
        print("\nTo start the app, run:")
        print("streamlit run ecommerce-practice-data/app.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed:")
        print("pip install streamlit langchain langchain-community langchain-google-genai chromadb sentence-transformers")
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure the vector database exists. Run:")
        print("python ecommerce-practice-data/enhanced_index_documents.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your .env file and Google API key configuration")

if __name__ == "__main__":
    test_app_imports()