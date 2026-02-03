import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from assistant import get_assistant

def test_queries():
    print("Initializing Assistant for Verification...")
    rag_chain = get_assistant()
    
    if not rag_chain:
        print("Failed to initialize assistant.")
        return

    queries = [
        "What is the price of the Titan Edge Gaming Laptop?",
        "What is the return policy for earbuds?",
        "Suggest a good camera for street photography under $1000."
    ]

    print("\n--- Starting Automatic Verification ---\n")

    for q in queries:
        print(f"Query: {q}")
        try:
            response = rag_chain.invoke(q)
            print(f"Answer: {response}")
            print("-" * 50)
        except Exception as e:
            print(f"Error processing query '{q}': {e}")

    print("\nVerification Complete.")

if __name__ == "__main__":
    test_queries()
