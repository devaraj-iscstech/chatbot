# Google AI (Gemini) Setup Guide

## ✅ Configuration Complete!

Your RAG Chatbot is now configured to use **Google AI's Gemini** model instead of OpenAI or Anthropic.

---

## What Was Done

1. ✅ Created `.env` file with your Google AI API key
2. ✅ Set `LLM_PROVIDER=google` to use Gemini
3. ✅ Set `LLM_MODEL=gemini-pro` (Google's latest model)
4. ✅ Added Google AI support to the codebase
5. ✅ Updated requirements.txt with `google-generativeai`

---

## Your Current Configuration

Your `.env` file is configured as:

```env
# Google AI API Key
GOOGLE_API_KEY=AIzaSyDfvPtYohZRPRXj9KDdNvTVuJaMkSOhZCI

# Using Google AI for LLM
LLM_PROVIDER=google
LLM_MODEL=gemini-pro

# Using free local embeddings (no API key needed)
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## How to Run

### Step 1: Install Dependencies

```bash
cd /home/user/chatbot

# Install the Google AI library
pip install google-generativeai

# Or install all requirements
pip install -r requirements.txt
```

### Step 2: Ingest Documents

```bash
# Ingest the PDF documents
python main.py --ingest "TheUdyog Brochure.pdf"
python main.py --ingest "TheUdyog Presentation.pdf"

# Or ingest all at once
python main.py --ingest .
```

**Expected output:**
```
Initializing RAG Chatbot...
Initialized Google AI provider with model: gemini-pro
Ingesting document: TheUdyog Brochure.pdf
✓ Created 45 chunks
```

### Step 3: Start Chatting

```bash
python main.py --chat
```

**Example conversation:**
```
============================================================
RAG Chatbot - Interactive Mode
============================================================

You: What is TheUdyog?