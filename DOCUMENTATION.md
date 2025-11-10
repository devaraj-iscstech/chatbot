# RAG Chatbot Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Components](#components)
7. [API Reference](#api-reference)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The RAG (Retrieval-Augmented Generation) Chatbot is a sophisticated question-answering system that combines document retrieval with large language models to provide accurate, context-aware responses based on your custom documents.

### Key Features

- **Multi-format Document Support**: PDF, TXT, CSV, HTML, Markdown
- **Advanced NLP Preprocessing**: Text normalization, stopword removal, lemmatization
- **Semantic Chunking**: Intelligent text splitting that preserves context
- **Flexible Embedding Options**: SentenceTransformers (local) or OpenAI embeddings
- **Vector Storage**: ChromaDB for efficient similarity search
- **Smart Retrieval**: BM25 or Cross-Encoder re-ranking
- **Multiple LLM Providers**: OpenAI, Anthropic Claude, or local models
- **Conversation Memory**: Multi-turn conversations with context
- **Interactive CLI**: Easy-to-use command-line interface

---

## Architecture

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Document Ingestion                       │
│  1. Load Document (PDF, TXT, CSV, HTML)                     │
│  2. NLP Preprocessing (cleaning, normalization)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Semantic Chunking                         │
│  1. Split text into meaningful chunks                        │
│  2. Add metadata (source, position, etc.)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Embedding Generation                        │
│  1. Convert chunks to vector embeddings                      │
│  2. Store in ChromaDB with metadata                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Query Processing                          │
│  1. User asks a question                                     │
│  2. Generate query embedding                                │
│  3. Similarity search in vector database                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Re-ranking (Optional)                       │
│  1. BM25 or Cross-Encoder re-ranking                        │
│  2. Select top-k most relevant documents                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Response Generation                          │
│  1. Build context from retrieved documents                   │
│  2. Send to LLM with user query                             │
│  3. Generate natural language response                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Quick Setup

1. **Clone or download the repository**

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

4. **Configure API keys** (edit `.env` file):
   ```bash
   nano .env
   ```

### Manual Installation

If you prefer manual installation:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Copy environment template
cp .env.example .env
# Edit .env and add your API keys
```

---

## Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Embedding Settings
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM Settings
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229

# Database
CHROMA_PERSIST_DIRECTORY=./chroma_db
COLLECTION_NAME=rag_documents

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MIN_CHUNK_SIZE=100

# Retrieval
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
RERANKER_TYPE=bm25

# Generation
TEMPERATURE=0.7
MAX_TOKENS=1000
```

### Provider Options

**Embedding Providers:**
- `sentence-transformers`: Free, runs locally, no API key needed
  - Models: `all-MiniLM-L6-v2` (fast), `all-mpnet-base-v2` (high quality)
- `openai`: Requires API key, high quality
  - Models: `text-embedding-3-small`, `text-embedding-3-large`

**LLM Providers:**
- `anthropic`: Claude models (recommended)
  - Models: `claude-3-sonnet-20240229`, `claude-3-opus-20240229`
- `openai`: GPT models
  - Models: `gpt-4`, `gpt-3.5-turbo`
- `local`: Run models locally using transformers

**Reranker Types:**
- `bm25`: Fast, lexical matching
- `cross-encoder`: More accurate, slower
- `none`: No re-ranking

---

## Usage

### Command Line Interface

#### 1. Ingest Documents

**Ingest a single document:**
```bash
python main.py --ingest "TheUdyog Brochure.pdf"
```

**Ingest all documents in a directory:**
```bash
python main.py --ingest ./data
```

#### 2. Interactive Chat

**Start chat after ingesting:**
```bash
python main.py --ingest ./data --chat
```

**Start chat with existing database:**
```bash
python main.py --chat
```

#### 3. Single Query

**Ask a single question:**
```bash
python main.py --query "What is TheUdyog?"
```

**Show source documents:**
```bash
python main.py --query "What services does TheUdyog provide?" --sources
```

#### 4. System Statistics

```bash
python main.py --stats
```

#### 5. Advanced Options

**Use specific providers:**
```bash
python main.py --embedding-provider openai --llm-provider openai --chat
```

**Change reranker:**
```bash
python main.py --reranker cross-encoder --chat
```

**Show configuration:**
```bash
python main.py --show-config
```

**Reset database:**
```bash
python main.py --reset
```

### Interactive Chat Commands

When in chat mode, you can use:
- Type your question normally
- `sources` - Show sources from last answer
- `clear` - Clear conversation history
- `quit` or `exit` - Exit chat

---

## Components

### 1. Document Ingestion (`src/modules/document_ingestion.py`)

Handles loading and preprocessing documents:
- PDF extraction using pdfplumber and PyPDF2
- Text file reading
- CSV to text conversion
- HTML parsing
- NLP preprocessing (normalization, stopword removal, lemmatization)

### 2. Semantic Chunking (`src/modules/semantic_chunking.py`)

Splits documents into meaningful chunks:
- Sentence-aware chunking
- Configurable chunk size and overlap
- Metadata preservation
- Section-based chunking

### 3. Embeddings (`src/modules/embeddings.py`)

Generates vector embeddings:
- SentenceTransformer support (local)
- OpenAI embeddings support
- Batch processing
- Cosine similarity utilities

### 4. Vector Store (`src/modules/vector_store.py`)

ChromaDB integration:
- Persistent storage
- Metadata filtering
- Similarity search
- Document management

### 5. Retrieval (`src/modules/retrieval.py`)

Retrieval and re-ranking:
- Vector similarity search
- BM25 re-ranking
- Cross-encoder re-ranking
- Context building

### 6. LLM Integration (`src/modules/llm_integration.py`)

LLM provider abstraction:
- OpenAI GPT support
- Anthropic Claude support
- Local model support
- Conversation memory

---

## API Reference

### RAGChatbot Class

```python
from src.rag_chatbot import RAGChatbot

# Initialize
chatbot = RAGChatbot(
    embedding_provider="sentence-transformers",
    llm_provider="anthropic",
    reranker_type="bm25"
)

# Ingest document
num_chunks = chatbot.ingest_document("document.pdf")

# Query
result = chatbot.query(
    question="What is this about?",
    return_sources=True
)

# Interactive chat
chatbot.chat()
```

### Key Methods

**`ingest_document(file_path, aggressive_cleaning=False)`**
- Ingest a single document
- Returns: Number of chunks created

**`ingest_directory(directory_path, file_extensions=None)`**
- Ingest all documents from a directory
- Returns: Dictionary of filename -> chunk count

**`query(question, use_memory=False, return_sources=False)`**
- Ask a question
- Returns: Dictionary with answer and optional sources

**`chat(enable_memory=True)`**
- Start interactive chat mode

**`get_stats()`**
- Get system statistics

---

## Examples

### Example 1: Basic Usage

```python
from src.rag_chatbot import RAGChatbot

# Initialize chatbot
chatbot = RAGChatbot()

# Ingest documents
chatbot.ingest_document("TheUdyog Brochure.pdf")
chatbot.ingest_document("TheUdyog Presentation.pdf")

# Ask questions
result = chatbot.query("What is TheUdyog?")
print(result['answer'])
```

### Example 2: Custom Configuration

```python
chatbot = RAGChatbot(
    embedding_provider="openai",
    embedding_model="text-embedding-3-large",
    llm_provider="anthropic",
    llm_model="claude-3-opus-20240229",
    reranker_type="cross-encoder",
    chunk_size=1024,
    chunk_overlap=100
)
```

### Example 3: Batch Processing

```python
# Ingest multiple documents
results = chatbot.ingest_directory("./documents")
for filename, chunks in results.items():
    print(f"{filename}: {chunks} chunks")

# Ask multiple questions
questions = [
    "What services are offered?",
    "Who is the target audience?",
    "What are the pricing options?"
]

for q in questions:
    result = chatbot.query(q, return_sources=True)
    print(f"\nQ: {q}")
    print(f"A: {result['answer']}")
```

### Example 4: With Conversation Memory

```python
# Enable memory for context-aware conversations
result1 = chatbot.query("What is TheUdyog?", use_memory=True)
result2 = chatbot.query("Tell me more about it", use_memory=True)
# The second query uses context from the first
```

---

## Troubleshooting

### Common Issues

**1. API Key Errors**
```
Error: ANTHROPIC_API_KEY environment variable not set
```
Solution: Add your API key to the `.env` file

**2. Import Errors**
```
ModuleNotFoundError: No module named 'chromadb'
```
Solution: Install requirements: `pip install -r requirements.txt`

**3. NLTK Data Missing**
```
LookupError: Resource punkt not found
```
Solution: Download NLTK data:
```python
python -c "import nltk; nltk.download('punkt')"
```

**4. ChromaDB Permission Errors**
```
PermissionError: [Errno 13] Permission denied: './chroma_db'
```
Solution: Check directory permissions or change `CHROMA_PERSIST_DIRECTORY`

**5. Memory Issues with Large Documents**
Solution: Reduce `CHUNK_SIZE` or process documents in smaller batches

### Performance Tips

1. **For faster embeddings**: Use `sentence-transformers/all-MiniLM-L6-v2`
2. **For better quality**: Use `all-mpnet-base-v2` or OpenAI embeddings
3. **For faster retrieval**: Use `bm25` reranker
4. **For better accuracy**: Use `cross-encoder` reranker
5. **For large documents**: Increase `CHUNK_SIZE` to 1024

### Getting Help

If you encounter issues:
1. Check the logs in `logs/` directory
2. Run with `--stats` to check system state
3. Try `--show-config` to verify configuration
4. Check if documents were ingested: `python main.py --stats`

---

## Advanced Features

### Custom System Prompts

```python
from src.modules.llm_integration import ResponseGenerator

generator = ResponseGenerator(provider="anthropic")
response = generator.generate_response(
    query="What is AI?",
    context=context,
    system_prompt="You are an expert in technology. Be very technical."
)
```

### Metadata Filtering

```python
# Search only in specific documents
result = chatbot.retriever.retrieve_and_rank(
    query="What is the pricing?",
    filter_metadata={"filename": "TheUdyog Brochure.pdf"}
)
```

### Batch Embedding Generation

```python
from src.modules.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator(provider="sentence-transformers")
embeddings = generator.generate_embeddings([
    "Text 1",
    "Text 2",
    "Text 3"
])
```

---

## License

This project is provided as-is for educational and commercial use.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- All tests pass
- Documentation is updated

---

**Happy chatting! 🤖**
