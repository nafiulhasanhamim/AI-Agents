"""
QA Service with Router Pattern - Multi-Model Support
Supports Ollama (local), Google Gemini, and OpenAI via environment config.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.llms import BaseLLM
from langchain_chroma import Chroma
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.chains import RetrievalQA

# Load environment variables from project root
# Navigate up from backend/src/services/ to project root
# We need to resolve() the path first to normalize any .. in __file__
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

class QAService:
    """Optimized Router Service with multi-model support"""
    
    def __init__(self, vector_store: Chroma, model_name: str = None):
        """
        Initialize Router with configurable LLM provider
        
        Args:
            vector_store: ChromaDB instance
            model_name: Optional override for model (uses .env if not provided)
        """
        # Determine which model provider to use
        provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
        
        print(f"🤖 Initializing AI Agent with provider: {provider.upper()}")
        
        # Initialize the appropriate LLM based on provider
        self.llm = self._initialize_llm(provider, model_name)
        
        self.vector_store = vector_store
        self.web_search_tool = DuckDuckGoSearchRun()
        
        # 3. Feature Toggles
        self.enable_web_search = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
        print(f"   └─ Web Search Enabled: {self.enable_web_search}")

        # 4. Local Knowledge Chain
        self.local_qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True
        )

        # 5. Router Prompt
        # We adjust the prompt based on whether web search is enabled
        router_options = "- LOCAL: For questions about company policies, internal projects, business documents, employee handbooks, or specific internal data.\n"
        if self.enable_web_search:
            router_options += "- WEB: For questions about current events, world news, stock prices, public companies, weather, or general knowledge external to this organization.\n"
        router_options += "- GENERAL: For simple greetings (hi, hello) or questions that don't need data (jokes, philosophical questions)."

        classification_hint = "(LOCAL, WEB, or GENERAL)" if self.enable_web_search else "(LOCAL or GENERAL)"

        router_template = f"""Given the user's question and conversation history, classify the intent into exactly one of these categories:
{router_options}

Chat History:
{{chat_history}}

Question: {{question}}

Classification {classification_hint}:"""
        
        self.ROUTER_PROMPT = PromptTemplate.from_template(router_template)

        # 6. Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    def _initialize_llm(self, provider: str, model_override: str = None) -> BaseLLM:
        """Factory method to initialize the correct LLM based on provider"""
        
        if provider == "ollama":
            from langchain_ollama import OllamaLLM
            model = model_override or os.getenv("OLLAMA_MODEL", "llama3.2")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            print(f"   └─ Using Ollama: {model} @ {base_url}")
            return OllamaLLM(
                model=model,
                temperature=0,
                base_url=base_url
            )
        
        elif provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            model = model_override or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in .env file!")
            print(f"   └─ Using Google Gemini: {model}")
            return ChatGoogleGenerativeAI(
                model=model,
                temperature=0,
                google_api_key=api_key
            )
        
        elif provider == "openai":
            from langchain_openai import ChatOpenAI
            model = model_override or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in .env file!")
            print(f"   └─ Using OpenAI: {model}")
            return ChatOpenAI(
                model=model,
                temperature=0,
                api_key=api_key
            )
        
        else:
            raise ValueError(f"Unknown MODEL_PROVIDER: {provider}. Use 'ollama', 'google', or 'openai'")

    def _route_question(self, question: str) -> str:
        """Decide which tool to use"""
        history = self.memory.load_memory_variables({})['chat_history']
        prompt = self.ROUTER_PROMPT.format(chat_history=history, question=question)
        
        # Generate classification
        response = self.llm.invoke(prompt)
        
        # Extract text from response (handles both string and message objects)
        if hasattr(response, 'content'):
            response = response.content
        
        response = str(response).strip().upper()
        
        # Simple heuristic cleanup
        if "LOCAL" in response: return "LOCAL"
        if "WEB" in response and self.enable_web_search: return "WEB"
        return "GENERAL"

    def answer_question(self, question: str) -> dict:
        """Main execution flow with Router optimization"""
        route = self._route_question(question)
        print(f"⚡ Router Decision: [{route}]")
        
        sources = []
        final_answer = ""
        
        try:
            if route == "LOCAL":
                print("  → Searching Local Documents...")
                result = self.local_qa_chain.invoke({"query": question})
                final_answer = result["result"]
                sources = result["source_documents"]
                
            elif route == "WEB" and self.enable_web_search:
                print("  → Searching the Internet...")
                search_results = self.web_search_tool.run(question)
                
                synthesis_prompt = f"""Based on the following web search results, answer the user's question.
                
Question: {question}

Web Results:
{search_results}

Answer (concise and helpful):"""
                
                answer_obj = self.llm.invoke(synthesis_prompt)
                final_answer = answer_obj.content if hasattr(answer_obj, 'content') else str(answer_obj)
                
            else:
                print("  → General Conversation...")
                answer_obj = self.llm.invoke(question)
                final_answer = answer_obj.content if hasattr(answer_obj, 'content') else str(answer_obj)

            # Update Memory
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
                "answer": f"I encountered an error: {str(e)}",
                "sources": [],
                "chat_history": []
            }
    
    def reset_memory(self):
        """Clear history"""
        self.memory.clear()
        print("✓ Agent memory reset.")
