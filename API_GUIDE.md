# RAG Chatbot FastAPI Guide

## Overview

The RAG Chatbot now includes a **FastAPI** backend that provides REST API endpoints for easy integration and testing.

---

## Quick Start

### 1. Install FastAPI Dependencies

```bash
pip install fastapi uvicorn python-multipart
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# Method 1: Direct Python
python api.py

# Method 2: Using uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

### 3. Test the API

**Option A: Use the Web Interface**
```bash
# Open in your browser
open test_api.html
# or
python -m http.server 8080
# Then open http://localhost:8080/test_api.html
```

**Option B: Use the Python Test Script**
```bash
python test_api.py
```

**Option C: Use Interactive API Docs**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

### 1. Health Check

**GET** `/` or `/health`

Check if the API is running and get configuration.

**Response:**
```json
{
  "status": "healthy",
  "llm_provider": "google",
  "llm_model": "gemini-pro",
  "embedding_provider": "sentence-transformers"
}
```

**cURL Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Query Chatbot

**POST** `/query`

Ask a question to the chatbot.

**Request Body:**
```json
{
  "question": "What is TheUdyog?",
  "use_memory": false,
  "return_sources": true
}
```

**Response:**
```json
{
  "question": "What is TheUdyog?",
  "answer": "TheUdyog is...",
  "sources": [
    {
      "text": "...",
      "score": 0.85,
      "metadata": {...}
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is TheUdyog?",
    "use_memory": false,
    "return_sources": true
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "What is TheUdyog?",
        "return_sources": True
    }
)

data = response.json()
print(data['answer'])
```

---

### 3. Ingest Document from Path

**POST** `/ingest/path`

Ingest a document from a file path on the server.

**Request Body:**
```json
{
  "file_path": "./TheUdyog Brochure.pdf"
}
```

**Response:**
```json
{
  "filename": "TheUdyog Brochure.pdf",
  "chunks_created": 45,
  "status": "success"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/ingest/path \
  -H "Content-Type: application/json" \
  -d '{"file_path": "./TheUdyog Brochure.pdf"}'
```

---

### 4. Upload and Ingest Document

**POST** `/ingest/upload`

Upload a document file to the server and ingest it.

**Request:**
- Content-Type: `multipart/form-data`
- Field name: `file`
- Supported formats: PDF, TXT, CSV, HTML, MD

**Response:**
```json
{
  "filename": "document.pdf",
  "chunks_created": 32,
  "status": "success"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/ingest/upload \
  -F "file=@./document.pdf"
```

**Python Example:**
```python
import requests

with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/ingest/upload",
        files=files
    )

print(response.json())
```

---

### 5. Get System Statistics

**GET** `/stats`

Get chatbot system statistics.

**Response:**
```json
{
  "collection_name": "rag_documents",
  "total_documents": 77,
  "embedding_dimension": 384,
  "conversation_history_length": 0
}
```

**cURL Example:**
```bash
curl http://localhost:8000/stats
```

---

### 6. List Indexed Documents

**GET** `/documents`

List all indexed documents with chunk counts.

**Response:**
```json
{
  "documents": [
    {
      "filename": "TheUdyog Brochure.pdf",
      "chunk_count": 45
    },
    {
      "filename": "TheUdyog Presentation.pdf",
      "chunk_count": 32
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:8000/documents
```

---

### 7. Get Configuration

**GET** `/config`

Get current chatbot configuration.

**Response:**
```json
{
  "llm_provider": "google",
  "llm_model": "gemini-pro",
  "embedding_provider": "sentence-transformers",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "top_k_retrieval": 10,
  "top_k_rerank": 5,
  "reranker_type": "bm25",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**cURL Example:**
```bash
curl http://localhost:8000/config
```

---

### 8. Clear Conversation Memory

**POST** `/memory/clear`

Clear the conversation history.

**Response:**
```json
{
  "status": "success",
  "message": "Conversation memory cleared"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/memory/clear
```

---

### 9. Get Conversation History

**GET** `/memory/history`

Get the current conversation history.

**Response:**
```json
{
  "history": [
    {
      "role": "user",
      "content": "What is TheUdyog?"
    },
    {
      "role": "assistant",
      "content": "TheUdyog is..."
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:8000/memory/history
```

---

## Testing Methods

### Method 1: Interactive Web Interface (Recommended)

1. **Start the API server:**
   ```bash
   python api.py
   ```

2. **Open the test interface:**
   ```bash
   # Serve the HTML file
   python -m http.server 8080
   ```

3. **Open in browser:**
   http://localhost:8080/test_api.html

**Features:**
- ✅ Beautiful UI
- ✅ Test all endpoints
- ✅ Upload files
- ✅ See responses in real-time
- ✅ Connection status indicator

---

### Method 2: Python Test Script

```bash
python test_api.py
```

This will:
- ✅ Test all endpoints
- ✅ Ingest documents
- ✅ Run queries
- ✅ Display results
- ✅ Show summary

---

### Method 3: Interactive API Documentation

FastAPI provides automatic interactive documentation:

**Swagger UI:**
http://localhost:8000/docs

**ReDoc:**
http://localhost:8000/redoc

Features:
- Try endpoints directly
- See request/response schemas
- Auto-generated documentation

---

### Method 4: Command Line (cURL)

```bash
# Health check
curl http://localhost:8000/health

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is TheUdyog?", "return_sources": true}'

# Ingest
curl -X POST http://localhost:8000/ingest/path \
  -H "Content-Type: application/json" \
  -d '{"file_path": "./TheUdyog Brochure.pdf"}'

# Stats
curl http://localhost:8000/stats
```

---

## Complete Testing Workflow

### Step 1: Start the API

```bash
cd /home/user/chatbot
python api.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Initializing RAG Chatbot...
INFO:     ✅ RAG Chatbot initialized successfully!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 2: Ingest Documents

**Using cURL:**
```bash
curl -X POST http://localhost:8000/ingest/path \
  -H "Content-Type: application/json" \
  -d '{"file_path": "./TheUdyog Brochure.pdf"}'

curl -X POST http://localhost:8000/ingest/path \
  -H "Content-Type: application/json" \
  -d '{"file_path": "./TheUdyog Presentation.pdf"}'
```

**Or using Python:**
```python
import requests

files = [
    "./TheUdyog Brochure.pdf",
    "./TheUdyog Presentation.pdf"
]

for file in files:
    response = requests.post(
        "http://localhost:8000/ingest/path",
        json={"file_path": file}
    )
    print(response.json())
```

---

### Step 3: Query the Chatbot

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is TheUdyog?",
    "return_sources": true
  }'
```

---

### Step 4: Check Statistics

```bash
curl http://localhost:8000/stats
```

---

## Integration Examples

### JavaScript/TypeScript

```javascript
// Query the chatbot
async function queryChatbot(question) {
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
  return data;
}

// Use it
queryChatbot("What is TheUdyog?")
  .then(data => console.log(data.answer));
```

---

### Python

```python
import requests

class RAGChatbotClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def query(self, question, use_memory=False, return_sources=True):
        response = requests.post(
            f"{self.base_url}/query",
            json={
                "question": question,
                "use_memory": use_memory,
                "return_sources": return_sources
            }
        )
        return response.json()

    def ingest(self, file_path):
        response = requests.post(
            f"{self.base_url}/ingest/path",
            json={"file_path": file_path}
        )
        return response.json()

    def get_stats(self):
        response = requests.get(f"{self.base_url}/stats")
        return response.json()

# Usage
client = RAGChatbotClient()
result = client.query("What is TheUdyog?")
print(result['answer'])
```

---

## Troubleshooting

### API Server Won't Start

**Error:** `ImportError: No module named 'fastapi'`
```bash
pip install fastapi uvicorn python-multipart
```

**Error:** `ModuleNotFoundError: No module named 'rag_chatbot'`
```bash
# Make sure you're in the chatbot directory
cd /home/user/chatbot
python api.py
```

---

### Connection Refused

**Make sure the server is running:**
```bash
python api.py
```

**Check if port 8000 is available:**
```bash
lsof -i :8000
```

**Use a different port:**
```bash
uvicorn api:app --port 8001
```

---

### CORS Errors

The API has CORS enabled for all origins. If you still face issues:

1. Check browser console
2. Make sure API URL is correct
3. Try from a different browser

---

### Google AI API Key Issues

**Error:** `GOOGLE_API_KEY environment variable not set`

**Solution:**
```bash
# Check .env file exists
cat .env

# Should contain:
GOOGLE_API_KEY=AIzaSyDfvPtYohZRPRXj9KDdNvTVuJaMkSOhZCI
```

---

## Production Deployment

### Using Gunicorn (Production)

```bash
pip install gunicorn

gunicorn api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## API Features

✅ **Google AI (Gemini) Integration**
✅ **Document Upload & Ingestion**
✅ **Semantic Search & Retrieval**
✅ **Source Attribution**
✅ **Conversation Memory**
✅ **CORS Enabled**
✅ **Auto-generated Documentation**
✅ **Error Handling**
✅ **Type Validation (Pydantic)**
✅ **Async Support**

---

## Summary

The FastAPI backend provides a complete REST API for your RAG Chatbot:

- **9 API endpoints** for all operations
- **3 testing methods** (Web UI, Python script, cURL)
- **Auto-generated documentation** (Swagger/ReDoc)
- **Easy integration** with any frontend
- **Production-ready** with proper error handling

**Start testing now:**
```bash
python api.py
# Then open http://localhost:8000/docs
```

🎉 **Your RAG Chatbot is now accessible via API!**
