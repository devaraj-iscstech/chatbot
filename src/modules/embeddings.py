"""
Embedding Generation Module
Converts text chunks into vector embeddings using various embedding models
"""

import os
from typing import List, Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

import numpy as np
from sentence_transformers import SentenceTransformer

# Optional: OpenAI embeddings
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingModel(ABC):
    """Abstract base class for embedding models"""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        pass


class SentenceTransformerEmbedding(EmbeddingModel):
    """
    Embedding model using Sentence Transformers
    Supports local models without API keys
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize Sentence Transformer model

        Args:
            model_name: Name of the model from Hugging Face
                       Popular options:
                       - all-MiniLM-L6-v2: Fast, 384 dimensions
                       - all-mpnet-base-v2: High quality, 768 dimensions
                       - multi-qa-mpnet-base-dot-v1: Optimized for Q&A
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.dimension

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [t if t and t.strip() else " " for t in texts]

        embeddings = self.model.encode(
            valid_texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.dimension


class OpenAIEmbedding(EmbeddingModel):
    """
    Embedding model using OpenAI's API
    Requires OPENAI_API_KEY environment variable
    """

    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedding model

        Args:
            model_name: OpenAI embedding model name
                       Options:
                       - text-embedding-3-small: 1536 dimensions, faster
                       - text-embedding-3-large: 3072 dimensions, higher quality
                       - text-embedding-ada-002: 1536 dimensions, legacy
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)

        # Set dimension based on model
        dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        self.dimension = dimension_map.get(model_name, 1536)

        logger.info(f"Initialized OpenAI embedding model: {model_name}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            return [0.0] * self.dimension

        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )

        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts (up to 2048 texts)"""
        if not texts:
            return []

        # Filter empty texts
        valid_texts = [t if t and t.strip() else " " for t in texts]

        # OpenAI allows up to 2048 texts per request
        batch_size = 2048
        all_embeddings = []

        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i:i + batch_size]

            response = self.client.embeddings.create(
                model=self.model_name,
                input=batch
            )

            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.dimension


class GoogleEmbedding(EmbeddingModel):
    """
    Embedding model using Google AI's Gemini embedding models
    Supports gemini-embedding-001 and other Google embedding models
    """

    def __init__(self, model_name: str = "models/embedding-001"):
        """
        Initialize Google AI embedding model

        Args:
            model_name: Google embedding model name
                       Options:
                       - models/embedding-001: 768 dimensions, high quality
                       - models/text-embedding-004: Latest model
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model_name = model_name

        # Gemini embeddings are 768 dimensions
        self.dimension = 768

        logger.info(f"Initialized Google embedding model: {model_name}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        import google.generativeai as genai

        if not text or not text.strip():
            return [0.0] * self.dimension

        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating Google embedding: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        import google.generativeai as genai

        if not texts:
            return []

        # Filter empty texts
        valid_texts = [t if t and t.strip() else " " for t in texts]

        all_embeddings = []

        # Google API has limits, process in batches
        batch_size = 100

        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i:i + batch_size]

            try:
                # Embed batch
                for text in batch:
                    result = genai.embed_content(
                        model=self.model_name,
                        content=text,
                        task_type="retrieval_document"
                    )
                    all_embeddings.append(result['embedding'])

            except Exception as e:
                logger.error(f"Error in batch embedding: {e}")
                # Add zero vectors for failed embeddings
                all_embeddings.extend([[0.0] * self.dimension] * len(batch))

        return all_embeddings

    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.dimension


class EmbeddingGenerator:
    """
    High-level interface for generating embeddings
    Manages different embedding models
    """

    def __init__(
        self,
        provider: str = "sentence-transformers",
        model_name: Optional[str] = None
    ):
        """
        Initialize embedding generator

        Args:
            provider: Embedding provider ('sentence-transformers', 'openai', or 'google')
            model_name: Specific model name (optional, uses defaults if not provided)
        """
        self.provider = provider

        if provider == "sentence-transformers":
            default_model = "sentence-transformers/all-MiniLM-L6-v2"
            self.model = SentenceTransformerEmbedding(model_name or default_model)
        elif provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not available. Install with: pip install openai")
            default_model = "text-embedding-3-small"
            self.model = OpenAIEmbedding(model_name or default_model)
        elif provider == "google":
            default_model = "models/embedding-001"
            self.model = GoogleEmbedding(model_name or default_model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        logger.info(f"Initialized EmbeddingGenerator with {provider}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        return self.model.embed_text(text)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return self.model.embed_batch(texts)

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return self.model.get_dimension()

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks and add them to chunk data

        Args:
            chunks: List of chunk dictionaries with 'text' field

        Returns:
            List of chunks with added 'embedding' field
        """
        # Extract texts
        texts = [chunk.get('text', '') for chunk in chunks]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.generate_embeddings(texts)

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding

        logger.info(f"Successfully generated {len(embeddings)} embeddings")
        return chunks


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score between -1 and 1
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


if __name__ == "__main__":
    # Test the embedding generator
    generator = EmbeddingGenerator(provider="sentence-transformers")

    # Test single text
    text = "This is a test sentence for embedding generation."
    embedding = generator.generate_embedding(text)

    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Test batch
    texts = [
        "Artificial intelligence is transforming technology.",
        "Machine learning models require large datasets.",
        "Natural language processing enables text understanding."
    ]

    embeddings = generator.generate_embeddings(texts)
    print(f"\nGenerated {len(embeddings)} embeddings")

    # Test similarity
    sim = cosine_similarity(embeddings[0], embeddings[1])
    print(f"\nSimilarity between first two texts: {sim:.4f}")
