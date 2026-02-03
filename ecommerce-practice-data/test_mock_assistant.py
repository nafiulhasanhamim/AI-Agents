#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_assistant_mock import MockEnhancedAssistant

def test_mock_assistant():
    """Test the mock enhanced assistant with sample queries"""
    
    print("🤖 Testing Mock Enhanced Assistant")
    print("=" * 50)
    
    try:
        assistant = MockEnhancedAssistant()
        print("✅ Mock Assistant initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize mock assistant: {e}")
        return
    
    # Test queries
    test_cases = [
        {
            "query": "Show me gaming laptops under $2000",
            "description": "Price filtering with category"
        },
        {
            "query": "What's the best Titan laptop?",
            "description": "Brand-specific search"
        },
        {
            "query": "Show me products on sale",
            "description": "Sale filtering"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print("-" * 40)
        
        try:
            response = assistant.query(test_case['query'])
            print(f"✅ Response generated successfully!")
            print(f"Preview: {response[:200]}...")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print()
    
    print("🎉 Mock Assistant is working! You can now use:")
    print("1. Command line: python ecommerce-practice-data/enhanced_assistant_mock.py")
    print("2. Streamlit app: streamlit run ecommerce-practice-data/app_mock.py")

if __name__ == "__main__":
    test_mock_assistant()