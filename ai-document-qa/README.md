# AI Document Q&A Agent

A free, local AI agent that answers questions about your business documents using Retrieval-Augmented Generation (RAG).

## Features
- 🆓 100% Free - No API keys or subscriptions needed
- 🔒 Private - Everything runs locally on your machine
- 📄 Multi-format - Supports PDF, DOCX, and TXT files
- 🤖 Powered by Ollama - Local LLM (Llama 3.2, Mistral, Phi-3)
- 🚀 Fast - ChromaDB vector storage with sentence-transformers embeddings

## Quick Start

### 1. Install Ollama
Download and install from [https://ollama.ai](https://ollama.ai)

Pull a model:
```bash
ollama pull llama3.2
```

### 2. Set Up Python Environment
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Add Your Documents
Place your PDF, DOCX, or TXT files in `documents/raw/`

### 4. Index Documents
1. Navigate to the `backend` folder and activate the environment:
   ```bash
   cd backend
   .\venv\Scripts\activate
   ```
2. Run the indexing script:
   ```bash
   python index_documents.py
   ```

### 5. Ask Questions (Backend)
- **Interactive Mode**:
  ```bash
  python query.py
  ```
- **API Mode**:
  ```bash
  uvicorn src.api.main:app --reload
  ```

### 6. Run the Frontend (Web Interface)
1. Open a new terminal in the `frontend` folder.
2. Install and run:
   ```bash
   npm install
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

## Project Structure
```
ai-document-qa/
├── backend/
│   ├── src/
│   │   ├── services/     # Core business logic
│   │   ├── api/          # FastAPI endpoints
│   │   └── utils/        # Helper functions
│   ├── tests/            # Unit tests
│   ├── index_documents.py
│   ├── query.py
│   └── requirements.txt
├── documents/
│   ├── raw/              # Place your documents here
│   └── processed/
├── chroma_db/            # Vector database storage
└── .env                  # Configuration
```

## Cost Comparison
| Component | This Project | Cloud Alternative | Savings |
|-----------|--------------|-------------------|---------|
| LLM | $0 (Ollama) | $50-200/mo (OpenAI) | 100% |
| Embeddings | $0 (local) | $10-50/mo | 100% |
| Vector DB | $0 (ChromaDB) | $70/mo (Pinecone) | 100% |
| **Total** | **$0/month** | **$130-320/month** | **100%** |

## Technologies Used
- **FastAPI** - Modern Python web framework
- **Ollama** - Local LLM runtime
- **ChromaDB** - Vector database
- **LangChain** - LLM application framework
- **sentence-transformers** - Text embeddings
