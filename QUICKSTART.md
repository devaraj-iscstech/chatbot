# Quick Start Guide - RAG Chatbot

Get up and running in 5 minutes! ⚡

## Prerequisites

- Python 3.8 or higher
- pip
- An API key from either:
  - Anthropic (for Claude) - Get it at https://console.anthropic.com/
  - OpenAI (for GPT) - Get it at https://platform.openai.com/

> **Note**: You can use SentenceTransformers for embeddings (free, no API key needed) and only need an API key for the LLM provider.

---

## Step 1: Setup (2 minutes)

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

---

## Step 2: Configure API Key (1 minute)

Edit the `.env` file and add your API key:

```bash
nano .env
```

Add one of these:
```env
ANTHROPIC_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here
```

Save and exit (Ctrl+X, then Y, then Enter in nano).

---

## Step 3: Ingest Your Documents (1 minute)

The repository already has two PDF documents. Let's ingest them:

```bash
python main.py --ingest "TheUdyog Brochure.pdf"
python main.py --ingest "TheUdyog Presentation.pdf"
```

Or ingest both at once:
```bash
python main.py --ingest .
```

You should see:
```
✓ Ingested 45 chunks from TheUdyog Brochure.pdf
✓ Ingested 32 chunks from TheUdyog Presentation.pdf
```

---

## Step 4: Start Chatting! (1 minute)

### Option A: Interactive Chat

```bash
python main.py --chat
```

Try asking:
- "What is TheUdyog?"
- "What services do they provide?"
- "Tell me about their features"

Commands in chat:
- `sources` - See source documents for last answer
- `clear` - Clear conversation history
- `quit` - Exit

### Option B: Single Question

```bash
python main.py --query "What is TheUdyog?"
```

### Option C: With Sources

```bash
python main.py --query "What services are offered?" --sources
```

---

## Common Commands Cheatsheet

```bash
# Ingest documents
python main.py --ingest "document.pdf"
python main.py --ingest ./folder

# Ask questions
python main.py --query "your question"
python main.py --query "your question" --sources

# Interactive chat
python main.py --chat

# Check system status
python main.py --stats

# Show configuration
python main.py --show-config

# Help
python main.py --help
```

---

## Troubleshooting

### "No module named X"
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

### "API key not found"
```bash
# Check your .env file exists and has the correct key
cat .env
```

### "No relevant information found"
```bash
# Check if documents are ingested
python main.py --stats
# If total_documents is 0, ingest them
python main.py --ingest .
```

### "NLTK data not found"
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

---

## What's Next?

1. **Read full documentation**: See [DOCUMENTATION.md](DOCUMENTATION.md)
2. **Try examples**: Run `python examples/example_usage.py`
3. **Add your documents**: Place PDFs in `data/` folder and ingest
4. **Customize settings**: Edit `.env` file for different models and settings

---

## Configuration Tips

### For Best Quality:
```env
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-large
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
RERANKER_TYPE=cross-encoder
```

### For Free/Local (no API costs):
```env
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
# Still need API key for LLM, but embeddings are free
LLM_PROVIDER=anthropic
```

### For Speed:
```env
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
RERANKER_TYPE=bm25
CHUNK_SIZE=1024
```

---

## Example Session

```bash
$ python main.py --chat

============================================================
RAG Chatbot - Interactive Mode
============================================================
Ask questions about your documents!

You: What is TheUdyog?