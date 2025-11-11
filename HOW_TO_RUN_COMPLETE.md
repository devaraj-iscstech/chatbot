# How to Run the RAG Chatbot

Complete step-by-step guide to get the RAG Chatbot running.

---

## Prerequisites

- **Python 3.8+** installed
- **API Key** from [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)

---

## Quick Start (5 Steps)

### Step 1: Setup

```bash
cd /home/user/chatbot
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

### Step 2: Configure API Key

```bash
nano .env
```

Add your API key:
```env
ANTHROPIC_API_KEY=your_key_here
```

Save and exit (Ctrl+X, Y, Enter)

### Step 3: Ingest Documents

```bash
python main.py --ingest "TheUdyog Brochure.pdf"
python main.py --ingest "TheUdyog Presentation.pdf"
```

### Step 4: Start Chatting

```bash
python main.py --chat
```

### Step 5: Ask Questions!

```
You: What is TheUdyog?
Assistant: [AI generates response based on documents]

You: What services do they provide?
Assistant: [AI generates response]

Commands:
- sources - See source documents
- clear - Clear history
- quit - Exit
```

---

## Detailed Instructions

### 1. Installation and Setup

#### A. Navigate to Project
```bash
cd /home/user/chatbot
```

#### B. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies (langchain, chromadb, nltk, etc.)
- Download NLTK data
- Create necessary directories

**Time:** 2-3 minutes

#### C. Activate Virtual Environment
```bash
source venv/bin/activate
```

You'll see `(venv)` in your prompt.

---

### 2. Configuration

#### Get API Key

**Option A: Anthropic Claude** (Recommended)
- Go to https://console.anthropic.com/
- Sign up / Log in
- Create API key
- Copy the key (starts with `sk-ant-`)

**Option B: OpenAI GPT**
- Go to https://platform.openai.com/
- Sign up / Log in  
- Create API key
- Copy the key (starts with `sk-`)

#### Configure .env File

```bash
# Create/edit .env file
nano .env
```

**For Anthropic:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229

CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
RERANKER_TYPE=bm25
```

**For OpenAI:**
```env
OPENAI_API_KEY=sk-your-actual-key-here

EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
RERANKER_TYPE=bm25
```

Save: Ctrl+X, then Y, then Enter

---

### 3. Ingest Documents

#### Ingest Existing PDFs

```bash
# Ingest both at once
python main.py --ingest .

# OR ingest one by one
python main.py --ingest "TheUdyog Brochure.pdf"
python main.py --ingest "TheUdyog Presentation.pdf"
```

**Output:**
```
Initializing RAG Chatbot...
Loading embedding model...
Ingesting document: TheUdyog Brochure.pdf
✓ Created 45 chunks
Ingesting document: TheUdyog Presentation.pdf
✓ Created 32 chunks

Total: 77 chunks indexed
```

#### Ingest Your Own Documents

```bash
# Single file
python main.py --ingest "/path/to/your/document.pdf"

# Entire directory
python main.py --ingest "/path/to/documents/"
```

**Supported formats:**
- PDF (.pdf)
- Text (.txt, .md)
- CSV (.csv)
- HTML (.html, .htm)

---

### 4. Usage Methods

#### Method 1: Interactive Chat (Recommended)

```bash
python main.py --chat
```

**Features:**
- Multi-turn conversations
- Context awareness
- See sources
- Clear history

**Commands:**
- Type your question naturally
- `sources` - View source documents for last answer
- `clear` - Clear conversation history
- `quit` or `exit` - Exit chat

**Example Session:**
```
You: What is TheUdyog?
