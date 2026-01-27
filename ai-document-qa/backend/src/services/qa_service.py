"""
QA Service with Digital Skills (Agents) - Modernized & Stabilized
Uses LangChain Agents to decide between Local Docs and Web Search.
Optimized for local LLMs like Llama 3.2.
"""
import os
from langchain_classic.agents import initialize_agent, AgentType
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.chains import RetrievalQA


class QAService:
    """Agentic Service for multi-source question answering"""
    
    def __init__(self, vector_store: Chroma, model_name: str = "llama3.2"):
        """
        Initialize Agent with Local and Web tools
        """
        print(f"Initializing Intelligent Agent with model: {model_name}")
        
        # 1. Initialize Local LLM using the modern OllamaLLM class
        self.llm = OllamaLLM(
            model=model_name,
            temperature=0,
            base_url="http://localhost:11434"
        )
        
        self.vector_store = vector_store
        
        # 2. Create the Local Knowledge Retrieval Chain
        self.local_qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True
        )

        # 3. Define the Tools
        # We give the LocalDocs tool a very strong priority description
        self.tools = [
            Tool(
                name="LocalDocs",
                func=self._local_search,
                description="ALWAYS USE THIS FIRST. Use this for ANY info about the company, policies, projects, or business documents."
            ),
            Tool(
                name="InternetSearch",
                func=DuckDuckGoSearchRun().run,
                description="Use this ONLY as a second choice if you cannot find the answer in LocalDocs."
            )
        ]

        # 4. Initialize Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )

        # 5. Initialize the Agent
        # ZERO_SHOT_REACT_DESCRIPTION is much more stable for small local models 
        # than the conversational JSON-based agents.
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            return_intermediate_steps=False # Faster processing
        )
        
        # Internal state for sources
        self.last_sources = []

    def _local_search(self, query: str) -> str:
        """Explicitly handles local document retrieval"""
        if not query or query.strip() == "":
            return "Please provide a specific search term for the local documents."
            
        print(f"  [Tool: LocalDocs] Searching for: {query}")
        result = self.local_qa_chain.invoke({"query": query})
        self.last_sources = result["source_documents"]
        return result["result"]

    def answer_question(self, question: str) -> dict:
        """
        Execute the agent loop with stability fixes
        """
        self.last_sources = []
        
        try:
            # We add a strong hint to the question to help the local model prioritize correctly
            enriched_input = f"{question} (IMPORTANT: Check LocalDocs first if relevant)"
            
            result = self.agent_executor.invoke({"input": enriched_input})
            
            return {
                "answer": result["output"],
                "sources": self.last_sources,
                "chat_history": result["chat_history"]
            }
        except Exception as e:
            print(f"Agent Error: {str(e)}")
            # Fallback to local search if agent fails
            fallback = self._local_search(question)
            return {
                "answer": fallback,
                "sources": self.last_sources,
                "chat_history": []
            }
    
    def reset_memory(self):
        """Clear history"""
        self.memory.clear()
        self.last_sources = []
        print("✓ Agent memory reset.")
