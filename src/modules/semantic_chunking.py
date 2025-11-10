"""
Semantic Chunking Module
Splits text into meaningful chunks while preserving context and semantic integrity
"""

import re
import uuid
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass, field

import nltk
from nltk.tokenize import sent_tokenize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a semantic text chunk with metadata"""
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_char: int = 0
    end_char: int = 0
    chunk_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary"""
        return {
            'chunk_id': self.chunk_id,
            'text': self.text,
            'metadata': self.metadata,
            'start_char': self.start_char,
            'end_char': self.end_char,
            'chunk_index': self.chunk_index
        }


class SemanticChunker:
    """
    Advanced text chunking that preserves semantic meaning
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100,
        respect_sentence_boundary: bool = True
    ):
        """
        Initialize semantic chunker

        Args:
            chunk_size: Target size for each chunk (in characters)
            chunk_overlap: Number of characters to overlap between chunks
            min_chunk_size: Minimum chunk size to avoid very small chunks
            respect_sentence_boundary: If True, don't split sentences across chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.respect_sentence_boundary = respect_sentence_boundary

        # Ensure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """
        Split text into semantic chunks

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to all chunks

        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []

        if metadata is None:
            metadata = {}

        # Use sentence-aware chunking if enabled
        if self.respect_sentence_boundary:
            return self._chunk_by_sentences(text, metadata)
        else:
            return self._chunk_by_size(text, metadata)

    def _chunk_by_sentences(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[TextChunk]:
        """
        Chunk text by sentences to preserve semantic boundaries

        Args:
            text: Text to chunk
            metadata: Metadata to attach

        Returns:
            List of TextChunk objects
        """
        # Split into sentences
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        char_position = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds chunk_size, save current chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = ' '.join(current_chunk)
                start_char = char_position - current_length
                end_char = char_position

                chunk = TextChunk(
                    text=chunk_text,
                    metadata=metadata.copy(),
                    start_char=start_char,
                    end_char=end_char,
                    chunk_index=len(chunks)
                )
                chunks.append(chunk)

                # Handle overlap: keep last few sentences for context
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk) + len(current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length + 1  # +1 for space
            char_position += sentence_length + 1

        # Add remaining sentences as final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                start_char = char_position - current_length
                chunk = TextChunk(
                    text=chunk_text,
                    metadata=metadata.copy(),
                    start_char=start_char,
                    end_char=char_position,
                    chunk_index=len(chunks)
                )
                chunks.append(chunk)

        logger.info(f"Created {len(chunks)} semantic chunks from text")
        return chunks

    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """
        Get sentences for overlap based on overlap size

        Args:
            sentences: List of sentences

        Returns:
            List of sentences for overlap
        """
        overlap_text = ''
        overlap_sentences = []

        # Take sentences from the end until we reach overlap size
        for sentence in reversed(sentences):
            if len(overlap_text) + len(sentence) <= self.chunk_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_text = ' '.join(overlap_sentences)
            else:
                break

        return overlap_sentences

    def _chunk_by_size(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[TextChunk]:
        """
        Simple chunking by character size with overlap

        Args:
            text: Text to chunk
            metadata: Metadata to attach

        Returns:
            List of TextChunk objects
        """
        chunks = []
        start = 0
        text_length = len(text)
        chunk_index = 0

        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size

            # Extract chunk
            chunk_text = text[start:end].strip()

            if len(chunk_text) >= self.min_chunk_size:
                chunk = TextChunk(
                    text=chunk_text,
                    metadata=metadata.copy(),
                    start_char=start,
                    end_char=end,
                    chunk_index=chunk_index
                )
                chunks.append(chunk)
                chunk_index += 1

            # Move start position considering overlap
            start = end - self.chunk_overlap

        logger.info(f"Created {len(chunks)} size-based chunks from text")
        return chunks

    def chunk_by_sections(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        section_pattern: str = r'\n\n+'
    ) -> List[TextChunk]:
        """
        Chunk text by sections (e.g., paragraphs)

        Args:
            text: Text to chunk
            metadata: Metadata to attach
            section_pattern: Regex pattern to identify section boundaries

        Returns:
            List of TextChunk objects
        """
        if metadata is None:
            metadata = {}

        # Split by sections
        sections = re.split(section_pattern, text)
        chunks = []
        char_position = 0

        for idx, section in enumerate(sections):
            section = section.strip()

            if len(section) < self.min_chunk_size:
                # Skip very small sections or merge with previous
                if chunks:
                    # Merge with previous chunk
                    chunks[-1].text += f"\n\n{section}"
                    chunks[-1].end_char = char_position + len(section)
                char_position += len(section)
                continue

            # If section is too large, split it further
            if len(section) > self.chunk_size:
                sub_chunks = self._chunk_by_sentences(section, metadata)
                for sub_chunk in sub_chunks:
                    sub_chunk.chunk_index = len(chunks)
                    sub_chunk.start_char += char_position
                    sub_chunk.end_char += char_position
                    sub_chunk.metadata['section_index'] = idx
                    chunks.append(sub_chunk)
            else:
                chunk = TextChunk(
                    text=section,
                    metadata={**metadata, 'section_index': idx},
                    start_char=char_position,
                    end_char=char_position + len(section),
                    chunk_index=len(chunks)
                )
                chunks.append(chunk)

            char_position += len(section)

        logger.info(f"Created {len(chunks)} section-based chunks")
        return chunks

    def add_context_to_chunks(self, chunks: List[TextChunk], document_title: str = None):
        """
        Add additional context metadata to chunks

        Args:
            chunks: List of chunks to enhance
            document_title: Title of the source document
        """
        total_chunks = len(chunks)

        for idx, chunk in enumerate(chunks):
            # Add position information
            chunk.metadata['chunk_position'] = f"{idx + 1}/{total_chunks}"
            chunk.metadata['is_first_chunk'] = (idx == 0)
            chunk.metadata['is_last_chunk'] = (idx == total_chunks - 1)

            # Add document title if provided
            if document_title:
                chunk.metadata['document_title'] = document_title

            # Add chunk statistics
            chunk.metadata['chunk_length'] = len(chunk.text)
            chunk.metadata['word_count'] = len(chunk.text.split())


if __name__ == "__main__":
    # Test the chunker
    chunker = SemanticChunker(chunk_size=200, chunk_overlap=50)

    sample_text = """
    Artificial Intelligence (AI) is transforming the world. Machine learning is a subset of AI.
    It enables systems to learn from data. Deep learning uses neural networks.

    Natural Language Processing (NLP) is another important field. It helps computers understand human language.
    Applications include chatbots and translation systems. The field is rapidly evolving.

    Computer vision enables machines to interpret visual information. It's used in autonomous vehicles.
    Facial recognition is another application. The technology continues to improve.
    """

    chunks = chunker.chunk_text(sample_text, metadata={'source': 'test'})

    print(f"\nCreated {len(chunks)} chunks:\n")
    for chunk in chunks:
        print(f"Chunk {chunk.chunk_index}:")
        print(f"Text: {chunk.text[:100]}...")
        print(f"Length: {len(chunk.text)}")
        print(f"Metadata: {chunk.metadata}\n")
