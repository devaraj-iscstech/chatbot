"""
Retrieval and Re-ranking Module
Handles query processing, document retrieval, and result re-ranking
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
    """Represents a retrieved document with score"""
    text: str
    metadata: Dict[str, Any]
    score: float
    doc_id: str
    rank: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'text': self.text,
            'metadata': self.metadata,
            'score': self.score,
            'doc_id': self.doc_id,
            'rank': self.rank
        }


class Retriever:
    """
    Handles document retrieval from vector store
    """

    def __init__(self, vector_store_manager, top_k: int = 10):
        """
        Initialize retriever

        Args:
            vector_store_manager: VectorStoreManager instance
            top_k: Number of documents to retrieve initially
        """
        self.vector_store_manager = vector_store_manager
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, str]] = None
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents for a query

        Args:
            query: User query
            top_k: Number of documents to retrieve (overrides default)
            filter_metadata: Optional metadata filters

        Returns:
            List of RetrievedDocument objects
        """
        k = top_k if top_k is not None else self.top_k

        # Retrieve from vector store
        results = self.vector_store_manager.search(
            query=query,
            top_k=k,
            filter_metadata=filter_metadata
        )

        # Convert to RetrievedDocument objects
        retrieved_docs = []
        for idx, result in enumerate(results):
            doc = RetrievedDocument(
                text=result['text'],
                metadata=result.get('metadata', {}),
                score=1.0 - result.get('distance', 0.0),  # Convert distance to similarity
                doc_id=result.get('id', f'doc_{idx}'),
                rank=idx + 1
            )
            retrieved_docs.append(doc)

        logger.info(f"Retrieved {len(retrieved_docs)} documents for query: '{query[:50]}...'")
        return retrieved_docs


class BM25Reranker:
    """
    Re-ranks retrieved documents using BM25 algorithm
    BM25 is a bag-of-words retrieval function that ranks documents based on query term frequency
    """

    def __init__(self):
        """Initialize BM25 reranker"""
        self.bm25 = None
        self.documents = []

    def rerank(
        self,
        query: str,
        documents: List[RetrievedDocument],
        top_k: int = 5
    ) -> List[RetrievedDocument]:
        """
        Re-rank documents using BM25

        Args:
            query: User query
            documents: List of retrieved documents
            top_k: Number of top documents to return

        Returns:
            Re-ranked list of documents
        """
        if not documents:
            return []

        # Tokenize documents
        tokenized_docs = [doc.text.lower().split() for doc in documents]

        # Create BM25 index
        self.bm25 = BM25Okapi(tokenized_docs)

        # Tokenize query
        tokenized_query = query.lower().split()

        # Get BM25 scores
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Combine vector similarity and BM25 scores
        for doc, bm25_score in zip(documents, bm25_scores):
            # Weighted combination: 70% vector similarity + 30% BM25
            doc.score = 0.7 * doc.score + 0.3 * (bm25_score / max(bm25_scores) if max(bm25_scores) > 0 else 0)

        # Sort by combined score
        reranked = sorted(documents, key=lambda x: x.score, reverse=True)

        # Update ranks
        for idx, doc in enumerate(reranked[:top_k]):
            doc.rank = idx + 1

        logger.info(f"Re-ranked documents using BM25, returning top {min(top_k, len(reranked))}")
        return reranked[:top_k]


class CrossEncoderReranker:
    """
    Re-ranks documents using a cross-encoder model
    Cross-encoders jointly encode query and document for better relevance scoring
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize cross-encoder reranker

        Args:
            model_name: Name of the cross-encoder model
        """
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
            self.available = True
            logger.info(f"Loaded cross-encoder model: {model_name}")
        except Exception as e:
            logger.warning(f"Could not load cross-encoder: {e}")
            self.available = False

    def rerank(
        self,
        query: str,
        documents: List[RetrievedDocument],
        top_k: int = 5
    ) -> List[RetrievedDocument]:
        """
        Re-rank documents using cross-encoder

        Args:
            query: User query
            documents: List of retrieved documents
            top_k: Number of top documents to return

        Returns:
            Re-ranked list of documents
        """
        if not self.available:
            logger.warning("Cross-encoder not available, returning original documents")
            return documents[:top_k]

        if not documents:
            return []

        # Prepare query-document pairs
        pairs = [[query, doc.text] for doc in documents]

        # Get cross-encoder scores
        scores = self.model.predict(pairs)

        # Update document scores
        for doc, score in zip(documents, scores):
            doc.score = float(score)

        # Sort by score
        reranked = sorted(documents, key=lambda x: x.score, reverse=True)

        # Update ranks
        for idx, doc in enumerate(reranked[:top_k]):
            doc.rank = idx + 1

        logger.info(f"Re-ranked documents using cross-encoder, returning top {min(top_k, len(reranked))}")
        return reranked[:top_k]


class ContextBuilder:
    """
    Builds context from retrieved documents for LLM prompt
    """

    def __init__(self, max_context_length: int = 4000):
        """
        Initialize context builder

        Args:
            max_context_length: Maximum length of context in characters
        """
        self.max_context_length = max_context_length

    def build_context(
        self,
        query: str,
        documents: List[RetrievedDocument],
        include_metadata: bool = True
    ) -> str:
        """
        Build context string from retrieved documents

        Args:
            query: User query
            documents: List of retrieved documents
            include_metadata: Whether to include metadata in context

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."

        context_parts = []
        current_length = 0

        for doc in documents:
            # Format document
            doc_text = f"\n--- Document {doc.rank} (Relevance: {doc.score:.3f}) ---\n"

            if include_metadata and doc.metadata:
                # Add key metadata
                if 'filename' in doc.metadata:
                    doc_text += f"Source: {doc.metadata['filename']}\n"
                if 'document_title' in doc.metadata:
                    doc_text += f"Title: {doc.metadata['document_title']}\n"

            doc_text += f"{doc.text}\n"

            # Check if adding this document exceeds limit
            if current_length + len(doc_text) > self.max_context_length:
                break

            context_parts.append(doc_text)
            current_length += len(doc_text)

        context = "".join(context_parts)

        logger.info(f"Built context from {len(context_parts)} documents ({len(context)} characters)")
        return context

    def build_prompt(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Build complete prompt with context and query

        Args:
            query: User query
            context: Context string
            system_prompt: Optional system prompt

        Returns:
            Complete prompt string
        """
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant. Answer the user's question based on the provided context.
If the answer cannot be found in the context, say so clearly. Be concise and accurate."""

        prompt = f"""{system_prompt}

CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:"""

        return prompt


class RAGRetriever:
    """
    Complete RAG retrieval pipeline
    Combines retrieval and re-ranking
    """

    def __init__(
        self,
        vector_store_manager,
        reranker_type: str = "bm25",  # Options: "bm25", "cross-encoder", "none"
        initial_k: int = 10,
        final_k: int = 5
    ):
        """
        Initialize RAG retriever

        Args:
            vector_store_manager: VectorStoreManager instance
            reranker_type: Type of reranker to use
            initial_k: Number of documents to retrieve initially
            final_k: Number of documents to return after re-ranking
        """
        self.retriever = Retriever(vector_store_manager, top_k=initial_k)
        self.context_builder = ContextBuilder()
        self.final_k = final_k

        # Initialize reranker
        if reranker_type == "bm25":
            self.reranker = BM25Reranker()
        elif reranker_type == "cross-encoder":
            self.reranker = CrossEncoderReranker()
        else:
            self.reranker = None

        logger.info(f"Initialized RAG retriever with {reranker_type} reranker")

    def retrieve_and_rank(
        self,
        query: str,
        filter_metadata: Optional[Dict[str, str]] = None
    ) -> tuple[List[RetrievedDocument], str]:
        """
        Complete retrieval and re-ranking pipeline

        Args:
            query: User query
            filter_metadata: Optional metadata filters

        Returns:
            Tuple of (ranked_documents, context_string)
        """
        # Step 1: Initial retrieval
        documents = self.retriever.retrieve(query, filter_metadata=filter_metadata)

        if not documents:
            logger.warning("No documents retrieved")
            return [], "No relevant information found."

        # Step 2: Re-rank if reranker is available
        if self.reranker:
            documents = self.reranker.rerank(query, documents, top_k=self.final_k)
        else:
            documents = documents[:self.final_k]

        # Step 3: Build context
        context = self.context_builder.build_context(query, documents)

        return documents, context


if __name__ == "__main__":
    # Test retrieval and reranking
    print("Retrieval and re-ranking module loaded successfully")
