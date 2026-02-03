"""
QA Service with Router Pattern - Multi-Model Support & Resilience
Features:
1. Multi-Model: Ollama, Google Gemini, OpenAI
2. Advanced Router: LOCAL vs WEB vs GENERAL
3. Hybrid Fallback: Automatically uses Local Ollama if Cloud limits are hit.
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
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

class QAService:
    """Optimized Router Service with multi-model support and Hybrid Fallback"""
    
    def __init__(self, vector_store: Chroma, model_name: str = None):
        """
        Initialize Router with Primary and Backup LLMs
        """
        self.primary_provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
        self.backup_provider = os.getenv("BACKUP_PROVIDER", "ollama").lower()
        
        print(f"🤖 Initializing AI Agent (Primary: {self.primary_provider.upper()}, Backup: {self.backup_provider.upper()})")
        
        # 1. Initialize Both LLMs
        self.primary_llm = self._initialize_llm(self.primary_provider, model_name)
        self.backup_llm = None
        
        # Only init backup if primary isn't already the backup
        if self.primary_provider != self.backup_provider:
            self.backup_llm = self._initialize_llm(self.backup_provider)
            
        self.active_llm = self.primary_llm
        self.vector_store = vector_store
        self.web_search_tool = DuckDuckGoSearchRun()
        
        # 3. Feature Toggles
        self.enable_web_search = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
        print(f"   └─ Web Search Enabled: {self.enable_web_search}")

        # 4. Create Retrieval Chains for both (to avoid re-init in mid-flight)
        self.primary_qa_chain = self._create_qa_chain(self.primary_llm)
        self.backup_qa_chain = self._create_qa_chain(self.backup_llm) if self.backup_llm else None

        # 5. Router Prompt
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

    def _create_qa_chain(self, llm: BaseLLM):
        """Helper to create a retrieval chain for a specific LLM"""
        if not llm: return None
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True
        )

    def _initialize_llm(self, provider: str, model_override: str = None) -> BaseLLM:
        """Factory method to initialize the correct LLM based on provider"""
        try:
            if provider == "ollama":
                from langchain_ollama import OllamaLLM
                model = model_override or os.getenv("OLLAMA_MODEL", "llama3.2")
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                return OllamaLLM(model=model, temperature=0, base_url=base_url)
            
            elif provider == "google":
                from langchain_google_genai import ChatGoogleGenerativeAI
                model = model_override or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
                api_key = os.getenv("GOOGLE_API_KEY")
                return ChatGoogleGenerativeAI(model=model, temperature=0, google_api_key=api_key)
            
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                model = model_override or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                api_key = os.getenv("OPENAI_API_KEY")
                return ChatOpenAI(model=model, temperature=0, api_key=api_key)
            
            return None
        except Exception as e:
            print(f"⚠️ Failed to init {provider}: {e}")
            return None

    def _safe_invoke(self, llm: BaseLLM, prompt_or_input: any, is_chain: bool = False) -> any:
        """Invokes primary LLM with automatic fallback to local Ollama on failure"""
        try:
            if is_chain:
                # prompt_or_input is dict {"query": ...}
                return llm.invoke(prompt_or_input)
            else:
                # prompt_or_input is string prompt
                return llm.invoke(prompt_or_input)
        except Exception as e:
            err_msg = str(e).lower()
            if ("429" in err_msg or "quota" in err_msg or "exhausted" in err_msg) and self.backup_llm:
                print(f"⚠️ Primary LLM ({self.primary_provider}) Limit Hit! Falling back to {self.backup_provider.upper()}...")
                
                # Switch to backup
                target_llm = self.backup_qa_chain if is_chain else self.backup_llm
                
                # We add a note to the answer later if it was a fallback
                result = target_llm.invoke(prompt_or_input)
                
                # If it's a direct LLM call and returned a message object, inject the warning
                if not is_chain and hasattr(result, 'content'):
                    result.content = f"(Fallback to local mode) {result.content}"
                elif not is_chain:
                    result = f"(Fallback to local mode) {result}"
                
                return result
            raise e

    def _route_question(self, question: str) -> str:
        """Decide which tool to use"""
        history = self.memory.load_memory_variables({})['chat_history']
        prompt = self.ROUTER_PROMPT.format(chat_history=history, question=question)
        
        # Use safe invoke for routing
        response = self._safe_invoke(self.primary_llm, prompt)
        
        # Extract text from response
        if hasattr(response, 'content'):
            response = response.content
        
        response = str(response).strip().upper()
        
        if "LOCAL" in response: return "LOCAL"
        if "WEB" in response and self.enable_web_search: return "WEB"
        return "GENERAL"

    def answer_question(self, question: str) -> dict:
        """Main execution flow with Resilience"""
        route = self._route_question(question)
        print(f"⚡ Router Decision: [{route}]")
        
        sources = []
        final_answer = ""
        is_fallback = False
        
        try:
            if route == "LOCAL":
                print("  → Searching Local Documents...")
                try:
                    result = self._safe_invoke(self.primary_qa_chain, {"query": question}, is_chain=True)
                except Exception:
                    # Specific secondary fallback check
                    result = self.backup_qa_chain.invoke({"query": question})
                    is_fallback = True
                
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
                
                try:
                    answer_obj = self._safe_invoke(self.primary_llm, synthesis_prompt)
                except Exception:
                    answer_obj = self.backup_llm.invoke(synthesis_prompt)
                    is_fallback = True
                    
                final_answer = answer_obj.content if hasattr(answer_obj, 'content') else str(answer_obj)
                
            else:
                print("  → General Conversation...")
                try:
                    answer_obj = self._safe_invoke(self.primary_llm, question)
                except Exception:
                    answer_obj = self.backup_llm.invoke(question)
                    is_fallback = True
                    
                final_answer = answer_obj.content if hasattr(answer_obj, 'content') else str(answer_obj)

            if is_fallback:
                final_answer = f"⚠️ [Cloud Limit Hit - Local Mode Active] {final_answer}"

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
                "answer": f"I encountered a persistent error: {str(e)}. Please check your model status.",
                "sources": [],
                "chat_history": []
            } # Final safety net
    
    def reset_memory(self):
        """Clear history"""
        self.memory.clear()
        print("✓ Agent memory reset.")
