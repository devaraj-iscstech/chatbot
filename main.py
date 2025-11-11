#!/usr/bin/env python3
"""
RAG Chatbot - Main Entry Point
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_chatbot import RAGChatbot
from utils.config import Config, validate_config


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="RAG Chatbot - Answer questions based on your documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest documents and start chat
  python main.py --ingest ./documents

  # Ingest single document
  python main.py --ingest "TheUdyog Brochure.pdf" --chat

  # Ask a single question
  python main.py --query "What is TheUdyog?"

  # Show system statistics
  python main.py --stats

  # Use specific providers
  python main.py --embedding-provider openai --llm-provider openai --chat

  # Show configuration
  python main.py --show-config
        """
    )

    # Document ingestion
    parser.add_argument(
        '--ingest',
        type=str,
        metavar='PATH',
        help='Ingest a document file or directory'
    )

    # Query modes
    parser.add_argument(
        '--query',
        type=str,
        metavar='QUESTION',
        help='Ask a single question and exit'
    )
    parser.add_argument(
        '--chat',
        action='store_true',
        help='Start interactive chat mode'
    )

    # Provider settings
    parser.add_argument(
        '--embedding-provider',
        type=str,
        choices=['sentence-transformers', 'openai'],
        default=Config.EMBEDDING_PROVIDER,
        help=f'Embedding provider (default: {Config.EMBEDDING_PROVIDER})'
    )
    parser.add_argument(
        '--embedding-model',
        type=str,
        help='Specific embedding model name'
    )
    parser.add_argument(
        '--llm-provider',
        type=str,
        choices=['openai', 'anthropic', 'google', 'local'],
        default=Config.LLM_PROVIDER,
        help=f'LLM provider (default: {Config.LLM_PROVIDER})'
    )
    parser.add_argument(
        '--llm-model',
        type=str,
        help='Specific LLM model name'
    )

    # Retrieval settings
    parser.add_argument(
        '--reranker',
        type=str,
        choices=['bm25', 'cross-encoder', 'none'],
        default=Config.RERANKER_TYPE,
        help=f'Reranker type (default: {Config.RERANKER_TYPE})'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=Config.TOP_K_RERANK,
        help=f'Number of top documents to use (default: {Config.TOP_K_RERANK})'
    )

    # Other options
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show system statistics'
    )
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Show current configuration'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset vector database (delete all documents)'
    )
    parser.add_argument(
        '--sources',
        action='store_true',
        help='Show source documents with answers'
    )

    args = parser.parse_args()

    # Show config if requested
    if args.show_config:
        Config.print_config()
        return

    # Validate configuration
    if not validate_config():
        print("\nPlease fix configuration errors before continuing.")
        print("You can set environment variables or create a .env file.")
        sys.exit(1)

    print("\n" + "="*60)
    print("RAG Chatbot - Retrieval-Augmented Generation System")
    print("="*60)

    try:
        # Initialize chatbot
        print("\nInitializing chatbot...")
        chatbot = RAGChatbot(
            embedding_provider=args.embedding_provider,
            embedding_model=args.embedding_model,
            llm_provider=args.llm_provider,
            llm_model=args.llm_model,
            reranker_type=args.reranker,
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )

        # Reset if requested
        if args.reset:
            response = input("\nAre you sure you want to reset the database? (yes/no): ")
            if response.lower() == 'yes':
                chatbot.vector_store_manager.vector_store.delete_collection()
                print("Database reset complete.")
                return

        # Ingest documents if specified
        if args.ingest:
            print(f"\nIngesting from: {args.ingest}")
            path = Path(args.ingest)

            if path.is_file():
                num_chunks = chatbot.ingest_document(str(path))
                print(f"✓ Ingested {num_chunks} chunks from {path.name}")
            elif path.is_dir():
                results = chatbot.ingest_directory(str(path))
                print("\n✓ Ingestion Complete:")
                total_chunks = 0
                for filename, num_chunks in results.items():
                    print(f"  • {filename}: {num_chunks} chunks")
                    total_chunks += num_chunks
                print(f"\nTotal: {total_chunks} chunks from {len(results)} documents")
            else:
                print(f"Error: {args.ingest} not found")
                sys.exit(1)

        # Show stats if requested
        if args.stats:
            stats = chatbot.get_stats()
            print("\n" + "="*60)
            print("System Statistics")
            print("="*60)
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            print("="*60)

        # Handle query or chat mode
        if args.query:
            # Single query mode
            print(f"\nQuestion: {args.query}")
            print("\nGenerating answer...")

            result = chatbot.query(
                args.query,
                return_sources=args.sources
            )

            print("\n" + "="*60)
            print("Answer:")
            print("="*60)
            print(result['answer'])

            if args.sources and 'sources' in result:
                print("\n" + "="*60)
                print("Sources:")
                print("="*60)
                for i, source in enumerate(result['sources'], 1):
                    print(f"\n{i}. Relevance Score: {source['score']:.3f}")
                    print(f"   {source['text']}")
                    if source.get('metadata'):
                        print(f"   Source: {source['metadata'].get('filename', 'Unknown')}")

        elif args.chat or not args.stats:
            # Interactive chat mode
            chatbot.chat(enable_memory=True)

    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
