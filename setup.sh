#!/bin/bash
# Setup script for RAG Chatbot

echo "======================================"
echo "RAG Chatbot Setup"
echo "======================================"
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo
echo "Installing requirements..."
pip install -r requirements.txt

# Download NLTK data
echo
echo "Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

# Download spaCy model (optional)
echo
echo "Downloading spaCy model (optional, you can skip this)..."
python3 -m spacy download en_core_web_sm || echo "Skipped spaCy model download"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env and add your API keys!"
fi

# Create necessary directories
echo
echo "Creating necessary directories..."
mkdir -p data logs chroma_db

echo
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Edit .env file and add your API keys"
echo "3. Run the chatbot: python main.py --help"
echo
