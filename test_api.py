#!/usr/bin/env python3
"""
Python script to test RAG Chatbot API endpoints
"""

import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"{'='*60}\n")


def test_health():
    """Test health check endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_config():
    """Test configuration endpoint"""
    print("Testing /config endpoint...")
    response = requests.get(f"{API_URL}/config")
    print_response("Configuration", response)
    return response.status_code == 200


def test_stats():
    """Test stats endpoint"""
    print("Testing /stats endpoint...")
    response = requests.get(f"{API_URL}/stats")
    print_response("Statistics", response)
    return response.status_code == 200


def test_ingest_from_path(file_path):
    """Test ingesting document from path"""
    print(f"Testing /ingest/path with {file_path}...")
    response = requests.post(
        f"{API_URL}/ingest/path",
        json={"file_path": file_path}
    )
    print_response(f"Ingest from Path: {file_path}", response)
    return response.status_code == 200


def test_query(question, use_memory=False, return_sources=True):
    """Test query endpoint"""
    print(f"Testing /query with question: {question[:50]}...")
    response = requests.post(
        f"{API_URL}/query",
        json={
            "question": question,
            "use_memory": use_memory,
            "return_sources": return_sources
        }
    )
    print_response(f"Query: {question}", response)
    return response.status_code == 200


def test_list_documents():
    """Test list documents endpoint"""
    print("Testing /documents endpoint...")
    response = requests.get(f"{API_URL}/documents")
    print_response("List Documents", response)
    return response.status_code == 200


def test_upload_file(file_path):
    """Test file upload endpoint"""
    print(f"Testing /ingest/upload with {file_path}...")

    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False

    with open(file_path, 'rb') as f:
        files = {'file': (Path(file_path).name, f)}
        response = requests.post(
            f"{API_URL}/ingest/upload",
            files=files
        )

    print_response(f"Upload File: {file_path}", response)
    return response.status_code == 200


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("RAG Chatbot API Test Suite")
    print("="*60)

    results = {}

    # Test 1: Health Check
    results['health'] = test_health()

    # Test 2: Configuration
    results['config'] = test_config()

    # Test 3: Stats (before ingestion)
    results['stats_before'] = test_stats()

    # Test 4: Ingest Documents
    print("\n--- Testing Document Ingestion ---")

    # Try to ingest TheUdyog documents
    pdf_files = [
        "TheUdyog Brochure.pdf",
        "TheUdyog Presentation.pdf"
    ]

    for pdf in pdf_files:
        if Path(pdf).exists():
            results[f'ingest_{pdf}'] = test_ingest_from_path(pdf)
        else:
            print(f"⚠️ Skipping {pdf} - file not found")

    # Test 5: Stats (after ingestion)
    results['stats_after'] = test_stats()

    # Test 6: List Documents
    results['list_docs'] = test_list_documents()

    # Test 7: Query
    print("\n--- Testing Query Endpoints ---")

    test_questions = [
        "What is TheUdyog?",
        "What services does TheUdyog provide?",
        "Tell me about the features"
    ]

    for question in test_questions:
        results[f'query_{question[:20]}'] = test_query(question)

    # Test 8: Query with memory
    print("\n--- Testing Query with Memory ---")
    test_query("What is TheUdyog?", use_memory=True)
    test_query("Tell me more about it", use_memory=True)  # Context-aware

    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server.")
        print("Make sure the API server is running:")
        print("  python api.py")
        print("or")
        print("  uvicorn api:app --reload")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
