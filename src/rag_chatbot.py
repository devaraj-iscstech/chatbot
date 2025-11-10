"""
RAG Chatbot - Main Interface
Orchestrates the complete RAG pipeline
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.document_ingestion import DocumentIngestion
from modules.semantic_chunking import SemanticChunker
from modules.embeddings import EmbeddingGenerator
from modules.vector_store import VectorStoreManager
from modules.retrieval import RAGRetriever
from modules.llm_integration import ResponseGenerator, ConversationMemory

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGChatbot:
    """
    Complete RAG Chatbot System
    Combines document ingestion, embedding, retrieval, and generation
    """

    def __init__(
        self,
        embedding_provider: str = "sentence-transformers",
        embedding_model: Optional[str] = None,
        llm_provider: str = "anthropic",
        llm_model: Optional[str] = None,
        collection_name: str = "rag_documents",
        persist_directory: str = "./chroma_db",
        reranker_type: str = "bm25",
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """
        Initialize RAG Chatbot

        Args:
            embedding_provider: Provider for embeddings ('sentence-transformers' or 'openai')
            embedding_model: Specific embedding model name
            llm_provider: Provider for LLM ('openai', 'anthropic', or 'local')
            llm_model: Specific LLM model name
            collection_name: Name for vector database collection
            persist_directory: Directory to persist vector database
            reranker_type: Type of reranker ('bm25', 'cross-encoder', or 'none')
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        logger.info("Initializing RAG Chatbot...")

        # Initialize components
        self.document_ingestion = DocumentIngestion()
        self.chunker = SemanticChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_generator = EmbeddingGenerator(
            provider=embedding_provider,
            model_name=embedding_model
        )
        self.vector_store_manager = VectorStoreManager(
            embedding_generator=self.embedding_generator,
            collection_name=collection_name,
            persist_directory=persist_directory
        )
        self.retriever = RAGRetriever(
            vector_store_manager=self.vector_store_manager,
            reranker_type=reranker_type
        )
        self.response_generator = ResponseGenerator(
            provider=llm_provider,
            model_name=llm_model
        )
        self.conversation_memory = ConversationMemory()

        logger.info("RAG Chatbot initialized successfully!")

    def ingest_document(
        self,
        file_path: str,
        aggressive_cleaning: bool = False
    ) -> int:
        """
        Ingest a document into the RAG system

        Args:
            file_path: Path to the document
            aggressive_cleaning: Whether to apply aggressive NLP preprocessing

        Returns:
            Number of chunks created
        """
        logger.info(f"Ingesting document: {file_path}")

        # Step 1: Load and preprocess document
        doc_data = self.document_ingestion.process_document(
            file_path,
            aggressive_cleaning=aggressive_cleaning
        )

        # Step 2: Create semantic chunks
        chunks = self.chunker.chunk_text(
            text=doc_data['cleaned_text'],
            metadata=doc_data['metadata']
        )

        # Add context to chunks
        document_title = doc_data['metadata'].get('filename', 'Unknown')
        self.chunker.add_context_to_chunks(chunks, document_title=document_title)

        # Convert to dictionaries
        chunk_dicts = [chunk.to_dict() for chunk in chunks]

        # Step 3: Index documents (generate embeddings and store)
        self.vector_store_manager.index_documents(chunk_dicts)

        logger.info(f"Successfully ingested {len(chunks)} chunks from {file_path}")
        return len(chunks)

    def ingest_directory(
        self,
        directory_path: str,
        file_extensions: List[str] = None
    ) -> Dict[str, int]:
        """
        Ingest all documents from a directory

        Args:
            directory_path: Path to directory containing documents
            file_extensions: List of file extensions to process (e.g., ['.pdf', '.txt'])

        Returns:
            Dictionary mapping filenames to number of chunks
        """
        if file_extensions is None:
            file_extensions = ['.pdf', '.txt', '.csv', '.html', '.md']

        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        results = {}

        # Find all matching files
        for ext in file_extensions:
            for file_path in directory.glob(f"*{ext}"):
                try:
                    num_chunks = self.ingest_document(str(file_path))
                    results[file_path.name] = num_chunks
                except Exception as e:
                    logger.error(f"Error ingesting {file_path.name}: {e}")
                    results[file_path.name] = 0

        return results

    def query(
        self,
        question: str,
        use_memory: bool = False,
        return_sources: bool = False
    ) -> Dict[str, Any]:
        """
        Ask a question and get a response

        Args:
            question: User question
            use_memory: Whether to use conversation memory
            return_sources: Whether to return source documents

        Returns:
            Dictionary with answer and optional sources
        """
        logger.info(f"Processing query: {question[:50]}...")

        # Step 1: Retrieve relevant documents
        documents, context = self.retriever.retrieve_and_rank(question)

        # Step 2: Generate response
        if use_memory:
            history = self.conversation_memory.get_history()
            answer = self.response_generator.generate_conversational_response(
                query=question,
                context=context,
                conversation_history=history
            )
            # Add to memory
            self.conversation_memory.add_message('user', question)
            self.conversation_memory.add_message('assistant', answer)
        else:
            answer = self.response_generator.generate_response(
                query=question,
                context=context
            )

        result = {
            'answer': answer,
            'question': question
        }

        if return_sources:
            sources = []
            for doc in documents:
                source = {
                    'text': doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                    'score': doc.score,
                    'metadata': doc.metadata
                }
                sources.append(source)
            result['sources'] = sources

        return result

    def chat(self, enable_memory: bool = True):
        """
        Interactive chat interface

        Args:
            enable_memory: Whether to enable conversation memory
        """
        print("\n" + "="*60)
        print("RAG Chatbot - Interactive Mode")
        print("="*60)
        print("Ask questions about your documents!")
        print("Commands: 'quit' to exit, 'clear' to clear history, 'sources' to see last sources")
        print("="*60 + "\n")

        last_sources = []

        while True:
            try:
                question = input("\nYou: ").strip()

                if not question:
                    continue

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                if question.lower() == 'clear':
                    self.conversation_memory.clear_history()
                    print("Conversation history cleared.")
                    continue

                if question.lower() == 'sources':
                    if last_sources:
                        print("\n--- Last Retrieved Sources ---")
                        for i, source in enumerate(last_sources, 1):
                            print(f"\n{i}. Score: {source['score']:.3f}")
                            print(f"   Text: {source['text']}")
                            if source['metadata']:
                                print(f"   Metadata: {source['metadata']}")
                    else:
                        print("No sources available yet.")
                    continue

                # Get response
                result = self.query(
                    question=question,
                    use_memory=enable_memory,
                    return_sources=True
                )

                # Store sources
                last_sources = result.get('sources', [])

                # Print answer
                print(f"\nAssistant: {result['answer']}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error during chat: {e}")
                print(f"\nError: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system

        Returns:
            Dictionary with system statistics
        """
        stats = self.vector_store_manager.vector_store.get_collection_stats()
        stats['embedding_dimension'] = self.embedding_generator.get_embedding_dimension()
        stats['conversation_history_length'] = len(self.conversation_memory.get_history())

        return stats


def main():
    """Main entry point for CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="RAG Chatbot")
    parser.add_argument(
        '--ingest',
        type=str,
        help='Ingest a document or directory'
    )
    parser.add_argument(
        '--embedding-provider',
        type=str,
        default='sentence-transformers',
        choices=['sentence-transformers', 'openai'],
        help='Embedding provider'
    )
    parser.add_argument(
        '--llm-provider',
        type=str,
        default='anthropic',
        choices=['openai', 'anthropic', 'local'],
        help='LLM provider'
    )
    parser.add_argument(
        '--reranker',
        type=str,
        default='bm25',
        choices=['bm25', 'cross-encoder', 'none'],
        help='Reranker type'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Single query mode'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show system statistics'
    )

    args = parser.parse_args()

    # Initialize chatbot
    chatbot = RAGChatbot(
        embedding_provider=args.embedding_provider,
        llm_provider=args.llm_provider,
        reranker_type=args.reranker
    )

    # Ingest documents if specified
    if args.ingest:
        path = Path(args.ingest)
        if path.is_file():
            num_chunks = chatbot.ingest_document(str(path))
            print(f"Ingested {num_chunks} chunks from {path.name}")
        elif path.is_dir():
            results = chatbot.ingest_directory(str(path))
            print("\nIngestion Results:")
            for filename, num_chunks in results.items():
                print(f"  {filename}: {num_chunks} chunks")

    # Show stats if requested
    if args.stats:
        stats = chatbot.get_stats()
        print("\n--- System Statistics ---")
        for key, value in stats.items():
            print(f"{key}: {value}")

    # Handle query or start interactive mode
    if args.query:
        result = chatbot.query(args.query, return_sources=True)
        print(f"\nQuestion: {result['question']}")
        print(f"\nAnswer: {result['answer']}")
        if 'sources' in result:
            print("\n--- Sources ---")
            for i, source in enumerate(result['sources'], 1):
                print(f"\n{i}. Score: {source['score']:.3f}")
                print(f"   {source['text']}")
    else:
        # Start interactive chat
        chatbot.chat()


if __name__ == "__main__":
    main()
