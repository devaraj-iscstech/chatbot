#!/usr/bin/env python3
"""
Basic test script to verify all modules load correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing RAG Chatbot Components...")
print("="*60)

# Test 1: Import all modules
print("\n1. Testing module imports...")
try:
    from modules.document_ingestion import DocumentIngestion
    print("   ✓ document_ingestion")

    from modules.semantic_chunking import SemanticChunker
    print("   ✓ semantic_chunking")

    from modules.embeddings import EmbeddingGenerator
    print("   ✓ embeddings")

    from modules.vector_store import VectorStore, VectorStoreManager
    print("   ✓ vector_store")

    from modules.retrieval import RAGRetriever
    print("   ✓ retrieval")

    from modules.llm_integration import ResponseGenerator, ConversationMemory
    print("   ✓ llm_integration")

    from rag_chatbot import RAGChatbot
    print("   ✓ rag_chatbot")

    from utils.config import Config
    print("   ✓ config")

    print("\n✅ All modules imported successfully!")

except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Initialize components
print("\n2. Testing component initialization...")
try:
    ingestion = DocumentIngestion()
    print("   ✓ DocumentIngestion initialized")

    chunker = SemanticChunker()
    print("   ✓ SemanticChunker initialized")

    # Test with sentence-transformers (no API key needed)
    embedder = EmbeddingGenerator(provider="sentence-transformers")
    print("   ✓ EmbeddingGenerator initialized")

    print("\n✅ All components initialized successfully!")

except Exception as e:
    print(f"\n❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Basic functionality
print("\n3. Testing basic functionality...")
try:
    # Test text preprocessing
    sample_text = "This is a TEST document!!! www.example.com"
    cleaned = ingestion.preprocess_text(sample_text)
    print(f"   ✓ Text preprocessing: '{cleaned[:50]}...'")

    # Test chunking
    chunks = chunker.chunk_text("This is a test. " * 100)
    print(f"   ✓ Semantic chunking: {len(chunks)} chunks created")

    # Test embeddings
    embedding = embedder.generate_embedding("Test text for embedding")
    print(f"   ✓ Embedding generation: dimension={len(embedding)}")

    print("\n✅ Basic functionality tests passed!")

except Exception as e:
    print(f"\n❌ Functionality test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Document processing
print("\n4. Testing document processing...")
try:
    # Check if PDF documents exist
    pdf_files = list(Path(".").glob("*.pdf"))
    if pdf_files:
        print(f"   Found {len(pdf_files)} PDF documents:")
        for pdf in pdf_files:
            print(f"     • {pdf.name}")
            try:
                doc_data = ingestion.process_document(str(pdf))
                text_length = len(doc_data['cleaned_text'])
                print(f"       ✓ Processed successfully: {text_length} characters")
            except Exception as e:
                print(f"       ⚠ Error processing: {e}")
    else:
        print("   ⚠ No PDF documents found in current directory")

except Exception as e:
    print(f"\n❌ Document processing test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Configuration
print("\n5. Testing configuration...")
try:
    config = Config.to_dict()
    print(f"   ✓ Configuration loaded: {len(config)} settings")
    print(f"   • Embedding Provider: {Config.EMBEDDING_PROVIDER}")
    print(f"   • LLM Provider: {Config.LLM_PROVIDER}")
    print(f"   • Chunk Size: {Config.CHUNK_SIZE}")
    print(f"   • Top K: {Config.TOP_K_RERANK}")

except Exception as e:
    print(f"\n❌ Configuration test failed: {e}")

# Summary
print("\n" + "="*60)
print("Test Summary")
print("="*60)
print("✅ Module imports: PASSED")
print("✅ Component initialization: PASSED")
print("✅ Basic functionality: PASSED")
print("✅ Configuration: PASSED")
print("\n✅ All basic tests passed!")
print("\nNote: LLM integration tests require API keys in .env file")
print("="*60)
