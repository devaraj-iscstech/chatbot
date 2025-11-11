# Quick Start with Google AI

## ✅ Setup Complete!

Your chatbot is configured to use **Google AI (Gemini)** with your API key.

---

## Run in 3 Steps

### 1. Install Dependencies

```bash
cd /home/user/chatbot
pip install -r requirements.txt
```

### 2. Ingest Documents

```bash
python main.py --ingest .
```

### 3. Start Chatting

```bash
python main.py --chat
```

---

## Your API Key

✅ Google AI API Key: `AIzaSyDfvPtYohZRPRXj9KDdNvTVuJaMkSOhZCI`

This is already configured in your `.env` file.

---

## Configuration Details

**LLM Provider:** Google AI (Gemini)
**Model:** gemini-pro
**Embeddings:** SentenceTransformers (free, local)

---

## Commands

```bash
# Interactive chat
python main.py --chat

# Single question
python main.py --query "What is TheUdyog?"

# With sources
python main.py --query "What services?" --sources

# Check status
python main.py --stats
```

---

## Troubleshooting

**If you see "google-generativeai not installed":**
```bash
pip install google-generativeai
```

**If you see "GOOGLE_API_KEY not set":**
Check that `.env` file exists and contains:
```env
GOOGLE_API_KEY=AIzaSyDfvPtYohZRPRXj9KDdNvTVuJaMkSOhZCI
LLM_PROVIDER=google
```

**To verify configuration:**
```bash
python main.py --show-config
```

---

## Features

✅ Google AI Gemini model for responses
✅ Free local embeddings (no API cost)
✅ ChromaDB vector storage
✅ Semantic search & retrieval
✅ BM25 re-ranking
✅ Conversation memory
✅ Source attribution

---

**Ready to chat with your documents!** 🚀
