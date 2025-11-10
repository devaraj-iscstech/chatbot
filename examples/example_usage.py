#!/usr/bin/env python3
"""
Example Usage of RAG Chatbot
Demonstrates various features and use cases
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_chatbot import RAGChatbot


def example_1_basic_usage():
    """Example 1: Basic document ingestion and querying"""
    print("\n" + "="*60)
    print("Example 1: Basic Usage")
    print("="*60)

    # Initialize chatbot
    chatbot = RAGChatbot(
        embedding_provider="sentence-transformers",
        llm_provider="anthropic"
    )

    # Ingest a document
    print("\n📄 Ingesting document...")
    num_chunks = chatbot.ingest_document("TheUdyog Brochure.pdf")
    print(f"✓ Created {num_chunks} chunks")

    # Ask a question
    print("\n❓ Asking: What is TheUdyog?")
    result = chatbot.query("What is TheUdyog?", return_sources=True)

    print("\n💬 Answer:")
    print(result['answer'])

    if 'sources' in result:
        print("\n📚 Sources:")
        for i, source in enumerate(result['sources'][:3], 1):
            print(f"\n{i}. Score: {source['score']:.3f}")
            print(f"   {source['text'][:200]}...")


def example_2_multiple_documents():
    """Example 2: Ingesting multiple documents"""
    print("\n" + "="*60)
    print("Example 2: Multiple Documents")
    print("="*60)

    chatbot = RAGChatbot()

    # Ingest directory
    print("\n📁 Ingesting all PDF documents...")
    results = chatbot.ingest_directory(".", file_extensions=['.pdf'])

    print("\n✓ Ingestion Results:")
    total = 0
    for filename, chunks in results.items():
        print(f"  • {filename}: {chunks} chunks")
        total += chunks
    print(f"\nTotal: {total} chunks")

    # Query across all documents
    print("\n❓ Asking: What products or services are mentioned?")
    result = chatbot.query("What products or services are mentioned?")
    print("\n💬 Answer:")
    print(result['answer'])


def example_3_conversational():
    """Example 3: Conversational with memory"""
    print("\n" + "="*60)
    print("Example 3: Conversational Mode (with memory)")
    print("="*60)

    chatbot = RAGChatbot()

    # Ensure documents are ingested
    stats = chatbot.get_stats()
    if stats['total_documents'] == 0:
        print("\n📄 No documents found, ingesting...")
        chatbot.ingest_directory(".", file_extensions=['.pdf'])

    # Conversational queries
    questions = [
        "What is TheUdyog?",
        "What services do they offer?",
        "Can you summarize the main benefits?"
    ]

    for q in questions:
        print(f"\n❓ {q}")
        result = chatbot.query(q, use_memory=True)
        print(f"💬 {result['answer'][:300]}...")


def example_4_custom_configuration():
    """Example 4: Custom configuration"""
    print("\n" + "="*60)
    print("Example 4: Custom Configuration")
    print("="*60)

    # Initialize with custom settings
    chatbot = RAGChatbot(
        embedding_provider="sentence-transformers",
        llm_provider="anthropic",
        reranker_type="bm25",
        chunk_size=1024,  # Larger chunks
        chunk_overlap=100,
        collection_name="custom_collection"
    )

    print("\n⚙️ Custom Configuration:")
    print(f"  • Chunk Size: 1024")
    print(f"  • Chunk Overlap: 100")
    print(f"  • Reranker: BM25")
    print(f"  • Collection: custom_collection")

    # Show stats
    stats = chatbot.get_stats()
    print(f"\n📊 Stats:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")


def example_5_advanced_retrieval():
    """Example 5: Advanced retrieval with sources"""
    print("\n" + "="*60)
    print("Example 5: Advanced Retrieval")
    print("="*60)

    chatbot = RAGChatbot()

    # Query with detailed source information
    query = "What are the key features?"
    print(f"\n❓ {query}")

    result = chatbot.query(query, return_sources=True)

    print("\n💬 Answer:")
    print(result['answer'])

    print("\n📚 Retrieved Sources:")
    for i, source in enumerate(result.get('sources', []), 1):
        print(f"\n--- Source {i} ---")
        print(f"Relevance Score: {source['score']:.3f}")
        print(f"Text: {source['text'][:250]}...")

        if source.get('metadata'):
            print(f"Metadata:")
            for key, value in source['metadata'].items():
                print(f"  • {key}: {value}")


def example_6_programmatic_usage():
    """Example 6: Programmatic usage without CLI"""
    print("\n" + "="*60)
    print("Example 6: Programmatic Usage")
    print("="*60)

    from modules.document_ingestion import DocumentIngestion
    from modules.semantic_chunking import SemanticChunker
    from modules.embeddings import EmbeddingGenerator

    # Step-by-step process
    print("\n1️⃣ Loading document...")
    ingestion = DocumentIngestion()
    doc = ingestion.process_document("TheUdyog Brochure.pdf")
    print(f"   ✓ Loaded {len(doc['cleaned_text'])} characters")

    print("\n2️⃣ Creating chunks...")
    chunker = SemanticChunker(chunk_size=512, chunk_overlap=50)
    chunks = chunker.chunk_text(doc['cleaned_text'], metadata=doc['metadata'])
    print(f"   ✓ Created {len(chunks)} chunks")

    print("\n3️⃣ Generating embeddings...")
    embedder = EmbeddingGenerator(provider="sentence-transformers")
    chunk_dicts = [c.to_dict() for c in chunks[:3]]  # Just first 3 for demo
    texts = [c['text'] for c in chunk_dicts]
    embeddings = embedder.generate_embeddings(texts)
    print(f"   ✓ Generated {len(embeddings)} embeddings")
    print(f"   ✓ Embedding dimension: {len(embeddings[0])}")


def main():
    """Run all examples"""
    import argparse

    parser = argparse.ArgumentParser(description="RAG Chatbot Examples")
    parser.add_argument(
        '--example',
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help='Run specific example (1-6), or run all if not specified'
    )

    args = parser.parse_args()

    examples = {
        1: example_1_basic_usage,
        2: example_2_multiple_documents,
        3: example_3_conversational,
        4: example_4_custom_configuration,
        5: example_5_advanced_retrieval,
        6: example_6_programmatic_usage
    }

    try:
        if args.example:
            # Run specific example
            examples[args.example]()
        else:
            # Run all examples
            print("\n" + "="*60)
            print("Running All Examples")
            print("="*60)

            # Note: Only run examples that don't require LLM API keys
            print("\nNote: Examples requiring LLM API will be skipped if not configured")

            # Safe examples (no LLM required)
            example_6_programmatic_usage()

            # Examples requiring API keys
            print("\n⚠️  Other examples require LLM API keys (OpenAI or Anthropic)")
            print("To run them, ensure your .env file is configured and run:")
            print("  python examples/example_usage.py --example 1")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
