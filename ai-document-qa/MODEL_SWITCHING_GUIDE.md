# 🔄 Quick Model Switching Guide

This guide explains how to easily switch between different AI models in your project.

## 📝 How to Switch Models

### **Step 1: Open your `.env` file**
Location: `C:\Projects\AI Agent\ai-document-qa\.env`

### **Step 2: Change the `MODEL_PROVIDER` variable**

```bash
# For Local Ollama (Free, Private)
MODEL_PROVIDER=ollama

# For Google Gemini (Free Tier, Cloud)
MODEL_PROVIDER=google

# For OpenAI (Paid, Cloud)
MODEL_PROVIDER=openai
```

### **Step 3: Restart your backend**
```powershell
# Stop the current server (Ctrl+C)
# Then restart:
uvicorn src.api.main:app --reload
```

---

## 🎯 Provider Comparison

| Provider | Speed | Intelligence | Privacy | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Ollama** | Medium | Good | ✅ Private | Free |
| **Google Gemini** | ⚡ Very Fast | Excellent | ⚠️ Cloud | Free Tier |
| **OpenAI** | Fast | Excellent | ⚠️ Cloud | Paid |

---

## ⚙️ Model Options for Each Provider

### Ollama (Local)
```bash
OLLAMA_MODEL=llama3.2      # Small, fast
OLLAMA_MODEL=llama3.1       # Larger, smarter
OLLAMA_MODEL=mistral        # Great for reasoning
```

### Google Gemini (Cloud)
```bash
GOOGLE_MODEL=gemini-1.5-flash      # 🔥 Recommended: Fast & Free
GOOGLE_MODEL=gemini-1.5-pro        # More capable
GOOGLE_MODEL=gemini-1.5-flash-8b   # Extremely fast
```

### OpenAI (Cloud)
```bash
OPENAI_MODEL=gpt-4o-mini    # 💰 Cheapest GPT-4 quality
OPENAI_MODEL=gpt-4o         # Most capable
```

---

## 💡 Recommended Setup

**For maximum speed + Free:** Set `MODEL_PROVIDER=google` and use `gemini-1.5-flash`

**For privacy:** Keep `MODEL_PROVIDER=ollama` with `llama3.2`
