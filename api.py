"""
FastAPI Backend for RAG Chatbot
Provides REST API endpoints for document ingestion and querying
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import sys
from pathlib import Path
import logging
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_chatbot import RAGChatbot
from utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation Chatbot API with Google AI (Gemini)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chatbot instance
chatbot: Optional[RAGChatbot] = None

# Pydantic models for request/response
class QueryRequest(BaseModel):
    question: str
    use_memory: bool = False
    return_sources: bool = False

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None

class IngestRequest(BaseModel):
    file_path: str

class IngestResponse(BaseModel):
    filename: str
    chunks_created: int
    status: str

class StatsResponse(BaseModel):
    collection_name: str
    total_documents: int
    embedding_dimension: int
    conversation_history_length: int

class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    llm_model: str
    embedding_provider: str


# Initialize chatbot
@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup"""
    global chatbot
    try:
        logger.info("Initializing RAG Chatbot...")
        chatbot = RAGChatbot(
            embedding_provider=Config.EMBEDDING_PROVIDER,
            llm_provider=Config.LLM_PROVIDER,
            llm_model=Config.LLM_MODEL,
            reranker_type=Config.RERANKER_TYPE
        )
        logger.info("✅ RAG Chatbot initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")
        raise


# Health check endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm_provider": Config.LLM_PROVIDER,
        "llm_model": Config.LLM_MODEL,
        "embedding_provider": Config.EMBEDDING_PROVIDER
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    return {
        "status": "healthy",
        "llm_provider": Config.LLM_PROVIDER,
        "llm_model": Config.LLM_MODEL,
        "embedding_provider": Config.EMBEDDING_PROVIDER
    }


# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_chatbot(request: QueryRequest):
    """
    Query the chatbot with a question

    Args:
        request: QueryRequest with question and options

    Returns:
        QueryResponse with answer and optional sources
    """
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    try:
        logger.info(f"Received query: {request.question[:50]}...")

        result = chatbot.query(
            question=request.question,
            use_memory=request.use_memory,
            return_sources=request.return_sources
        )

        return QueryResponse(
            question=result['question'],
            answer=result['answer'],
            sources=result.get('sources')
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Ingest document from file path
@app.post("/ingest/path", response_model=IngestResponse)
async def ingest_from_path(request: IngestRequest):
    """
    Ingest a document from file path

    Args:
        request: IngestRequest with file path

    Returns:
        IngestResponse with ingestion results
    """
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    file_path = Path(request.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

    try:
        logger.info(f"Ingesting document: {file_path.name}")
        num_chunks = chatbot.ingest_document(str(file_path))

        return IngestResponse(
            filename=file_path.name,
            chunks_created=num_chunks,
            status="success"
        )

    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Upload and ingest document
@app.post("/ingest/upload", response_model=IngestResponse)
async def ingest_uploaded_file(file: UploadFile = File(...)):
    """
    Upload and ingest a document

    Args:
        file: Uploaded file

    Returns:
        IngestResponse with ingestion results
    """
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    # Validate file type
    allowed_extensions = {'.pdf', '.txt', '.csv', '.html', '.md'}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )

    # Save uploaded file temporarily
    upload_dir = Path("./uploads")
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / file.filename

    try:
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Uploaded and saved: {file.filename}")

        # Ingest document
        num_chunks = chatbot.ingest_document(str(file_path))

        return IngestResponse(
            filename=file.filename,
            chunks_created=num_chunks,
            status="success"
        )

    except Exception as e:
        logger.error(f"Error ingesting uploaded file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()


# Get system statistics
@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get chatbot system statistics

    Returns:
        StatsResponse with system stats
    """
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    try:
        stats = chatbot.get_stats()
        return StatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Clear conversation memory
@app.post("/memory/clear")
async def clear_memory():
    """Clear conversation memory"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    try:
        chatbot.conversation_memory.clear_history()
        return {"status": "success", "message": "Conversation memory cleared"}

    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get conversation history
@app.get("/memory/history")
async def get_conversation_history():
    """Get conversation history"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    try:
        history = chatbot.conversation_memory.get_history()
        return {"history": history}

    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# List available documents
@app.get("/documents")
async def list_documents():
    """List all indexed documents"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    try:
        documents = chatbot.vector_store_manager.vector_store.get_all_documents(limit=100)

        # Group by filename
        doc_info = {}
        for doc in documents:
            filename = doc['metadata'].get('filename', 'Unknown')
            if filename not in doc_info:
                doc_info[filename] = {'filename': filename, 'chunk_count': 0}
            doc_info[filename]['chunk_count'] += 1

        return {"documents": list(doc_info.values())}

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Configuration endpoint
@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "llm_provider": Config.LLM_PROVIDER,
        "llm_model": Config.LLM_MODEL,
        "embedding_provider": Config.EMBEDDING_PROVIDER,
        "embedding_model": Config.EMBEDDING_MODEL,
        "chunk_size": Config.CHUNK_SIZE,
        "chunk_overlap": Config.CHUNK_OVERLAP,
        "top_k_retrieval": Config.TOP_K_RETRIEVAL,
        "top_k_rerank": Config.TOP_K_RERANK,
        "reranker_type": Config.RERANKER_TYPE,
        "temperature": Config.TEMPERATURE,
        "max_tokens": Config.MAX_TOKENS
    }


if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
