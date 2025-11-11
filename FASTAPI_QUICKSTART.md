# FastAPI Quick Start - RAG Chatbot

## ✅ Complete! FastAPI Backend is Ready

Your RAG Chatbot now has a full REST API backend!

---

## Start in 3 Steps

### Step 1: Install FastAPI

```bash
pip install fastapi uvicorn python-multipart
```

### Step 2: Start the API Server

```bash
cd /home/user/chatbot
python api.py
```

**You'll see:**
```
INFO:     Started server process
INFO:     Initializing RAG Chatbot...
INFO:     Initialized Google AI provider with model: gemini-pro
INFO:     ✅ RAG Chatbot initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test the API

**Option A: Web Interface (Easiest)**
```bash
# Open test_api.html in your browser
open test_api.html
```

**Option B: Interactive Docs**
```bash
# Open in browser:
http://localhost:8000/docs
```

**Option C: Python Script**
```bash
python test_api.py
```

---

## Quick Test Examples

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "llm_provider": "google",
  "llm_model": "gemini-pro",
  "embedding_provider": "sentence-transformers"
}
```

### Test 2: Ingest Documents

```bash
curl -X POST http://localhost:8000/ingest/path \
  -H "Content-Type: application/json" \
  -d '{"file_path": "./TheUdyog Brochure.pdf"}'
```

**Response:**
```json
{
  "filename": "TheUdyog Brochure.pdf",
  "chunks_created": 45,
  "status": "success"
}
```

### Test 3: Ask a Question

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is TheUdyog?",
    "return_sources": true
  }'
```

**Response:**
```json
{
  "question": "What is TheUdyog?",
  "answer": "TheUdyog is...",
  "sources": [...]
}
```

### Test 4: Get Statistics

```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "collection_name": "rag_documents",
  "total_documents": 45,
  "embedding_dimension": 384,
  "conversation_history_length": 0
}
```

---

## Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/query` | Ask questions |
| POST | `/ingest/path` | Ingest from path |
| POST | `/ingest/upload` | Upload & ingest file |
| GET | `/stats` | System statistics |
| GET | `/documents` | List documents |
| GET | `/config` | Show configuration |
| POST | `/memory/clear` | Clear history |
| GET | `/memory/history` | Get history |

---

## Testing Methods

### 1. Web Interface (Best for Manual Testing)

**Features:**
- 🎨 Beautiful UI
- 📤 Upload files
- 💬 Chat interface
- 📊 View stats
- 🔍 See sources

**How to use:**
1. Start API: `python api.py`
2. Open: `test_api.html` in browser
3. Test all features!

---

### 2. Interactive API Docs (Swagger)

**URL:** http://localhost:8000/docs

**Features:**
- 📖 Auto-generated docs
- ▶️ Try endpoints directly
- 📋 Request/response schemas
- 🔍 Explore all endpoints

---

### 3. Python Test Script

```bash
python test_api.py
```

**What it does:**
- ✅ Tests all endpoints
- ✅ Ingests documents
- ✅ Runs queries
- ✅ Shows summary

---

### 4. Command Line (cURL)

Quick tests from terminal:

```bash
# Health
curl http://localhost:8000/health

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is TheUdyog?"}'

# Stats
curl http://localhost:8000/stats
```

---

## Python Client Example

```python
import requests

# Connect to API
API_URL = "http://localhost:8000"

# 1. Ingest a document
response = requests.post(
    f"{API_URL}/ingest/path",
    json={"file_path": "./TheUdyog Brochure.pdf"}
)
print(response.json())

# 2. Ask a question
response = requests.post(
    f"{API_URL}/query",
    json={
        "question": "What is TheUdyog?",
        "return_sources": True
    }
)
data = response.json()
print(f"Answer: {data['answer']}")

# 3. Get stats
response = requests.get(f"{API_URL}/stats")
print(response.json())
```

---

## JavaScript/Frontend Example

```javascript
// Query the chatbot
async function askQuestion(question) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: question,
      return_sources: true
    })
  });

  const data = await response.json();
  console.log(data.answer);
  return data;
}

// Use it
askQuestion("What is TheUdyog?")
  .then(result => {
    console.log("Answer:", result.answer);
    console.log("Sources:", result.sources);
  });
```

---

## Troubleshooting

### API Won't Start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install fastapi uvicorn python-multipart
```

### Can't Connect to API

**Problem:** Connection refused

**Solution:**
```bash
# Make sure API is running
python api.py

# Check the URL
http://localhost:8000/health
```

### CORS Errors in Browser

**Already fixed!** The API has CORS enabled for all origins.

---

## What's Included

### API Features
✅ 9 REST endpoints
✅ Google AI (Gemini) integration
✅ Document upload & ingestion
✅ Semantic search & retrieval
✅ Source attribution
✅ Conversation memory
✅ Error handling
✅ Type validation (Pydantic)
✅ CORS support

### Testing Tools
✅ Web interface (`test_api.html`)
✅ Python test script (`test_api.py`)
✅ Auto-generated docs (Swagger/ReDoc)
✅ cURL examples

### Documentation
✅ Complete API guide (`API_GUIDE.md`)
✅ This quick start
✅ Code examples

---

## Next Steps

1. **Start the API:**
   ```bash
   python api.py
   ```

2. **Test with web interface:**
   Open `test_api.html`

3. **Explore the docs:**
   http://localhost:8000/docs

4. **Integrate with your app:**
   Use the API endpoints in your frontend

---

## Full Workflow Example

```bash
# Terminal 1: Start API
python api.py

# Terminal 2: Test
# Ingest documents
curl -X POST http://localhost:8000/ingest/path \
  -H "Content-Type: application/json" \
  -d '{"file_path": "./TheUdyog Brochure.pdf"}'

# Ask questions
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is TheUdyog?", "return_sources": true}'

# Check stats
curl http://localhost:8000/stats
```

---

## Summary

Your RAG Chatbot is now a **full-featured API server**:

- 🚀 **Easy to use** - Start with one command
- 🔌 **Easy to integrate** - REST API for any frontend
- 📚 **Well documented** - Auto-generated docs
- 🧪 **Easy to test** - Multiple testing tools
- 🔒 **Production ready** - Error handling & validation

**Start now:**
```bash
python api.py
# Then open http://localhost:8000/docs
```

🎉 **Your RAG Chatbot API is ready to use!**
