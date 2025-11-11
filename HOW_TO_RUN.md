# How to Run the RAG Chatbot

This guide provides step-by-step instructions to get the RAG Chatbot up and running.

---

## Prerequisites

Before you begin, ensure you have:
- **Python 3.8 or higher** installed
- **Git** (already available since you cloned the repo)
- **API Key** from either:
  - [Anthropic](https://console.anthropic.com/) (for Claude) - Recommended
  - [OpenAI](https://platform.openai.com/) (for GPT)

---

## Step 1: Navigate to the Project Directory

```bash
cd /home/user/chatbot
```

---

## Step 2: Run the Setup Script

The setup script will:
- Create a virtual environment
- Install all required packages
- Download NLTK data
- Create necessary directories

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup
./setup.sh
```

**Expected output:**
```
======================================
RAG Chatbot Setup
======================================
Creating virtual environment...
Installing requirements...
Downloading NLTK data...
Setup Complete!
```

This will take 2-3 minutes depending on your internet speed.

---

## Step 3: Activate the Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt.

---

## Step 4: Configure Your API Key

### Option A: Using Anthropic Claude (Recommended)

1. **Get your API key** from https://console.anthropic.com/

2. **Create/Edit the .env file:**
   ```bash
   nano .env
   ```

3. **Add your API key:**
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

   # Leave these as default for best results
   EMBEDDING_PROVIDER=sentence-transformers
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   LLM_PROVIDER=anthropic
   LLM_MODEL=claude-3-sonnet-20240229
   ```

4. **Save and exit** (Ctrl+X, then Y, then Enter)

### Option B: Using OpenAI GPT

1. **Get your API key** from https://platform.openai.com/

2. **Create/Edit the .env file:**
   ```bash
   nano .env
   ```

3. **Add your API key:**
   ```env
   OPENAI_API_KEY=sk-your-key-here

   # Use OpenAI for LLM
   EMBEDDING_PROVIDER=sentence-transformers
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-3.5-turbo
   ```

4. **Save and exit**

> **Note:** Embeddings use SentenceTransformers (free, local) so you only need an API key for the LLM provider.

---

## Step 5: Ingest Documents

The repository already contains two PDF documents. Let's ingest them:

### Ingest Both Documents at Once

```bash
python main.py --ingest .
```

**Expected output:**
```
Initializing RAG Chatbot...
Ingesting from: .

✓ Ingestion Complete:
  • TheUdyog Brochure.pdf: 45 chunks
  • TheUdyog Presentation.pdf: 32 chunks

Total: 77 chunks from 2 documents
```

### Or Ingest One at a Time

```bash
python main.py --ingest "TheUdyog Brochure.pdf"
python main.py --ingest "TheUdyog Presentation.pdf"
```

### Ingest Your Own Documents

Place your documents in the project directory and run:

```bash
# For a specific file
python main.py --ingest "your_document.pdf"

# For all files in a directory
python main.py --ingest /path/to/your/documents
```

**Supported formats:** PDF, TXT, CSV, HTML, Markdown

---

## Step 6: Start Using the Chatbot

### Method 1: Interactive Chat Mode (Recommended)

```bash
python main.py --chat
```

**Example conversation:**
```
============================================================
RAG Chatbot - Interactive Mode
============================================================
Ask questions about your documents!
Commands: 'quit' to exit, 'clear' to clear history, 'sources' to see last sources
============================================================

You: What is TheUdyog?