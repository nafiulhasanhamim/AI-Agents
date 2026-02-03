import os
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# Configuration
DATA_DIR = "c:/Projects/AI Agent/ecommerce-practice-data"
DB_DIR = "c:/Projects/AI Agent/ecommerce-practice-data/vector_db"

def load_documents():
    print("Loading documents...")
    # Load Markdown files
    md_loader = DirectoryLoader(DATA_DIR, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    md_docs = md_loader.load()
    
    # Load JSON catalog
    # Note: For JSON, we use a simpler approach for this practice - treating the whole massive_catalog.json as one or 
    # breaking it down. For RAG, it's often better to have individual product descriptions.
    # We'll load massive_catalog.json specifically.
    json_path = os.path.join(DATA_DIR, "massive_catalog.json")
    with open(json_path, 'r') as f:
        catalog_data = json.load(f)
    
    from langchain_core.documents import Document
    json_docs = [
        Document(
            page_content=f"Product: {item['name']}. Category: {item['category']}. Price: ${item['price']}. Description: {item['description']} Rating: {item['specs']['rating']} stars.",
            metadata={"source": "massive_catalog.json", "sku": item['id']}
        ) for item in catalog_data
    ]
    
    return md_docs + json_docs

def create_vector_db():
    docs = load_documents()
    print(f"Total documents loaded: {len(docs)}")
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    print(f"Total chunks created: {len(splits)}")
    
    # Use Local Embeddings (HuggingFace) so it works without extra API cost for embeddings
    print("Generating embeddings (using HuggingFace all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create and persist the vector store
    print("Creating Vector DB in Chroma...")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=DB_DIR
    )
    vectorstore.persist()
    print(f"Vector DB created and saved to {DB_DIR}")

if __name__ == "__main__":
    create_vector_db()
