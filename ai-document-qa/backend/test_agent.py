"""
Test script for Level 2: Internet Access
Verifies the agent can switch between Local and Web tools.
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.vector_store import VectorStoreManager
from services.qa_service import QAService


def test_agent():
    print("Initializing Intelligent Agent...")
    try:
        # Load vector store
        vector_store_manager = VectorStoreManager(
            persist_directory="../chroma_db",
            model_name="all-MiniLM-L6-v2"
        )
        vector_store = vector_store_manager.get_vector_store()
        
        # Initialize QA service (Now with Internet Access!)
        qa_service = QAService(
            vector_store=vector_store,
            model_name="llama3.2"
        )
        
        # Test 1: Local Knowledge
        print("\n--- Test 1: Local Knowledge ---")
        question1 = "What are the company's working hours?"
        print(f"Question: {question1}")
        result1 = qa_service.answer_question(question1)
        print(f"Answer: {result1['answer']}")
        print(f"Sources: {[os.path.basename(s.metadata.get('source', '')) for s in result1['sources']]}")
        
        # Test 2: Web Search
        print("\n--- Test 2: Web Search ---")
        question2 = "What is the current price of Bitcoin?"
        print(f"Question: {question2}")
        result2 = qa_service.answer_question(question2)
        print(f"Answer: {result2['answer']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    test_agent()
