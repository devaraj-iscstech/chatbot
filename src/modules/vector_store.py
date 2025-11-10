"""
Vector Store Module using ChromaDB
Stores and retrieves document embeddings for similarity search
"""

import os
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector database for storing and retrieving document embeddings
    Uses ChromaDB for efficient similarity search
    """

    def __init__(
        self,
        collection_name: str = "rag_documents",
        persist_directory: str = "./chroma_db",
        reset: bool = False
    ):
        """
        Initialize ChromaDB vector store

        Args:
            collection_name: Name of the collection to store embeddings
            persist_directory: Directory to persist the database
            reset: If True, delete existing collection and start fresh
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Create persist directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Reset collection if requested
        if reset:
            try:
                self.client.delete_collection(name=collection_name)
                logger.info(f"Deleted existing collection: {collection_name}")
            except:
                pass

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.info(f"Created new collection: {collection_name}")

    def add_documents(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> None:
        """
        Add document chunks and their embeddings to the vector store

        Args:
            chunks: List of chunk dictionaries containing text and metadata
            embeddings: List of embedding vectors corresponding to chunks
        """
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings provided")
            return

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        embeddings_list = []

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate unique ID
            chunk_id = chunk.get('chunk_id', f"chunk_{idx}")
            ids.append(chunk_id)

            # Extract text
            text = chunk.get('text', '')
            documents.append(text)

            # Extract metadata (ChromaDB requires string values)
            metadata = chunk.get('metadata', {})
            # Convert all metadata values to strings
            clean_metadata = {
                k: str(v) if v is not None else ""
                for k, v in metadata.items()
            }
            # Add chunk index
            clean_metadata['chunk_index'] = str(chunk.get('chunk_index', idx))
            metadatas.append(clean_metadata)

            # Add embedding
            embeddings_list.append(embedding)

        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings_list
            )
            logger.info(f"Added {len(ids)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using query embedding

        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of top results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of similar documents with metadata and scores
        """
        try:
            # Perform similarity search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata if filter_metadata else None
            )

            # Format results
            formatted_results = []

            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    }
                    formatted_results.append(result)

            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results

        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            return []

    def search_by_text(
        self,
        query_text: str,
        embedding_generator,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using query text

        Args:
            query_text: Text query
            embedding_generator: EmbeddingGenerator instance to create query embedding
            top_k: Number of top results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of similar documents with metadata and scores
        """
        # Generate query embedding
        query_embedding = embedding_generator.generate_embedding(query_text)

        # Perform search
        return self.similarity_search(query_embedding, top_k, filter_metadata)

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection

        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()

        return {
            'collection_name': self.collection_name,
            'total_documents': count,
            'persist_directory': self.persist_directory
        }

    def delete_collection(self) -> None:
        """Delete the current collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

    def get_all_documents(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all documents from the collection

        Args:
            limit: Maximum number of documents to retrieve

        Returns:
            List of all documents with metadata
        """
        try:
            count = self.collection.count()
            fetch_limit = min(limit, count) if limit else count

            if fetch_limit == 0:
                return []

            results = self.collection.get(
                limit=fetch_limit,
                include=['documents', 'metadatas']
            )

            documents = []
            for i in range(len(results['ids'])):
                doc = {
                    'id': results['ids'][i],
                    'text': results['documents'][i],
                    'metadata': results['metadatas'][i]
                }
                documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def update_document(
        self,
        doc_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        embedding: Optional[List[float]] = None
    ) -> None:
        """
        Update an existing document

        Args:
            doc_id: ID of the document to update
            text: New text (optional)
            metadata: New metadata (optional)
            embedding: New embedding (optional)
        """
        try:
            update_params = {'ids': [doc_id]}

            if text is not None:
                update_params['documents'] = [text]
            if metadata is not None:
                update_params['metadatas'] = [metadata]
            if embedding is not None:
                update_params['embeddings'] = [embedding]

            self.collection.update(**update_params)
            logger.info(f"Updated document: {doc_id}")

        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise


class VectorStoreManager:
    """
    High-level manager for vector store operations
    Coordinates between document processing and storage
    """

    def __init__(
        self,
        embedding_generator,
        collection_name: str = "rag_documents",
        persist_directory: str = "./chroma_db"
    ):
        """
        Initialize vector store manager

        Args:
            embedding_generator: EmbeddingGenerator instance
            collection_name: Name for the ChromaDB collection
            persist_directory: Directory to persist the database
        """
        self.embedding_generator = embedding_generator
        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory
        )

    def index_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Index documents by generating embeddings and storing them

        Args:
            chunks: List of text chunks with metadata
        """
        if not chunks:
            logger.warning("No chunks to index")
            return

        # Generate embeddings if not already present
        if 'embedding' not in chunks[0]:
            logger.info("Generating embeddings for chunks...")
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings(texts)

            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk['embedding'] = embedding
        else:
            embeddings = [chunk['embedding'] for chunk in chunks]

        # Store in vector database
        self.vector_store.add_documents(chunks, embeddings)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents

        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of relevant documents with scores
        """
        return self.vector_store.search_by_text(
            query_text=query,
            embedding_generator=self.embedding_generator,
            top_k=top_k,
            filter_metadata=filter_metadata
        )


if __name__ == "__main__":
    # Test the vector store
    from embeddings import EmbeddingGenerator

    # Initialize
    embedding_gen = EmbeddingGenerator(provider="sentence-transformers")
    vector_store = VectorStore(collection_name="test_collection", reset=True)

    # Create sample chunks
    sample_chunks = [
        {
            'chunk_id': 'chunk_1',
            'text': 'Machine learning is a subset of artificial intelligence.',
            'metadata': {'source': 'test', 'topic': 'ml'}
        },
        {
            'chunk_id': 'chunk_2',
            'text': 'Neural networks are inspired by biological neurons.',
            'metadata': {'source': 'test', 'topic': 'dl'}
        }
    ]

    # Generate embeddings
    texts = [c['text'] for c in sample_chunks]
    embeddings = embedding_gen.generate_embeddings(texts)

    # Add to vector store
    vector_store.add_documents(sample_chunks, embeddings)

    # Search
    query = "What is machine learning?"
    results = vector_store.search_by_text(query, embedding_gen, top_k=2)

    print(f"\nSearch results for: '{query}'")
    for r in results:
        print(f"\nText: {r['text']}")
        print(f"Metadata: {r['metadata']}")
        print(f"Distance: {r['distance']}")
