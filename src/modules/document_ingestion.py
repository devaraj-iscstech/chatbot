"""
Document Ingestion & NLP Preprocessing Module
Handles loading and cleaning of documents (PDF, TXT, CSV, HTML)
"""

import os
import re
import string
from typing import List, Dict, Any
from pathlib import Path
import logging

# Document loaders
import PyPDF2
import pdfplumber
from bs4 import BeautifulSoup
import pandas as pd

# NLP libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentIngestion:
    """Handles document loading and preprocessing"""

    def __init__(self, use_lemmatization: bool = True):
        """
        Initialize the document ingestion module

        Args:
            use_lemmatization: If True, use lemmatization; otherwise use stemming
        """
        self.use_lemmatization = use_lemmatization
        self._download_nltk_resources()

        if use_lemmatization:
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.stemmer = PorterStemmer()

        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            nltk.download('stopwords')
            self.stop_words = set(stopwords.words('english'))

    def _download_nltk_resources(self):
        """Download required NLTK resources"""
        resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                try:
                    nltk.download(resource, quiet=True)
                except:
                    logger.warning(f"Could not download {resource}")

    def load_document(self, file_path: str) -> Dict[str, Any]:
        """
        Load a document and extract its text content

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary containing the extracted text and metadata
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = file_path.suffix.lower()

        # Route to appropriate loader based on file type
        if file_extension == '.pdf':
            text = self._load_pdf(file_path)
        elif file_extension in ['.txt', '.md']:
            text = self._load_text(file_path)
        elif file_extension == '.csv':
            text = self._load_csv(file_path)
        elif file_extension in ['.html', '.htm']:
            text = self._load_html(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        metadata = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_type': file_extension,
            'file_size': file_path.stat().st_size
        }

        logger.info(f"Loaded document: {file_path.name} ({len(text)} characters)")

        return {
            'text': text,
            'metadata': metadata
        }

    def _load_pdf(self, file_path: Path) -> str:
        """Extract text from PDF using pdfplumber (better for complex PDFs)"""
        text_content = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)

        return '\n\n'.join(text_content)

    def _load_text(self, file_path: Path) -> str:
        """Load plain text file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _load_csv(self, file_path: Path) -> str:
        """Load CSV and convert to text"""
        df = pd.read_csv(file_path)
        # Convert dataframe to text representation
        text_parts = []
        for _, row in df.iterrows():
            row_text = ' | '.join([f"{col}: {val}" for col, val in row.items()])
            text_parts.append(row_text)
        return '\n'.join(text_parts)

    def _load_html(self, file_path: Path) -> str:
        """Extract text from HTML"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text()

    def preprocess_text(self, text: str, aggressive: bool = False) -> str:
        """
        Clean and preprocess text using NLP techniques

        Args:
            text: Raw text to preprocess
            aggressive: If True, apply aggressive cleaning (remove stopwords, lemmatization)

        Returns:
            Cleaned and preprocessed text
        """
        # Step 1: Basic cleaning
        text = self._basic_cleaning(text)

        if aggressive:
            # Step 2: Tokenization
            tokens = word_tokenize(text.lower())

            # Step 3: Remove stopwords
            tokens = [t for t in tokens if t not in self.stop_words]

            # Step 4: Remove punctuation
            tokens = [t for t in tokens if t not in string.punctuation]

            # Step 5: Lemmatization or Stemming
            if self.use_lemmatization:
                tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
            else:
                tokens = [self.stemmer.stem(t) for t in tokens]

            # Reconstruct text
            text = ' '.join(tokens)

        return text

    def _basic_cleaning(self, text: str) -> str:
        """
        Perform basic text cleaning

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep periods and basic punctuation
        text = re.sub(r'[^\w\s\.\,\?\!\-\:]', '', text)

        # Remove multiple periods
        text = re.sub(r'\.{2,}', '.', text)

        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove page numbers (common in PDFs)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        return sent_tokenize(text)

    def process_document(self, file_path: str, aggressive_cleaning: bool = False) -> Dict[str, Any]:
        """
        Complete pipeline: Load and preprocess a document

        Args:
            file_path: Path to the document
            aggressive_cleaning: Whether to apply aggressive NLP preprocessing

        Returns:
            Dictionary with processed text and metadata
        """
        # Load document
        doc_data = self.load_document(file_path)

        # Preprocess
        original_text = doc_data['text']
        cleaned_text = self.preprocess_text(original_text, aggressive=aggressive_cleaning)

        return {
            'original_text': original_text,
            'cleaned_text': cleaned_text,
            'metadata': doc_data['metadata']
        }


if __name__ == "__main__":
    # Test the module
    ingestion = DocumentIngestion()

    # Test with a sample text
    sample_text = """
    This is a TEST document!!! It contains various elements like
    URLs (www.example.com), emails (test@example.com), and special characters @#$%.
    We want to clean this text properly.
    """

    cleaned = ingestion.preprocess_text(sample_text, aggressive=False)
    print("Cleaned Text:", cleaned)
