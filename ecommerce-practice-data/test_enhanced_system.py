#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_assistant import EnhancedAssistant

def test_queries():
    """Test the enhanced system with sample queries"""
    
    print("🧪 Testing Enhanced Hybrid Chunking System")
    print("=" * 50)
    
    try:
        assistant = EnhancedAssistant()
        print("✅ Assistant initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")
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
            "query": "Compare smartphone cameras",
            "description": "Category comparison"
        },
        {
            "query": "What's your return policy?",
            "description": "Policy information"
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
            print(f"Response: {response[:200]}...")
            print("✅ Test passed")
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print()

if __name__ == "__main__":
    test_queries()