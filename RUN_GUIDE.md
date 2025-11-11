# RAG Chatbot - How to Run

## ✅ Implementation Status: COMPLETE

Yes, the RAG Chatbot is **fully implemented** with all requested features!

---

## Quick Start (4 Commands)

```bash
# 1. Setup
./setup.sh && source venv/bin/activate

# 2. Configure (add your API key)
nano .env  # Add ANTHROPIC_API_KEY or OPENAI_API_KEY

# 3. Ingest documents
python main.py --ingest .

# 4. Start chatting
python main.py --chat
```

---

## Detailed Step-by-Step Guide

### Step 1: Setup Environment (2-3 minutes)

```bash
cd /home/user/chatbot

# Make setup script executable
chmod +x setup.sh

# Run setup (installs everything)
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

**What setup does:**
- Creates Python virtual environment
- Installs all packages (langchain, chromadb, transformers, etc.)
- Downloads NLTK data
- Creates necessary directories

---

### Step 2: Add API Key (1 minute)

**Get an API key:**
- **Anthropic (Claude)**: https://console.anthropic.com/ - Recommended
- **OpenAI (GPT)**: https://platform.openai.com/

**Configure:**
```bash
nano .env
```

**Add this (replace with your key):**
```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Or for OpenAI:
```env
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
```

**Save**: Ctrl+X, then Y, then Enter

> **Note:** Embeddings are FREE (using SentenceTransformers locally). You only need an API key for the LLM.

---

### Step 3: Ingest Documents (1 minute)

```bash
# Ingest both PDFs in the repo
python main.py --ingest .
```

Or one at a time:
```bash
python main.py --ingest "TheUdyog Brochure.pdf"
python main.py --ingest "TheUdyog Presentation.pdf"
```

**Expected output:**
```
Initializing RAG Chatbot...
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Model loaded. Embedding dimension: 384

Ingesting from: .
✓ Ingested 45 chunks from TheUdyog Brochure.pdf
✓ Ingested 32 chunks from TheUdyog Presentation.pdf

Total: 77 chunks from 2 documents
```

---

### Step 4: Start Using

#### Option A: Interactive Chat (Recommended)

```bash
python main.py --chat
```

**Example conversation:**
```
============================================================
RAG Chatbot - Interactive Mode
============================================================

You: What is TheUdyog?