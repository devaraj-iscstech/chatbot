# RAG Chatbot - Complete Implementation Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Implementation Details](#implementation-details)
5. [Technologies Used](#technologies-used)
6. [Features](#features)
7. [API Reference](#api-reference)

---

## Overview

The RAG (Retrieval-Augmented Generation) Chatbot is a production-ready question-answering system that combines document retrieval with large language models to provide accurate, context-aware responses based on custom documents.

### What is RAG?

RAG (Retrieval-Augmented Generation) is an AI pattern that:
1. **Retrieves** relevant information from a knowledge base
2. **Augments** the LLM prompt with this context
3. **Generates** accurate, grounded responses

---

## Architecture

### System Overview

```
1. DOCUMENT INGESTION
   ├── Load Documents (PDF, TXT, CSV, HTML, Markdown)
   ├── NLP Preprocessing (normalization, stopwords, lemmatization)
   └── Metadata Extraction

2. SEMANTIC CHUNKING
   ├── Sentence-aware splitting
   ├── Context preservation
   └── Metadata enrichment

3. EMBEDDING GENERATION
   ├── Convert chunks to vectors
   └── Store in vector database

4. VECTOR STORAGE (ChromaDB)
   ├── Persistent storage
   └── Fast similarity search

5. QUERY PROCESSING
   ├── Generate query embedding
   ├── Similarity search
   └── Retrieve top-K documents

6. RE-RANKING
   ├── BM25 (lexical matching)
   └── Cross-Encoder (neural)

7. RESPONSE GENERATION
   ├── Build context from retrieved docs
   └── Generate natural language response
```

### Component Hierarchy

```
RAGChatbot
    ├── DocumentIngestion (PDF, TXT, CSV, HTML processing)
    ├── SemanticChunker (Intelligent text splitting)
    ├── EmbeddingGenerator (SentenceTransformers / OpenAI)
    ├── VectorStoreManager (ChromaDB integration)
    ├── RAGRetriever (Retrieval & re-ranking)
    ├── ResponseGenerator (Multiple LLM providers)
    └── ConversationMemory (Multi-turn context)
```

---

## Components

### 1. Document Ingestion (`src/modules/document_ingestion.py`)

**Purpose**: Load and preprocess documents from various formats.

**Key Features**:
- Multi-format support (PDF, TXT, CSV, HTML, Markdown)
- Robust PDF extraction with PyPDF2 and pdfplumber
- Advanced NLP preprocessing with NLTK
- Metadata extraction

**Preprocessing Pipeline**:
1. Load → Read file based on format
2. Clean → Remove unwanted characters
3. Normalize → Lowercase, Unicode normalization
4. Tokenize → Split into words/sentences
5. Remove Stopwords → Filter common words
6. Lemmatize → Reduce to base form

---

### 2. Semantic Chunking (`src/modules/semantic_chunking.py`)

**Purpose**: Split documents into meaningful chunks preserving semantic context.

**Key Features**:
- Sentence-aware splitting (doesn't break mid-sentence)
- Configurable chunk size and overlap
- Rich metadata preservation
- Multiple chunking strategies

**Metadata Enriched**:
- Document title and filename
- Chunk position in document
- Total chunks count
- Word and character counts
- Source timestamps

---

### 3. Embedding Generation (`src/modules/embeddings.py`)

**Purpose**: Convert text chunks into dense vector representations.

**Provider Options**:

**SentenceTransformers (Local, Free)**:
- all-MiniLM-L6-v2: Fast, 384 dimensions
- all-mpnet-base-v2: High quality, 768 dimensions

**OpenAI (API, Paid)**:
- text-embedding-3-small: 1536 dimensions
- text-embedding-3-large: 3072 dimensions

**Google Gemini (API)**:
- textembedding-gecko: Optimized for Gemini

---

### 4. Vector Storage (`src/modules/vector_store.py`)

**Purpose**: Persistent storage and fast similarity search using ChromaDB.

**Key Features**:
- Persistent local storage
- Fast similarity search (cosine distance)
- Metadata filtering
- Batch operations

---

### 5. Retrieval & Re-ranking (`src/modules/retrieval.py`)

**Purpose**: Retrieve relevant documents and improve accuracy.

**Retrieval Pipeline**:
1. Embed Query → Convert to vector
2. Similarity Search → Find top-K similar chunks
3. Re-rank → Improve results with BM25 or Cross-Encoder
4. Build Context → Combine chunks with metadata

**Re-ranking Options**:
- **BM25**: Fast lexical matching (recommended)
- **Cross-Encoder**: Neural re-ranking (more accurate, slower)
- **None**: No re-ranking

---

### 6. Response Generation (`src/modules/llm_integration.py`)

**Purpose**: Generate natural language responses using LLMs.

**Supported Providers**:

**Google Gemini**:
- gemini-2.5-pro: Latest flagship model
- gemini-2.5-flash: Fast and efficient

**OpenAI**:
- gpt-4: Highest quality
- gpt-3.5-turbo: Fast and cost-effective

**Anthropic**:
- claude-3-opus: Most capable
- claude-3-sonnet: Balanced

**Local Models**:
- Any Hugging Face transformers model
- Run entirely offline

---

## Implementation Details

### Complete Data Flow

```
User Query: "What is TheUdyog?"
     ↓
1. Query Embedding (convert to vector)
     ↓
2. Similarity Search (ChromaDB)
   - Find top-10 most similar chunks
   - Scores: 0.89, 0.85, 0.82, ...
     ↓
3. Re-ranking (BM25)
   - Re-score using lexical matching
   - Select top-5 after re-ranking
     ↓
4. Context Building
   - Combine selected chunks
   - Add metadata (source, position)
     ↓
5. LLM Prompting
   "You are a helpful assistant. Answer based on this context:
   CONTEXT: [Retrieved chunks]
   USER QUESTION: What is TheUdyog?
   ANSWER:"
     ↓
6. Response Generation
   - LLM generates natural language response
     ↓
User sees: "TheUdyog is a company that provides training,
placement, and consultancy services..."
```

---

## Technologies Used

### Core Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| langchain | 0.1.0 | LLM orchestration |
| chromadb | 0.4.22 | Vector database |
| sentence-transformers | 2.2.2 | Local embeddings |
| google-generativeai | 0.8.5 | Google Gemini API |
| nltk | 3.8.1 | NLP preprocessing |
| transformers | 4.36.2 | Model loading |

### Document Processing

- **PyPDF2** - PDF parsing
- **pdfplumber** - Advanced PDF extraction
- **beautifulsoup4** - HTML parsing
- **python-docx** - Word documents
- **pandas** - CSV processing

### Retrieval

- **rank-bm25** - BM25 algorithm
- **numpy** - Vector operations

---

## Features

### Core Features

✅ Multi-Format Document Support (PDF, TXT, CSV, HTML, Markdown)
✅ Advanced NLP Preprocessing
✅ Semantic Chunking
✅ Multiple Embedding Options (SentenceTransformers, OpenAI, Google)
✅ Vector Storage with ChromaDB
✅ Smart Retrieval (Similarity search, BM25, Cross-Encoder)
✅ Multiple LLM Providers (Google Gemini, OpenAI, Anthropic, Local)
✅ Conversation Memory
✅ Interactive CLI
✅ Source Citations
✅ Metadata Filtering
✅ Batch Processing
✅ Configuration Management

---

## API Reference

### RAGChatbot Class

```python
from src.rag_chatbot import RAGChatbot

# Initialize
chatbot = RAGChatbot(
    embedding_provider="sentence-transformers",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    llm_provider="google",
    llm_model="gemini-2.5-pro",
    reranker_type="bm25",
    chunk_size=512,
    chunk_overlap=50
)
```

### Key Methods

**ingest_document(file_path, aggressive_cleaning=False)**
- Ingest a single document
- Returns: Number of chunks created

**ingest_directory(directory_path, file_extensions=None)**
- Ingest all documents from a directory
- Returns: Dictionary of filename → chunk count

**query(question, use_memory=False, return_sources=False)**
- Ask a question
- Returns: Dictionary with answer and optional sources

**chat(enable_memory=True)**
- Start interactive chat mode

**get_stats()**
- Get system statistics

---

## Python API Examples

**Example 1: Basic Usage**
```python
from src.rag_chatbot import RAGChatbot

chatbot = RAGChatbot()
chatbot.ingest_document("document.pdf")
result = chatbot.query("What is this about?")
print(result['answer'])
```

**Example 2: With Sources**
```python
result = chatbot.query("What services?", return_sources=True)
print(f"Answer: {result['answer']}")
for source in result['sources']:
    print(f"Score: {source['score']:.3f}")
    print(f"Text: {source['text'][:100]}...")
```

**Example 3: Conversation Memory**
```python
result1 = chatbot.query("What is TheUdyog?", use_memory=True)
result2 = chatbot.query("Tell me more", use_memory=True)
```

**Example 4: Batch Processing**
```python
results = chatbot.ingest_directory("./documents")
for filename, chunks in results.items():
    print(f"{filename}: {chunks} chunks")
```

---

## Configuration

### Environment Variables (.env)

```env
# API Keys
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Embedding Settings
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM Settings
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-pro

# ChromaDB Settings
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Chunking Settings
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Retrieval Settings
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
RERANKER_TYPE=bm25

# Generation Settings
TEMPERATURE=0.7
MAX_TOKENS=1000
```

---

## Project Structure

```
chatbot/
├── main.py                      # CLI entry point
├── setup.sh                     # Automated setup
├── requirements.txt             # Dependencies
├── .env                        # Configuration
│
├── src/
│   ├── rag_chatbot.py          # Main orchestrator
│   ├── modules/
│   │   ├── document_ingestion.py
│   │   ├── semantic_chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retrieval.py
│   │   └── llm_integration.py
│   └── utils/
│       └── config.py
│
├── chroma_db/                  # Vector database
└── venv/                       # Virtual environment
```

---

## Performance Tips

1. **For Faster Embeddings**: Use `all-MiniLM-L6-v2`
2. **For Better Quality**: Use `all-mpnet-base-v2` or OpenAI
3. **For Faster Retrieval**: Use `bm25` reranker
4. **For Better Accuracy**: Use `cross-encoder` reranker
5. **For Large Documents**: Increase `CHUNK_SIZE` to 1024
6. **For Better Context**: Increase `CHUNK_OVERLAP` to 100

---

**Implementation Complete** ✅
**Version**: 1.0.0
**Last Updated**: January 2025
