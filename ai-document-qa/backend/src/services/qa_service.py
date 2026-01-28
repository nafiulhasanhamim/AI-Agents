"""
QA Service with Router Pattern (Optimized)
Uses a single classification step to route questions to Local Docs or Web Search.
Eliminates agent loops for maximum speed and reliability.
"""
import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.chains import RetrievalQA


class QAService:
    """Optimized Router Service for multi-source question answering"""
    
    def __init__(self, vector_store: Chroma, model_name: str = "llama3.2"):
        """
        Initialize Router with Local and Web capabilities
        """
        print(f"Initializing Optimized Router Agent with model: {model_name}")
        
        # 1. Initialize Local LLM
        self.llm = OllamaLLM(
            model=model_name,
            temperature=0,
            base_url="http://localhost:11434"
        )
        
        self.vector_store = vector_store
        self.web_search_tool = DuckDuckGoSearchRun()
        
        # 2. Local Knowledge Chain
        self.local_qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True
        )

        # 3. Router Prompt
        # A focused prompt that forces the LLM to output a single word classification
        router_template = """Given the user's question and conversation history, classify the intent into exactly one of these categories:
- LOCAL: For questions about company policies, internal projects, business documents, employee handbooks, or specific internal data.
- WEB: For questions about current events, world news, stock prices, public companies, weather, or general knowledge external to this organization.
- GENERAL: For simple greetings (hi, hello) or questions that don't need data (jokes, philosophical questions).

Chat History:
{chat_history}

Question: {question}

Classification (LOCAL, WEB, or GENERAL):"""
        
        self.ROUTER_PROMPT = PromptTemplate.from_template(router_template)

        # 4. Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    def _route_question(self, question: str) -> str:
        """Decide which tool to use"""
        # Get history string
        history = self.memory.load_memory_variables({})['chat_history']
        
        # format prompt
        prompt = self.ROUTER_PROMPT.format(chat_history=history, question=question)
        
        # Generate classification
        # We use a lower temperature for routing to be deterministic
        response = self.llm.invoke(prompt).strip().upper()
        
        # Simple heuristic cleanup
        if "LOCAL" in response: return "LOCAL"
        if "WEB" in response: return "WEB"
        return "GENERAL"

    def answer_question(self, question: str) -> dict:
        """
        Main execution flow with Router optimization
        """
        route = self._route_question(question)
        print(f"⚡ Router Decision: [{route}]")
        
        sources = []
        final_answer = ""
        
        try:
            if route == "LOCAL":
                # Execute Local Search
                print("  -> Searching Local Documents...")
                result = self.local_qa_chain.invoke({"query": question})
                final_answer = result["result"]
                sources = result["source_documents"]
                
            elif route == "WEB":
                # Execute Web Search
                print("  -> Searching the Internet...")
                # We do a direct search + synthesis
                search_results = self.web_search_tool.run(question)
                
                # Synthesize answer
                synthesis_prompt = f"""Based on the following web search results, answer the user's question.
                
Question: {question}

Web Results:
{search_results}

Answer (concise and helpful):"""
                final_answer = self.llm.invoke(synthesis_prompt)
                
            else:
                # General Chat
                print("  -> General Conversation...")
                final_answer = self.llm.invoke(question)

            # Update Memory manually since we aren't using a Chain anymore
            self.memory.chat_memory.add_user_message(question)
            self.memory.chat_memory.add_ai_message(final_answer)
            
            return {
                "answer": final_answer,
                "sources": sources,
                "chat_history": self.memory.load_memory_variables({})['chat_history']
            }
            
        except Exception as e:
            print(f"✗ Error in QA execution: {str(e)}")
            return {
                "answer": f"I encountered an error while processing your request: {str(e)}",
                "sources": [],
                "chat_history": []
            } # Fallback
    
    def reset_memory(self):
        """Clear history"""
        self.memory.clear()
        print("✓ Agent memory reset.")
