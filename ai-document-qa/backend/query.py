"""
Query Script
Interactive question answering using indexed documents
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.vector_store import VectorStoreManager
from services.qa_service import QAService


def main():
    """Main query interface"""
    print("=" * 60)
    print("AI Document Q&A - Query Interface")
    print("=" * 60)
    print()
    
    # Check if vector store exists
    if not os.path.exists("../chroma_db"):
        print("⚠ Vector database not found!")
        print("Please run 'python index_documents.py' first to index your documents.")
        return
    
    # Initialize services
    print("Initializing QA system...")
    print("(This may take a moment on first run)")
    print()
    
    try:
        # Load vector store
        vector_store_manager = VectorStoreManager(
            persist_directory="../chroma_db",
            model_name="all-MiniLM-L6-v2"
        )
        vector_store = vector_store_manager.get_vector_store()
        
        # Initialize QA service
        qa_service = QAService(
            vector_store=vector_store,
            model_name="llama3.2"  # Change to "mistral" or "phi3" if you prefer
        )
        
        print("✓ QA system ready!")
        print()
        print("=" * 60)
        print("Ask questions about your documents (type 'exit' to quit)")
        print("=" * 60)
        print()
        
        # Interactive loop
        while True:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            if not question:
                continue
            
            print("\n🤖 Thinking...")
            try:
                result = qa_service.answer_question(question)
                
                print("\n" + "=" * 60)
                print("📝 Answer:")
                print("=" * 60)
                print(result["answer"])
                print()
                
                print("📚 Sources:")
                for i, doc in enumerate(result["sources"], 1):
                    source = doc.metadata.get('source', 'Unknown')
                    page = doc.metadata.get('page', 'N/A')
                    print(f"  {i}. {os.path.basename(source)} (page {page})")
                print("=" * 60)
                
            except Exception as e:
                print(f"\n✗ Error: {str(e)}")
                print("\nTroubleshooting:")
                print("  - Make sure Ollama is running: 'ollama serve'")
                print("  - Check if model is installed: 'ollama pull llama3.2'")
    
    except Exception as e:
        print(f"✗ Error initializing QA system: {str(e)}")
        print("\nMake sure you have:")
        print("  1. Indexed documents: 'python index_documents.py'")
        print("  2. Ollama installed and running")
        print("  3. A model pulled: 'ollama pull llama3.2'")


if __name__ == "__main__":
    main()
