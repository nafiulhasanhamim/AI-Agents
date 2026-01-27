"""
Document Loader Service
Loads documents from various formats (PDF, DOCX, TXT)
"""
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.documents import Document


class DocumentLoader:
    """Service for loading documents from various file formats"""
    
    def __init__(self, documents_path: str = "./documents/raw"):
        self.documents_path = documents_path
        
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a single document based on file extension
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext == '.docx':
            loader = Docx2txtLoader(file_path)
        elif ext == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file type: {ext}")
            
        return loader.load()
    
    def load_all_documents(self) -> List[Document]:
        """
        Load all documents from the documents directory
        
        Returns:
            List of all loaded Document objects
        """
        documents = []
        
        if not os.path.exists(self.documents_path):
            raise FileNotFoundError(f"Documents path not found: {self.documents_path}")
        
        for filename in os.listdir(self.documents_path):
            file_path = os.path.join(self.documents_path, filename)
            
            if os.path.isfile(file_path):
                try:
                    docs = self.load_document(file_path)
                    documents.extend(docs)
                    print(f"✓ Loaded: {filename} ({len(docs)} pages/sections)")
                except Exception as e:
                    print(f"✗ Failed to load {filename}: {str(e)}")
        
        return documents
