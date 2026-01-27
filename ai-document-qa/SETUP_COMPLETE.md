# AI Document Q&A - Setup Instructions

## ✅ What's Been Set Up

Your AI Document Q&A agent is now ready! Here's what has been created:

### Project Structure
```
C:\Projects\AI Agent\ai-document-qa\
├── backend/
│   ├── src/
│   │   ├── services/
│   │   │   ├── document_loader.py    ✓ Created
│   │   │   ├── text_chunker.py       ✓ Created
│   │   │   ├── vector_store.py       ✓ Created
│   │   │   └── qa_service.py         ✓ Created
│   │   └── api/
│   │       └── main.py               ✓ Created
│   ├── index_documents.py            ✓ Created
│   ├── query.py                      ✓ Created
│   ├── requirements.txt              ✓ Created
│   └── venv/                         ✓ Created & Activated
├── documents/
│   └── raw/
│       └── sample_company_info.txt   ✓ Sample document added
├── chroma_db/                        (Will be created on first index)
├── .env                              ✓ Created
├── .gitignore                        ✓ Created
└── README.md                         ✓ Created
```

### Dependencies Installed ✓
- FastAPI & Uvicorn
- LangChain & LangChain Community
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- Ollama (LLM client)
- PyPDF2, python-docx (document loaders)

---

## 🚀 Next Steps - Getting Started

### Step 1: Install Ollama (Required)

Ollama is not installed yet. You need to install it to run the LLM locally.

**Download and Install:**
1. Visit: https://ollama.ai
2. Download the Windows installer
3. Run the installer
4. Verify installation by opening a new terminal and running:
   ```powershell
   ollama --version
   ```

**Pull a Model:**
```powershell
ollama pull llama3.2
```
(This will download ~2GB, one-time only)

**Alternative models:**
```powershell
ollama pull mistral    # Better reasoning, larger (4GB)
ollama pull phi3       # Microsoft's efficient model (2.3GB)
```

---

### Step 2: Test the Setup

Once Ollama is installed, you can test everything:

**Option A: Interactive Query Mode**
```powershell
cd C:\Projects\AI Agent\ai-document-qa\backend
.\venv\Scripts\activate
python index_documents.py    # Index the sample document first
python query.py              # Start asking questions
```

**Option B: Run the API**
```powershell
cd C:\Projects\AI Agent\ai-document-qa\backend
.\venv\Scripts\activate
python index_documents.py    # Index documents first
uvicorn src.api.main:app --reload
```

Then test with:
```powershell
# In another terminal
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d "{\"question\":\"What are the company's working hours?\"}"
```

---

### Step 3: Add Your Own Documents

1. Place your PDF, DOCX, or TXT files in:
   ```
   C:\Projects\AI Agent\ai-document-qa\documents\raw\
   ```

2. Re-index the documents:
   ```powershell
   cd C:\Projects\AI Agent\ai-document-qa\backend
   .\venv\Scripts\activate
   python index_documents.py
   ```

3. Start querying:
   ```powershell
   python query.py
   ```

---

## 📝 Example Questions to Try

With the sample document, you can ask:
- "What are the company's working hours?"
- "How many days of annual leave do employees get?"
- "What services does TechVision offer?"
- "Tell me about the Global Bank project"
- "What is the professional development budget?"

---

## 🔧 Troubleshooting

### Issue: "Ollama not found"
**Solution:** Install Ollama from https://ollama.ai and restart your terminal

### Issue: "Model not found"
**Solution:** Run `ollama pull llama3.2`

### Issue: "No documents found"
**Solution:** Add documents to `documents/raw/` folder

### Issue: "Vector database not found"
**Solution:** Run `python index_documents.py` first

---

## 💰 Cost Reminder

Everything is 100% FREE:
- ✅ No API keys needed
- ✅ No subscriptions
- ✅ Runs completely locally
- ✅ Your data stays private
- ✅ $0/month forever

---

## 📚 What You Can Do Next

1. **Install Ollama** (required to run)
2. **Test with sample document** (already included)
3. **Add your business documents**
4. **Build a web frontend** (React + this API)
5. **Deploy locally or on free tier services**

---

## 🎯 Quick Command Reference

```powershell
# Activate virtual environment
cd C:\Projects\AI Agent\ai-document-qa\backend
.\venv\Scripts\activate

# Index documents
python index_documents.py

# Interactive queries
python query.py

# Run API server
uvicorn src.api.main:app --reload

# Test API
curl http://localhost:8000/health
```

---

**Your AI Document Q&A agent is ready! Just install Ollama and you're good to go! 🎉**
