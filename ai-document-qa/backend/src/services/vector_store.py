"""
Vector Store Manager
Manages ChromaDB vector database with free local embeddings
"""
import os
from typing import List
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


class VectorStoreManager:
    """Service for managing vector database operations"""
    
    def __init__(
        self, 
        persist_directory: str = "./chroma_db",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store with free local embeddings
        
        Args:
            persist_directory: Directory to persist the vector database
            model_name: Name of the embedding model to use
                       Options: all-MiniLM-L6-v2 (fast), all-mpnet-base-v2 (quality)
        """
        self.persist_directory = persist_directory
        
        # Free local embeddings (no API key needed!)
        print(f"Loading embedding model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # Use 'cuda' if you have GPU
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
    
    def add_documents(self, chunks: List[Document]) -> Chroma:
        """
        Add document chunks to ChromaDB
        
        Args:
            chunks: List of document chunks to add
            
        Returns:
            Chroma vector store instance
        """
        print(f"Adding {len(chunks)} chunks to vector store...")
        
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="business_docs"
        )
        
        # Persistence is handled automatically in modern langchain-chroma
        print("✓ Documents added automatically to vector store!")
        return vector_store
    
    def get_vector_store(self) -> Chroma:
        """
        Load existing ChromaDB from disk
        
        Returns:
            Chroma vector store instance
        """
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="business_docs"
        )
    
    def delete_collection(self):
        """Delete the entire collection (useful for re-indexing)"""
        try:
            vector_store = self.get_vector_store()
            vector_store.delete_collection()
            print("✓ Collection deleted successfully!")
        except Exception as e:
            print(f"Note: {str(e)}")
