"""
FastAPI Application
REST API for AI Document Q&A
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.vector_store import VectorStoreManager
from services.qa_service import QAService


app = FastAPI(
    title="AI Document Q&A API",
    description="Free local AI agent for answering questions about business documents",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global QA service
qa_service = None


class QuestionRequest(BaseModel):
    """Request model for questions"""
    question: str


class AnswerResponse(BaseModel):
    """Response model for answers"""
    answer: str
    sources: list


@app.on_event("startup")
async def startup_event():
    """Initialize QA system on startup"""
    global qa_service
    
    print("Initializing AI Document Q&A system...")
    
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
            model_name="llama3.2"
        )
        
        print("✓ QA system initialized successfully!")
        
    except Exception as e:
        print(f"✗ Error initializing QA system: {str(e)}")
        print("Make sure you have:")
        print("  1. Indexed documents: 'python index_documents.py'")
        print("  2. Ollama installed and running")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Document Q&A API",
        "status": "running",
        "cost": "$0.00/month",
        "endpoints": {
            "health": "/health",
            "ask": "/ask (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "qa_service_ready": qa_service is not None,
        "cost": "$0.00"
    }


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer a question based on indexed documents
    
    Args:
        request: Question request with 'question' field
        
    Returns:
        Answer and source documents
    """
    if not qa_service:
        raise HTTPException(
            status_code=503,
            detail="QA service not initialized. Please check server logs."
        )
    
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        result = qa_service.answer_question(request.question)
        
        # Format sources
        sources = [
            {
                "source": os.path.basename(doc.metadata.get('source', 'Unknown')),
                "page": doc.metadata.get('page', 'N/A'),
                "content_preview": doc.page_content[:200] + "..."
            }
            for doc in result["sources"]
        ]
        
        return AnswerResponse(
            answer=result["answer"],
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
