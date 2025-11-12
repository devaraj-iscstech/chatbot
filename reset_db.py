"""Script to reset the ChromaDB database without interactive prompt."""
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag_chatbot import RAGChatbot
from src.utils.config import Config

def main():
    print("Initializing chatbot...")
    chatbot = RAGChatbot(
        embedding_provider=Config.EMBEDDING_PROVIDER,
        embedding_model=Config.EMBEDDING_MODEL,
        llm_provider=Config.LLM_PROVIDER,
        llm_model=Config.LLM_MODEL,
        reranker_type=Config.RERANKER_TYPE,
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )

    print("\nResetting database...")
    try:
        chatbot.vector_store_manager.vector_store.delete_collection()
        print("✓ Database reset complete!")
        print("\nThe database has been cleared. You can now re-ingest documents.")
    except Exception as e:
        print(f"Error resetting database: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
