"""
Document Indexing Script
Loads documents, chunks them, and stores in vector database
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.document_loader import DocumentLoader
from services.text_chunker import TextChunker
from services.vector_store import VectorStoreManager


def main():
    """Main indexing pipeline"""
    print("=" * 60)
    print("AI Document Q&A - Indexing Pipeline")
    print("=" * 60)
    print()
    
    # Initialize services
    print("1. Initializing services...")
    document_loader = DocumentLoader(documents_path="../documents/raw")
    text_chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    vector_store_manager = VectorStoreManager(
        persist_directory="../chroma_db",
        model_name="all-MiniLM-L6-v2"
    )
    print()
    
    # Load documents
    print("2. Loading documents from ../documents/raw/")
    try:
        documents = document_loader.load_all_documents()
        if not documents:
            print("⚠ No documents found in ../documents/raw/")
            print("Please add PDF, DOCX, or TXT files to the documents/raw/ folder")
            return
        print(f"✓ Loaded {len(documents)} document pages/sections")
    except Exception as e:
        print(f"✗ Error loading documents: {str(e)}")
        return
    print()
    
    # Chunk documents
    print("3. Chunking documents...")
    chunks = text_chunker.chunk_documents(documents)
    print(f"✓ Created {len(chunks)} chunks")
    print()
    
    # Create vector store
    print("4. Creating vector embeddings and storing in ChromaDB...")
    print("(First run will download the embedding model ~80MB)")
    try:
        vector_store = vector_store_manager.add_documents(chunks)
        print()
        print("=" * 60)
        print("✓ SUCCESS! Documents indexed and ready for querying")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run 'python query.py' to ask questions")
        print("  2. Or run the API: 'uvicorn src.api.main:app --reload'")
    except Exception as e:
        print(f"✗ Error creating vector store: {str(e)}")
        return


if __name__ == "__main__":
    main()
