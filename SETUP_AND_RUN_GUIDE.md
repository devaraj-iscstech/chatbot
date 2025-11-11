# RAG Chatbot - Setup and Run Guide

## Table of Contents
1. [Before Setup](#before-setup)
2. [Setup Instructions](#setup-instructions)
3. [After Setup - Running the Application](#after-setup---running-the-application)
4. [Usage Examples](#usage-examples)
5. [Troubleshooting](#troubleshooting)

---

## Before Setup

### Prerequisites

Before you begin, ensure you have:

**Required**:
- **Python 3.12** (Python 3.14 is NOT compatible with ChromaDB)
- **Git** (for cloning the repository)
- **Internet connection** (for downloading packages)

**API Key** (choose one):
- [Google AI](https://aistudio.google.com/app/apikey) - For Gemini models (Recommended)
- [Anthropic](https://console.anthropic.com/) - For Claude models
- [OpenAI](https://platform.openai.com/) - For GPT models

**Note**: Embeddings use SentenceTransformers (free, local), so you only need an API key for the LLM provider.

### System Requirements

- **OS**: Windows, macOS, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for dependencies and models
- **Python Version**: 3.12 (3.11 also works)

---

## Setup Instructions

### Step 1: Navigate to Project Directory

```bash
cd "d:\New folder\chatbot"
```

Or on Linux/Mac:
```bash
cd /path/to/chatbot
```

### Step 2: Check Python Version

**IMPORTANT**: Verify you have Python 3.12 or 3.11 installed:

```bash
python --version
```

Should show: `Python 3.12.x` or `Python 3.11.x`

If you have Python 3.14, you need to install Python 3.12:
- **Windows**: Download from https://www.python.org/downloads/
- **Linux**: `sudo apt install python3.12`
- **Mac**: `brew install python@3.12`

### Step 3: Create Virtual Environment

**Windows**:
```bash
# Create virtual environment with Python 3.12
py -3.12 -m venv venv

# Activate it
venv\Scripts\activate
```

**Linux/Mac**:
```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 4: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

This will take 2-5 minutes. You'll see packages being installed:
- chromadb
- sentence-transformers
- google-generativeai
- nltk
- and many more...

### Step 5: Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('punkt'); nltk.download('stopwords')"
```

### Step 6: Configure API Key

Create or edit the `.env` file:

**Windows**:
```bash
notepad .env
```

**Linux/Mac**:
```bash
nano .env
```

**Add your configuration**:

```env
# ==========================================
# 🔑 API Keys
# ==========================================
# Add YOUR API key here
GOOGLE_API_KEY=your_google_api_key_here
# OR
# OPENAI_API_KEY=your_openai_key_here
# OR
# ANTHROPIC_API_KEY=your_anthropic_key_here

# ==========================================
# 🔍 Embedding Model Settings
# ==========================================
# Use free local embeddings (no API key needed)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ==========================================
# 🤖 LLM Settings
# ==========================================
LLM_PROVIDER=google  # Options: google, openai, anthropic
LLM_MODEL=gemini-2.5-pro  # or gemini-2.5-flash

# ==========================================
# 🔎 Retrieval Settings
# ==========================================
TOP_K_RETRIEVAL=5
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# ==========================================
# 🧩 Re-ranking
# ==========================================
ENABLE_RERANKING=true
TOP_K_RERANK=3
```

**Save and exit**:
- Windows Notepad: File → Save
- Linux/Mac nano: Ctrl+X, then Y, then Enter

### Step 7: Verify Installation

```bash
# Check if everything is installed correctly
python -c "from src.rag_chatbot import RAGChatbot; print('✅ Installation successful!')"
```

If you see "✅ Installation successful!", you're ready to go!

---

## After Setup - Running the Application

### Quick Start (4 Commands)

```bash
# 1. Activate virtual environment (if not already activated)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Ingest documents
python main.py --ingest .

# 3. Start chatting
python main.py --chat

# 4. Ask questions!
# Type your questions in the interactive chat
```

### Detailed Usage

#### 1. Ingest Documents

Before you can ask questions, you need to ingest documents into the system.

**Ingest specific files**:
```bash
python main.py --ingest "TheUdyog Brochure.pdf"
python main.py --ingest "TheUdyog Presentation.pdf"
```

**Ingest all files in current directory**:
```bash
python main.py --ingest .
```

**Ingest all files from a folder**:
```bash
python main.py --ingest /path/to/your/documents
```

**Expected Output**:
```
============================================================
RAG Chatbot - Retrieval-Augmented Generation System
============================================================

Initializing chatbot...
INFO:rag_chatbot:Initializing RAG Chatbot...
INFO:modules.embeddings:Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
INFO:modules.embeddings:Model loaded. Embedding dimension: 384

Ingesting from: .

Successfully ingested 7 chunks from TheUdyog Brochure.pdf
```

**Supported File Formats**:
- PDF (`.pdf`)
- Text files (`.txt`, `.md`)
- CSV (`.csv`)
- HTML (`.html`, `.htm`)

#### 2. Ask Single Questions

**Basic query**:
```bash
python main.py --query "What is TheUdyog?"
```

**With source citations**:
```bash
python main.py --query "What services does TheUdyog provide?" --sources
```

**Expected Output**:
```
============================================================
RAG Chatbot - Retrieval-Augmented Generation System
============================================================

Initializing chatbot...

Question: What is TheUdyog?

Generating answer...

============================================================
Answer:
============================================================
Based on the provided context, TheUdyog is a company that provides
training, placement, and consultancy services. It aims to connect
people with jobs that match their skills and help companies find
the right talent.
```

#### 3. Interactive Chat Mode (Recommended)

Start an interactive conversation:

```bash
python main.py --chat
```

**Example Session**:
```
============================================================
RAG Chatbot - Interactive Mode
============================================================
Ask questions about your documents!
Commands: 'quit' to exit, 'clear' to clear history, 'sources' to see last sources
============================================================

You: What is TheUdyog?