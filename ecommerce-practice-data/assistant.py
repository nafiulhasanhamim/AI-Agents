import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# Configuration
DB_DIR = "c:/Projects/AI Agent/ecommerce-practice-data/vector_db"

def get_assistant():
    # 1. Load Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 2. Load Vector DB
    if not os.path.exists(DB_DIR):
        print(f"Error: Vector DB not found at {DB_DIR}. Please run index_documents.py first.")
        return None
        
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    # 3. Setup LLM
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in environment.")
        return None
        
    # Try using the Experimental model (often has separate quota)
    llm = ChatGoogleGenerativeAI(model="gemini-exp-1206", temperature=0)
    
    # 4. Define the RAG Chain using LCEL
    from langchain_core.runnables import RunnableBranch
    from operator import itemgetter
    
    # A. Chain to rephrase question if history exists
    condense_q_system = """Given a chat history and the latest user question 
    which might reference context in the chat history, formulate a standalone question 
    which can be understood without the chat history. Do NOT answer the question, 
    just reformulate it if needed and otherwise return it as is."""
    
    condense_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", condense_q_system),
            ("human", "Chat History:\n{chat_history}\n\nQuestion: {input}"),
        ]
    )
    
    condense_q_chain = condense_q_prompt | llm | StrOutputParser()

    # B. The Main Retrieval Chain
    # We use a branch: If history exists, rephrase first. If not, pass input directly.
    def parse_retriever_input(params):
        if params.get("chat_history"):
            return condense_q_chain
        return itemgetter("input")

    # This chain will return the Documents
    retrieval_chain = RunnableBranch(
        (lambda x: bool(x.get("chat_history")), condense_q_chain | retriever),
        (lambda x: not x.get("chat_history"), itemgetter("input") | retriever),
        itemgetter("input") | retriever # Fallback
    )

    # C. The Answer Chain
    qa_system = """You are a helpful E-commerce Assistant for 'VibeShop'. 
    Use the following pieces of retrieved context to answer the user's question. 
    If you don't know the answer, just say that you don't know. 
    Always be polite and professional.
    
    Context:
    {context}"""
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system),
            ("human", "{input}"),
        ]
    )
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # D. Putting it all together
    # Input: {"input": "...", "chat_history": []}
    rag_chain = (
        {
            "context": retrieval_chain | format_docs, 
            "input": (lambda x: condense_q_chain.invoke(x) if x.get("chat_history") else x["input"])
        }
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def chat():
    print("Loading assistant...")
    assistant = get_assistant()
    if not assistant:
        return

    print("\n--- VibeShop AI Assistant Ready ---")
    print("(Type 'exit' to quit)\n")
    
    chat_history = []
    
    while True:
        query = input("You: ")
        if not query.strip():
            continue
            
        if query.lower() in ["exit", "quit", "bye"]:
            print("Assistant: Goodbye! Have a great day.")
            break
            
        try:
            # For LCEL chains, we use .invoke()
            response = assistant.invoke({"input": query, "chat_history": chat_history})
            print(f"\nAssistant: {response}\n")
            
            # Update History (Keep reasonable size, e.g., last 3 turns)
            chat_history.append(f"Human: {query}")
            chat_history.append(f"AI: {response}")
            if len(chat_history) > 6:
                chat_history = chat_history[-6:]

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"\nAssistant: ⚠️ Rate limit hit (Free Tier). Please wait a moment before trying again.\n")
            else:
                print(f"\nAssistant: I encountered an error: {e}\n")

if __name__ == "__main__":
    chat()
