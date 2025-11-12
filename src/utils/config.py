"""
Configuration Management for RAG Chatbot
"""

import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (override system env vars with .env file)
load_dotenv(override=True)


class Config:
    """Configuration class for RAG Chatbot"""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

    # Embedding Settings
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-sonnet-20240229")

    # ChromaDB Settings
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_documents")

    # Chunking Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    MIN_CHUNK_SIZE = int(os.getenv("MIN_CHUNK_SIZE", "100"))

    # Retrieval Settings
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
    TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", "5"))
    RERANKER_TYPE = os.getenv("RERANKER_TYPE", "bm25")  # bm25, cross-encoder, none

    # Generation Settings
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

    # Preprocessing Settings
    AGGRESSIVE_CLEANING = os.getenv("AGGRESSIVE_CLEANING", "false").lower() == "true"

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            key: value
            for key, value in cls.__dict__.items()
            if not key.startswith('_') and key.isupper()
        }

    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n=== RAG Chatbot Configuration ===")
        config = cls.to_dict()
        for key, value in config.items():
            # Mask API keys
            if 'API_KEY' in key and value:
                value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"{key}: {value}")
        print("=" * 35 + "\n")


def validate_config() -> bool:
    """
    Validate configuration

    Returns:
        True if configuration is valid
    """
    errors = []

    # Check API keys based on provider
    if Config.LLM_PROVIDER == "openai" and not Config.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required for OpenAI LLM provider")

    if Config.LLM_PROVIDER == "anthropic" and not Config.ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY is required for Anthropic LLM provider")

    if Config.LLM_PROVIDER == "google" and not Config.GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is required for Google AI LLM provider")

    if Config.EMBEDDING_PROVIDER == "openai" and not Config.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required for OpenAI embedding provider")

    if Config.EMBEDDING_PROVIDER == "google" and not Config.GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is required for Google AI embedding provider")

    # Check numeric values
    if Config.CHUNK_SIZE <= 0:
        errors.append("CHUNK_SIZE must be positive")

    if Config.CHUNK_OVERLAP < 0:
        errors.append("CHUNK_OVERLAP must be non-negative")

    if Config.CHUNK_OVERLAP >= Config.CHUNK_SIZE:
        errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")

    if Config.TOP_K_RETRIEVAL <= 0:
        errors.append("TOP_K_RETRIEVAL must be positive")

    if Config.TOP_K_RERANK <= 0:
        errors.append("TOP_K_RERANK must be positive")

    if Config.TEMPERATURE < 0 or Config.TEMPERATURE > 2:
        errors.append("TEMPERATURE must be between 0 and 2")

    if errors:
        print("\nConfiguration Errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True
