"""
QA Service
Question answering service using free local Ollama LLM
"""
from langchain_classic.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma


class QAService:
    """Service for question answering using local LLM"""
    
    def __init__(self, vector_store: Chroma, model_name: str = "llama3.2"):
        """
        Initialize QA service with free local Ollama LLM
        
        Args:
            vector_store: ChromaDB vector store instance
            model_name: Ollama model name (llama3.2, mistral, phi3)
        """
        # Free local LLM (no API costs!)
        print(f"Initializing Ollama with model: {model_name}")
        self.llm = Ollama(
            model=model_name,
            temperature=0
        )
        
        self.vector_store = vector_store
        
        # Custom prompt template optimized for local LLMs
        self.prompt_template = """You are a helpful AI assistant answering questions about business documents.

Use ONLY the following context to answer the question. If the answer is not in the context, say "I don't have enough information in the provided documents to answer that question."

Context:
{context}

Question: {question}

Answer (be concise and accurate):"""
        
        self.PROMPT = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
    
    def answer_question(self, question: str) -> dict:
        """
        Generate answer for a question using free local LLM
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with 'answer' and 'sources'
        """
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": self.PROMPT},
            return_source_documents=True
        )
        
        result = qa_chain({"query": question})
        
        return {
            "answer": result["result"],
            "sources": result["source_documents"]
        }
