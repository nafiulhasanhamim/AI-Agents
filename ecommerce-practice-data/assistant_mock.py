import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Configuration
DB_DIR = "c:/Projects/AI Agent/ecommerce-practice-data/vector_db"

def get_assistant():
    print("Initializing Mock Assistant (No API Key needed)...")
    
    # 1. Load Embeddings (Local - No API)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 2. Load Vector DB
    if not os.path.exists(DB_DIR):
        print(f"Error: Vector DB not found at {DB_DIR}. Please run index_documents.py first.")
        return None
        
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    
    # 3. Define a "Mock" Chain
    # Instead of sending to Google, we just retrieve the docs and print them.
    
    from operator import itemgetter

    def mock_generate(inputs):
        docs = inputs["context"]
        question = inputs["question"]
        
        # Create a formatted string of the retrieved sources
        sources_text = "\n\n".join([f"- {d.page_content[:200]}..." for d in docs])
        
        return f"""[MOCK AI RESPONSE]
I retrieved {len(docs)} documents relevant to your query: "{question}"

Here are the snippets I found in your Mock Database:
{sources_text}

(Since we are in Mock Mode to save your API quota, I cannot generate a full natural language answer, but this proves your RAG retrieval pipeline is working perfectly! 🚀)"""

    # Mock Rephraser (Since we don't have an LLM to rewrite the question smartly)
    def heuristic_rephrase(inputs):
        question = inputs["input"]
        history = inputs.get("chat_history", [])
        
        # If we have history, append the previous user noun/context to help the search
        if history:
            # Simple trick: Combine last Question + Current Question
            # "Tell me about Titan" + "Price?" => "Tell me about Titan Price?"
            # This helps the vector DB find the right keywords.
            
            # History format is ["Human: ...", "AI: ..."]
            # We look for the last string starting with "Human:"
            last_human_msg = next((m for m in reversed(history) if m.startswith("Human:")), None)
            if last_human_msg:
                # Strip "Human: " prefix and combine
                clean_last = last_human_msg.replace("Human: ", "")
                return f"{clean_last} {question}"
        
        return question

    # Update Chain to usage rephrased query for retrieval
    rag_chain = (
        {
            "context": RunnableLambda(heuristic_rephrase) | retriever, 
            "question": itemgetter("input") 
        }
        | RunnableLambda(mock_generate)
    )
    
    return rag_chain

def chat():
    print("Loading Mock Assistant...")
    assistant = get_assistant()
    if not assistant:
        return

    print("\n--- VibeShop Mock Assistant (Free Mode) ---")
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
            # Pass dictionary with history to match real assistant signature
            response = assistant.invoke({"input": query, "chat_history": chat_history})
            print(f"\nAssistant: {response}\n")
            
            # Simple history update (Mock doesn't really use it, but good for consistency)
            chat_history.append(f"Human: {query}")
            chat_history.append(f"AI: {response}")

        except Exception as e:
            print(f"\nAssistant: Error: {e}\n")

if __name__ == "__main__":
    chat()
