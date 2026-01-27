"""
QA Service with Conversational Memory
Allows multi-turn dialogue using free local Ollama LLM
"""
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_classic.memory import ConversationBufferMemory


class QAService:
    """Service for conversational question answering using local LLM"""
    
    def __init__(self, vector_store: Chroma, model_name: str = "llama3.2"):
        """
        Initialize QA service with conversational memory
        
        Args:
            vector_store: ChromaDB vector store instance
            model_name: Ollama model name
        """
        print(f"Initializing Conversational QA with model: {model_name}")
        
        # Local LLM
        self.llm = Ollama(
            model=model_name,
            temperature=0
        )
        
        self.vector_store = vector_store
        
        # 1. Memory Configuration
        # We use memory_key="chat_history" to match the chain's expectations
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # 2. Rephrase Prompt (Condense Question)
        # This prompt takes the chat history and the new user question and
        # creates a single, standalone question that is searchable in the vector DB.
        condense_template = """Given the following conversation and a follow up question, 
rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
        
        CONDENSE_PROMPT = PromptTemplate.from_template(condense_template)
        
        # 3. QA Prompt (Answer Generation)
        # This prompt takes the retrieved context and answers the standalone question.
        qa_template = """You are a helpful AI assistant answering questions about business documents.

Use ONLY the following context to answer the question. If the answer is not in the context, say "I don't have enough information in the provided documents to answer that question."

Context:
{context}

Question: {question}

Answer (be concise and accurate):"""
        
        QA_PROMPT = PromptTemplate.from_template(qa_template)
        
        # 4. Construct the Conversational Retrieval Chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            memory=self.memory,
            condense_question_prompt=CONDENSE_PROMPT,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT},
            return_source_documents=True,
            verbose=True # Helpful for debugging rephrased queries
        )

    def answer_question(self, question: str) -> dict:
        """
        Handle conversational question answering
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with 'answer', 'sources', and 'chat_history'
        """
        # The chain handles memory updates automatically
        result = self.qa_chain({"question": question})
        
        return {
            "answer": result["answer"],
            "sources": result["source_documents"],
            "chat_history": result["chat_history"]
        }
    
    def reset_memory(self):
        """Clear the conversation history"""
        self.memory.clear()
        print("✓ Conversation history cleared.")
