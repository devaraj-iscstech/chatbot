# RAG Chatbot 🤖

A powerful **Retrieval-Augmented Generation (RAG) Chatbot** that answers user queries based on custom documents using advanced NLP, semantic chunking, embeddings, and vector similarity search.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Features

- **📄 Multi-Format Support**: PDF, TXT, CSV, HTML, Markdown
- **🧠 Advanced NLP**: Text normalization, stopword removal, lemmatization
- **✂️ Semantic Chunking**: Intelligent text splitting preserving context
- **🎯 Multiple Embedding Options**:
  - SentenceTransformers (free, local)
  - OpenAI Embeddings
- **💾 Vector Storage**: ChromaDB for fast similarity search
- **🔍 Smart Retrieval**: BM25 or Cross-Encoder re-ranking
- **🤖 Multiple LLM Providers**:
  - Anthropic Claude
  - OpenAI GPT
  - Local models (Hugging Face)
- **💬 Conversation Memory**: Context-aware multi-turn conversations
- **⚡ Interactive CLI**: User-friendly command-line interface

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd chatbot

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Configuration

Create a `.env` file with your API keys:

```env
# Choose your LLM provider
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Optional: Configure embedding provider
EMBEDDING_PROVIDER=sentence-transformers  # Free, no API key needed
LLM_PROVIDER=anthropic  # or openai
```

### 3. Ingest Documents

```bash
# Ingest a single document
python main.py --ingest "TheUdyog Brochure.pdf"

# Or ingest a directory
python main.py --ingest ./data
```

### 4. Start Chatting!

```bash
# Interactive chat mode
python main.py --chat

# Or ask a single question
python main.py --query "What is TheUdyog?"
```

---

## 📖 Usage Examples

### Interactive Chat

```bash
python main.py --chat
```

```
RAG Chatbot - Interactive Mode
============================================================
Ask questions about your documents!

You: What services does TheUdyog provide?
Assistant: Based on the documents, TheUdyog provides...

You: Tell me more about pricing
Assistant: The pricing structure includes...

You: sources
--- Last Retrieved Sources ---
1. Score: 0.892
   Text: TheUdyog offers comprehensive...
```

### Command Line Queries

```bash
# Simple query
python main.py --query "What is the company's mission?"

# With source citations
python main.py --query "What are the main products?" --sources
```

### Batch Document Processing

```bash
# Ingest all PDFs from a directory
python main.py --ingest ./documents --stats

# Output:
# Ingestion Results:
#   • document1.pdf: 45 chunks
#   • document2.pdf: 32 chunks
# Total: 77 chunks from 2 documents
```

### Custom Configuration

```bash
# Use specific providers
python main.py \
  --embedding-provider openai \
  --llm-provider openai \
  --reranker cross-encoder \
  --chat

# Show current configuration
python main.py --show-config
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Document Ingestion                       │
│  • Multi-format loading (PDF, TXT, CSV, HTML)               │
│  • NLP preprocessing & cleaning                              │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Semantic Chunking                         │
│  • Context-preserving text splitting                         │
│  • Metadata enrichment                                       │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Embedding Generation                        │
│  • SentenceTransformers / OpenAI                            │
│  • Vector representation                                     │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 ChromaDB Vector Storage                      │
│  • Persistent vector database                                │
│  • Fast similarity search                                    │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Retrieval & Re-ranking                           │
│  • Similarity search                                         │
│  • BM25 / Cross-Encoder re-ranking                          │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 LLM Response Generation                      │
│  • Context-aware prompting                                   │
│  • Natural language generation                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 Project Structure

```
chatbot/
├── main.py                      # Main entry point
├── setup.sh                     # Setup script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── DOCUMENTATION.md             # Comprehensive docs
├── README_NEW.md                # This file
│
├── src/
│   ├── rag_chatbot.py          # Main RAG orchestrator
│   │
│   ├── modules/
│   │   ├── document_ingestion.py      # Document loading & preprocessing
│   │   ├── semantic_chunking.py       # Semantic text chunking
│   │   ├── embeddings.py              # Embedding generation
│   │   ├── vector_store.py            # ChromaDB integration
│   │   ├── retrieval.py               # Retrieval & re-ranking
│   │   └── llm_integration.py         # LLM providers
│   │
│   └── utils/
│       └── config.py            # Configuration management
│
├── examples/
│   └── example_usage.py        # Usage examples
│
└── data/                       # Your documents (create this)
```

---

## 🔧 Configuration Options

### Embedding Providers

| Provider | API Key Required | Quality | Speed | Cost |
|----------|-----------------|---------|-------|------|
| `sentence-transformers` | ❌ No | Good | Fast | Free |
| `openai` | ✅ Yes | Excellent | Fast | Paid |

**Recommended Models:**
- Fast & Free: `sentence-transformers/all-MiniLM-L6-v2`
- High Quality: `sentence-transformers/all-mpnet-base-v2`
- OpenAI: `text-embedding-3-small`

### LLM Providers

| Provider | Models | API Key | Cost |
|----------|--------|---------|------|
| `anthropic` | Claude 3 (Sonnet, Opus) | Required | Paid |
| `openai` | GPT-4, GPT-3.5-turbo | Required | Paid |
| `local` | Hugging Face models | Not required | Free |

### Reranker Options

- `bm25`: Fast lexical matching (recommended for most cases)
- `cross-encoder`: Neural re-ranking (more accurate, slower)
- `none`: No re-ranking

---

## 💡 Advanced Usage

### Python API

```python
from src.rag_chatbot import RAGChatbot

# Initialize
chatbot = RAGChatbot(
    embedding_provider="sentence-transformers",
    llm_provider="anthropic",
    reranker_type="bm25",
    chunk_size=512,
    chunk_overlap=50
)

# Ingest documents
chatbot.ingest_document("document.pdf")

# Query
result = chatbot.query(
    "What is this document about?",
    return_sources=True
)

print(result['answer'])
for source in result['sources']:
    print(f"Source: {source['text'][:100]}...")
```

### Custom Embeddings

```python
from src.modules.embeddings import EmbeddingGenerator

# Use custom model
embedder = EmbeddingGenerator(
    provider="sentence-transformers",
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

embeddings = embedder.generate_embeddings([
    "Text to embed",
    "Another text"
])
```

### Metadata Filtering

```python
# Search only in specific documents
documents, context = chatbot.retriever.retrieve_and_rank(
    query="pricing information",
    filter_metadata={"filename": "brochure.pdf"}
)
```

---

## 🎯 Use Cases

1. **📚 Document Q&A**: Answer questions from technical documentation
2. **🏢 Enterprise Knowledge Base**: Query company policies and procedures
3. **📖 Research Assistant**: Extract insights from research papers
4. **💼 Customer Support**: Automated responses based on product manuals
5. **📝 Content Analysis**: Understand and summarize large document collections
6. **🎓 Educational Tool**: Study assistant for textbooks and notes

---

## 🛠️ Development

### Running Tests

```bash
# Test individual modules
python src/modules/document_ingestion.py
python src/modules/semantic_chunking.py
python src/modules/embeddings.py

# Run examples
python examples/example_usage.py --example 1
```

### Adding Custom Document Types

Extend `DocumentIngestion` class in `src/modules/document_ingestion.py`:

```python
def _load_custom_format(self, file_path: Path) -> str:
    # Your custom loading logic
    return extracted_text
```

---

## 📊 Performance Tips

1. **Faster Embeddings**: Use `all-MiniLM-L6-v2` model
2. **Better Quality**: Use `all-mpnet-base-v2` or OpenAI embeddings
3. **Large Documents**: Increase `CHUNK_SIZE` to 1024
4. **Better Retrieval**: Use `cross-encoder` reranker
5. **Memory Issues**: Reduce batch size or chunk size

---

## 🐛 Troubleshooting

### Common Issues

**"API key not found"**
```bash
# Solution: Add to .env file
echo "ANTHROPIC_API_KEY=your_key" >> .env
```

**"No module named 'chromadb'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**"NLTK data not found"**
```bash
# Solution: Download NLTK data
python -c "import nltk; nltk.download('punkt')"
```

**Empty responses**
```bash
# Check if documents are ingested
python main.py --stats

# If total_documents is 0, ingest documents
python main.py --ingest ./data
```

---

## 📝 Documentation

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)

Topics covered:
- Complete architecture overview
- API reference
- Advanced configuration
- Deployment guidelines
- Optimization strategies

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - LLM orchestration
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [Anthropic](https://www.anthropic.com/) - Claude LLM
- [OpenAI](https://openai.com/) - GPT models

---

## 📞 Support

For issues, questions, or contributions:
- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/rag-chatbot/issues)
- 📖 Docs: [Documentation](DOCUMENTATION.md)

---

**Made with ❤️ for better document understanding**

---

## 🚦 Quick Commands Cheat Sheet

```bash
# Setup
./setup.sh && source venv/bin/activate

# Ingest
python main.py --ingest "document.pdf"

# Chat
python main.py --chat

# Query
python main.py --query "your question here" --sources

# Stats
python main.py --stats

# Help
python main.py --help
```

---

## 📈 Roadmap

- [ ] Add support for more document formats (Word, Excel)
- [ ] Implement streaming responses
- [ ] Add web interface (Gradio/Streamlit)
- [ ] Multi-language support
- [ ] Document summarization feature
- [ ] Export conversation history
- [ ] Docker containerization
- [ ] API server mode

---

**Happy chatting! 🎉**
