# RAG Chatbot - Improvements & Roadmap

**Current Rating: 6.5/10**
**Target Rating: 9.5/10**

---

## Table of Contents

- [1. Error Handling & Resilience](#1-error-handling--resilience)
- [2. Security Vulnerabilities](#2-security-vulnerabilities)
- [3. Performance & Scalability](#3-performance--scalability)
- [4. Monitoring & Observability](#4-monitoring--observability)
- [5. Testing & Quality](#5-testing--quality)
- [6. Configuration & Deployment](#6-configuration--deployment)
- [7. Data Management](#7-data-management)
- [8. API Improvements](#8-api-improvements)
- [9. User Experience](#9-user-experience)
- [10. Documentation](#10-documentation)
- [Priority Roadmap](#priority-roadmap)

---

## 1. Error Handling & Resilience

**Current Score: 4/10 → Target: 9/10**

### Critical Issues
- ❌ No retry logic for API calls (LLM, embeddings)
- ❌ Bare exception catches in `vector_store.py:59, 63`
- ❌ No circuit breakers for external service failures
- ❌ No graceful degradation when components fail
- ❌ Missing input validation for user queries and file uploads

### Improvements

#### 1.1 Add Retry Logic with Exponential Backoff
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def generate_embedding(self, text: str) -> List[float]:
    """Generate embedding with automatic retry"""
    try:
        return self.model.encode(text)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise
```

**Files to modify:**
- `src/modules/embeddings.py`
- `src/modules/llm_integration.py`

#### 1.2 Add Input Validation
```python
from pydantic import validator, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)
    use_memory: bool = False
    return_sources: bool = False

    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError("Question cannot be empty or whitespace")
        # Sanitize for prompt injection
        if any(suspicious in v.lower() for suspicious in ['ignore previous', 'system:', 'assistant:']):
            raise ValueError("Potentially malicious input detected")
        return v.strip()
```

**Files to modify:**
- `api.py`

#### 1.3 Add Circuit Breaker Pattern
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_llm_api(self, prompt: str) -> str:
    """Call LLM with circuit breaker protection"""
    return self.llm.generate(prompt)
```

**New dependency:** `circuitbreaker==1.4.0`

#### 1.4 Replace Bare Exceptions
```python
# ❌ Before (vector_store.py:59)
except:
    pass

# ✅ After
except ValueError as e:
    logger.warning(f"Collection not found: {e}")
except Exception as e:
    logger.error(f"Unexpected error deleting collection: {e}")
    raise
```

**Files to modify:**
- `src/modules/vector_store.py`

---

## 2. Security Vulnerabilities

**Current Score: 3/10 → Target: 9/10**

### Critical Issues
- ❌ No authentication/authorization
- ❌ No rate limiting
- ❌ CORS set to allow all origins (`api.py:38`)
- ❌ API keys exposed in environment (no secret management)
- ❌ Weak file upload validation (only checks extension)
- ❌ No input sanitization for prompt injection
- ❌ Uploaded files not scanned for malware

### Improvements

#### 2.1 Add API Authentication (JWT)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/query")
async def query_chatbot(
    request: QueryRequest,
    username: str = Depends(verify_token)
):
    """Protected endpoint"""
    pass
```

**New files:**
- `src/auth.py` - Authentication logic
- `src/middleware/auth.py` - Auth middleware

**New dependencies:**
- `python-jose[cryptography]==3.3.0`
- `passlib[bcrypt]==1.7.4`

#### 2.2 Add Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/query")
@limiter.limit("10/minute")
async def query_chatbot(request: Request, query: QueryRequest):
    """Rate limited query endpoint"""
    pass
```

**New dependency:** `slowapi==0.1.9`

**Files to modify:**
- `api.py`

#### 2.3 Fix CORS Configuration
```python
# ❌ Before (api.py:38)
allow_origins=["*"]

# ✅ After
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
    max_age=3600
)
```

**Files to modify:**
- `api.py`

#### 2.4 Strict File Validation
```python
import magic
import hashlib

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'text/plain',
    'text/csv',
    'text/html',
    'text/markdown'
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

async def validate_uploaded_file(file: UploadFile):
    """Strict file validation"""
    # Check file size
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB)")

    # Check actual MIME type (not extension)
    content = await file.read(1024)
    file.file.seek(0)
    mime_type = magic.from_buffer(content, mime=True)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"Invalid file type: {mime_type}")

    # Check for malicious content patterns
    if b'<?php' in content or b'<script>' in content:
        raise HTTPException(400, "Potentially malicious file content")

    return True
```

**New dependency:** `python-magic==0.4.27`

**Files to modify:**
- `api.py`

#### 2.5 Add Secret Management
```python
# Use environment-specific secret management
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class SecretManager:
    def __init__(self):
        if os.getenv("ENVIRONMENT") == "production":
            # Use Azure Key Vault or AWS Secrets Manager
            credential = DefaultAzureCredential()
            self.client = SecretClient(
                vault_url=os.getenv("KEY_VAULT_URL"),
                credential=credential
            )
        else:
            # Use .env for local development
            self.client = None

    def get_secret(self, name: str) -> str:
        if self.client:
            return self.client.get_secret(name).value
        return os.getenv(name)
```

**New file:** `src/utils/secrets.py`

#### 2.6 Sanitize Inputs (Prevent Prompt Injection)
```python
import re

SUSPICIOUS_PATTERNS = [
    r'ignore\s+previous',
    r'system:',
    r'assistant:',
    r'<\|im_start\|>',
    r'<\|im_end\|>',
    r'\[INST\]',
    r'\[/INST\]'
]

def sanitize_query(query: str) -> str:
    """Sanitize query to prevent prompt injection"""
    # Check for suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError(f"Potentially malicious input pattern detected")

    # Limit special characters
    if query.count('{') > 5 or query.count('[') > 5:
        raise ValueError("Too many special characters")

    # Remove control characters
    query = re.sub(r'[\x00-\x1F\x7F]', '', query)

    return query.strip()
```

**New file:** `src/utils/sanitization.py`

---

## 3. Performance & Scalability

**Current Score: 5/10 → Target: 9/10**

### Critical Issues
- ❌ No caching for embeddings or responses
- ❌ Blocking I/O operations not made async
- ❌ No connection pooling for database
- ❌ Documents loaded entirely into memory
- ❌ No batch processing for large document sets
- ❌ No pagination for results

### Improvements

#### 3.1 Add Redis Caching
```python
import redis
import hashlib
import json
from functools import wraps

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def cache_response(ttl: int = 3600):
    """Cache decorator for responses"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hashlib.md5(str(kwargs).encode()).hexdigest()}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit: {cache_key}")
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

@cache_response(ttl=1800)
async def query_chatbot(question: str):
    """Cached query endpoint"""
    pass
```

**New file:** `src/cache/redis_cache.py`

**New dependency:** `redis==5.0.1`

**Add to docker-compose.yml:**
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

#### 3.2 Make Operations Async
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class EmbeddingGenerator:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def generate_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """Async embedding generation"""
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            self.executor,
            self._generate_embeddings_sync,
            texts
        )
        return embeddings

    def _generate_embeddings_sync(self, texts: List[str]) -> List[List[float]]:
        """Sync implementation"""
        return self.model.encode(texts)
```

**Files to modify:**
- `src/modules/embeddings.py`
- `src/modules/llm_integration.py`

#### 3.3 Add Batch Processing
```python
async def ingest_documents_batch(
    files: List[str],
    batch_size: int = 10,
    background_tasks: BackgroundTasks = None
):
    """Process documents in batches"""
    total_chunks = 0

    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{len(files)//batch_size + 1}")

        # Process batch in parallel
        tasks = [ingest_document_async(file) for file in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful ingestions
        for result in results:
            if isinstance(result, int):
                total_chunks += result
            else:
                logger.error(f"Batch processing error: {result}")

    return total_chunks
```

**Files to modify:**
- `src/rag_chatbot.py`

#### 3.4 Add Pagination
```python
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

@app.get("/documents", response_model=PaginatedResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Paginated document list"""
    offset = (page - 1) * page_size

    total = chatbot.vector_store_manager.vector_store.collection.count()
    documents = chatbot.vector_store_manager.vector_store.get_all_documents(
        limit=page_size,
        offset=offset
    )

    return PaginatedResponse(
        items=documents,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )
```

**Files to modify:**
- `api.py`

#### 3.5 Add Connection Pooling
```python
# For ChromaDB, use persistent client with connection pooling
import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory
            )
        )
```

**Files to modify:**
- `src/modules/vector_store.py`

#### 3.6 Add Streaming Responses
```python
from fastapi.responses import StreamingResponse

@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    """Stream response chunks"""
    async def generate():
        # Retrieve context
        documents, context = chatbot.retriever.retrieve_and_rank(request.question)

        # Stream LLM response
        async for chunk in chatbot.response_generator.generate_stream(
            query=request.question,
            context=context
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Files to modify:**
- `api.py`
- `src/modules/llm_integration.py`

---

## 4. Monitoring & Observability

**Current Score: 2/10 → Target: 9/10**

### Critical Issues
- ❌ No metrics collection (latency, throughput, errors)
- ❌ No distributed tracing
- ❌ No health checks for dependencies
- ❌ Logs lack context (request IDs, user IDs)
- ❌ No alerting on failures

### Improvements

#### 4.1 Add Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app

# Define metrics
query_counter = Counter('chatbot_queries_total', 'Total number of queries', ['status'])
query_latency = Histogram('chatbot_query_latency_seconds', 'Query processing time')
embedding_latency = Histogram('chatbot_embedding_latency_seconds', 'Embedding generation time')
active_requests = Gauge('chatbot_active_requests', 'Number of active requests')
error_counter = Counter('chatbot_errors_total', 'Total errors', ['error_type'])

# Instrument code
@query_latency.time()
async def query_chatbot(request: QueryRequest):
    active_requests.inc()
    try:
        result = chatbot.query(request.question)
        query_counter.labels(status='success').inc()
        return result
    except Exception as e:
        query_counter.labels(status='error').inc()
        error_counter.labels(error_type=type(e).__name__).inc()
        raise
    finally:
        active_requests.dec()

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**New file:** `src/monitoring/metrics.py`

**New dependency:** `prometheus-client==0.19.0`

#### 4.2 Add OpenTelemetry Tracing
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracing
resource = Resource.create({"service.name": "rag-chatbot"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(JaegerExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Use in code
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("query_processing")
async def query_chatbot(question: str):
    span = trace.get_current_span()
    span.set_attribute("question_length", len(question))
    span.set_attribute("user_id", user_id)

    with tracer.start_as_current_span("retrieve_documents"):
        documents = retriever.retrieve(question)

    with tracer.start_as_current_span("generate_response"):
        response = generator.generate(question, documents)

    return response
```

**New file:** `src/monitoring/tracing.py`

**New dependencies:**
- `opentelemetry-api==1.21.0`
- `opentelemetry-sdk==1.21.0`
- `opentelemetry-instrumentation-fastapi==0.42b0`
- `opentelemetry-exporter-jaeger==1.21.0`

#### 4.3 Structured Logging
```python
import structlog
from contextvars import ContextVar

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

logger = structlog.get_logger()

# Middleware to add request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Use in code
logger.info("query_processed",
    user_id=user_id,
    duration_ms=duration,
    status="success",
    sources_count=len(sources)
)
```

**New file:** `src/logging/structured_logging.py`

**New dependency:** `structlog==23.2.0`

#### 4.4 Health Check Endpoints
```python
from typing import Dict, Any
from enum import Enum

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck(BaseModel):
    status: HealthStatus
    checks: Dict[str, Any]
    timestamp: datetime

async def check_chromadb() -> Dict[str, Any]:
    """Check ChromaDB health"""
    try:
        count = chatbot.vector_store_manager.vector_store.collection.count()
        return {
            "status": "healthy",
            "document_count": count,
            "latency_ms": 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

async def check_llm_connection() -> Dict[str, Any]:
    """Check LLM API health"""
    try:
        start = time.time()
        # Simple test query
        result = chatbot.response_generator.generate_response(
            query="test",
            context="test"
        )
        latency = (time.time() - start) * 1000
        return {
            "status": "healthy",
            "latency_ms": latency
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/health/live")
async def liveness_check():
    """Liveness probe - is the app running?"""
    return {"status": "healthy"}

@app.get("/health/ready", response_model=HealthCheck)
async def readiness_check():
    """Readiness probe - is the app ready to serve traffic?"""
    checks = {
        "vector_db": await check_chromadb(),
        "llm": await check_llm_connection(),
        "redis": await check_redis()
    }

    # Determine overall status
    unhealthy = any(c["status"] == "unhealthy" for c in checks.values())
    status = HealthStatus.UNHEALTHY if unhealthy else HealthStatus.HEALTHY

    return HealthCheck(
        status=status,
        checks=checks,
        timestamp=datetime.now()
    )
```

**New file:** `src/health/checks.py`

---

## 5. Testing & Quality

**Current Score: 1/10 → Target: 9/10**

### Critical Issues
- ❌ No unit tests
- ❌ No integration tests
- ❌ No load testing
- ❌ No code coverage tracking
- ❌ No type checking enforced

### Improvements

#### 5.1 Add Unit Tests
```python
# tests/test_retrieval.py
import pytest
from src.modules.retrieval import Retriever, BM25Reranker, RetrievedDocument

@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing"""
    pass

@pytest.fixture
def sample_documents():
    return [
        RetrievedDocument(
            text="Machine learning is AI",
            metadata={"source": "test"},
            score=0.9,
            doc_id="doc1"
        )
    ]

def test_retriever_returns_documents(mock_vector_store):
    retriever = Retriever(mock_vector_store, top_k=5)
    docs = retriever.retrieve("test query")

    assert len(docs) > 0
    assert all(isinstance(d, RetrievedDocument) for d in docs)
    assert all(d.score >= 0 and d.score <= 1 for d in docs)

def test_bm25_reranker(sample_documents):
    reranker = BM25Reranker()
    reranked = reranker.rerank("machine learning", sample_documents, top_k=1)

    assert len(reranked) == 1
    assert reranked[0].rank == 1

def test_empty_document_list():
    reranker = BM25Reranker()
    result = reranker.rerank("query", [], top_k=5)
    assert result == []
```

**New directory:** `tests/`

**Files to create:**
- `tests/conftest.py` - Pytest configuration
- `tests/test_retrieval.py`
- `tests/test_embeddings.py`
- `tests/test_vector_store.py`
- `tests/test_llm_integration.py`
- `tests/test_api.py`

#### 5.2 Add Integration Tests
```python
# tests/integration/test_end_to_end.py
import pytest
from httpx import AsyncClient
from api import app

@pytest.mark.integration
@pytest.mark.asyncio
async def test_document_ingestion_and_query():
    """Test complete flow: ingest → query → response"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Ingest document
        files = {"file": ("test.txt", b"Machine learning content", "text/plain")}
        response = await client.post("/ingest/upload", files=files)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 2. Query chatbot
        response = await client.post(
            "/query",
            json={"question": "What is machine learning?", "return_sources": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert len(data["sources"]) > 0

@pytest.mark.integration
async def test_rate_limiting():
    """Test rate limiting works"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make multiple requests
        for _ in range(15):
            response = await client.post("/query", json={"question": "test"})

        # Should hit rate limit
        assert response.status_code == 429
```

#### 5.3 Add Property-Based Tests
```python
# tests/test_properties.py
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=1000))
def test_sanitize_handles_any_text(query):
    """Sanitization should handle any text without crashing"""
    try:
        result = sanitize_query(query)
        assert isinstance(result, str)
    except ValueError:
        # Expected for malicious inputs
        pass

@given(
    st.lists(st.text(min_size=10, max_size=500), min_size=1, max_size=10)
)
def test_embedding_dimensions_consistent(texts):
    """All embeddings should have same dimension"""
    generator = EmbeddingGenerator()
    embeddings = generator.generate_embeddings(texts)

    dimensions = [len(emb) for emb in embeddings]
    assert len(set(dimensions)) == 1  # All same dimension
```

**New dependency:** `hypothesis==6.92.1`

#### 5.4 Add Load Testing
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class ChatbotUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def query_chatbot(self):
        """Simulate user queries"""
        self.client.post("/query", json={
            "question": "What is machine learning?",
            "return_sources": False
        })

    @task(1)
    def get_stats(self):
        """Check system stats"""
        self.client.get("/stats")

    @task(1)
    def health_check(self):
        """Check health"""
        self.client.get("/health")

# Run with: locust -f tests/load/locustfile.py --host=http://localhost:8000
```

**New dependency:** `locust==2.20.0`

#### 5.5 Add Code Coverage
```bash
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    pytest --cov=src --cov-report=html --cov-report=term --cov-report=xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

**New dependency:** `pytest-cov==4.1.0`

#### 5.6 Add Type Checking
```bash
# mypy.ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_calls = True
```

**Add to CI:**
```bash
- name: Type check
  run: mypy src/
```

**New dependency:** `mypy==1.7.1`

---

## 6. Configuration & Deployment

**Current Score: 5/10 → Target: 9/10**

### Critical Issues
- ❌ Hardcoded configuration values
- ❌ No environment-specific configs
- ❌ No configuration validation
- ❌ No Docker/container setup
- ❌ No CI/CD pipeline

### Improvements

#### 6.1 Use Pydantic for Config Validation
```python
# src/config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Security
    jwt_secret_key: str = Field(..., min_length=32)
    allowed_origins: list[str] = ["http://localhost:3000"]
    rate_limit_per_minute: int = 60

    # LLM
    llm_provider: str = "google"
    llm_model: str = "gemini-2.5-pro"
    llm_temperature: float = Field(0.7, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(1000, ge=1, le=100000)

    # Embeddings
    embedding_provider: str = "sentence-transformers"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector Store
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "rag_documents"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Performance
    max_query_length: int = 5000
    max_file_size_mb: int = 50
    batch_size: int = 10
    cache_ttl_seconds: int = 3600

    @validator('llm_provider')
    def validate_llm_provider(cls, v):
        allowed = ['google', 'openai', 'anthropic', 'local']
        if v not in allowed:
            raise ValueError(f"LLM provider must be one of {allowed}")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Singleton instance
settings = Settings()
```

**Files to modify:**
- Replace `src/utils/config.py` with `src/config/settings.py`

#### 6.2 Create Dockerfile
```dockerfile
# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Run application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 6.3 Create Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_HOST=redis
      - CHROMA_PERSIST_DIRECTORY=/data/chroma
    volumes:
      - ./data:/data
      - ./uploads:/app/uploads
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
```

#### 6.4 Add CI/CD Pipeline
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov mypy

    - name: Lint with flake8
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

    - name: Type check with mypy
      run: mypy src/

    - name: Run unit tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Security scan with bandit
      run: |
        pip install bandit
        bandit -r src/ -f json -o bandit-report.json

    - name: Dependency check
      run: |
        pip install safety
        safety check --json

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        push: true
        tags: yourusername/rag-chatbot:latest
        cache-from: type=registry,ref=yourusername/rag-chatbot:buildcache
        cache-to: type=registry,ref=yourusername/rag-chatbot:buildcache,mode=max
```

---

## 7. Data Management

**Current Score: 5/10 → Target: 9/10**

### Critical Issues
- ❌ No document versioning
- ❌ No backup/restore mechanism
- ❌ No data migration strategy
- ❌ No duplicate detection
- ❌ No document deletion API
- ❌ Vector DB not optimized (no index tuning)

### Improvements

#### 7.1 Add Document Versioning
```python
# src/models/document.py
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class DocumentVersion:
    document_id: str
    version: int
    content_hash: str
    created_at: datetime
    metadata: dict

class DocumentVersionManager:
    def __init__(self, db_path: str):
        self.versions: Dict[str, List[DocumentVersion]] = {}

    def compute_hash(self, content: str) -> str:
        """Compute content hash"""
        return hashlib.sha256(content.encode()).hexdigest()

    def is_duplicate(self, content_hash: str) -> bool:
        """Check if document already exists"""
        for versions in self.versions.values():
            if any(v.content_hash == content_hash for v in versions):
                return True
        return False

    def add_version(self, doc_id: str, content: str, metadata: dict):
        """Add new version of document"""
        content_hash = self.compute_hash(content)

        if self.is_duplicate(content_hash):
            return None  # Skip duplicate

        if doc_id not in self.versions:
            self.versions[doc_id] = []

        version = DocumentVersion(
            document_id=doc_id,
            version=len(self.versions[doc_id]) + 1,
            content_hash=content_hash,
            created_at=datetime.now(),
            metadata=metadata
        )

        self.versions[doc_id].append(version)
        return version
```

**New file:** `src/models/document.py`

#### 7.2 Add Backup/Restore
```python
# src/admin/backup.py
import shutil
from datetime import datetime
from pathlib import Path
import tarfile

class BackupManager:
    def __init__(self, chroma_path: str, backup_dir: str):
        self.chroma_path = Path(chroma_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self) -> str:
        """Create backup of vector database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"chroma_backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.tar.gz"

        # Create tar archive
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(self.chroma_path, arcname="chroma_db")

        logger.info(f"Backup created: {backup_path}")
        return str(backup_path)

    def restore_backup(self, backup_path: str):
        """Restore from backup"""
        # Extract tar archive
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(self.chroma_path.parent)

        logger.info(f"Restored from backup: {backup_path}")

    def list_backups(self) -> List[dict]:
        """List available backups"""
        backups = []
        for backup_file in self.backup_dir.glob("chroma_backup_*.tar.gz"):
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size_mb": backup_file.stat().st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(backup_file.stat().st_mtime)
            })
        return sorted(backups, key=lambda x: x["created"], reverse=True)

# API endpoints
@app.post("/admin/backup")
async def create_backup(background_tasks: BackgroundTasks):
    """Create database backup"""
    backup_manager = BackupManager(Config.CHROMA_PATH, "./backups")
    backup_path = backup_manager.create_backup()
    return {"status": "success", "backup_path": backup_path}

@app.get("/admin/backups")
async def list_backups():
    """List available backups"""
    backup_manager = BackupManager(Config.CHROMA_PATH, "./backups")
    return {"backups": backup_manager.list_backups()}
```

**New file:** `src/admin/backup.py`

#### 7.3 Add Document Deletion
```python
# Add to vector_store.py
def delete_document(self, doc_id: str) -> bool:
    """Delete document by ID"""
    try:
        self.collection.delete(ids=[doc_id])
        logger.info(f"Deleted document: {doc_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return False

def delete_by_metadata(self, metadata_filter: Dict[str, str]) -> int:
    """Delete documents matching metadata filter"""
    try:
        # Get matching documents
        results = self.collection.get(where=metadata_filter)
        ids = results['ids']

        if ids:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")

        return len(ids)
    except Exception as e:
        logger.error(f"Error deleting by metadata: {e}")
        return 0

# API endpoint
@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    if chatbot is None:
        raise HTTPException(503, "Chatbot not initialized")

    success = chatbot.vector_store_manager.vector_store.delete_document(document_id)

    if success:
        return {"status": "deleted", "document_id": document_id}
    else:
        raise HTTPException(404, "Document not found")
```

#### 7.4 Add Duplicate Detection
```python
# src/utils/deduplication.py
from datasketch import MinHash, MinHashLSH

class DuplicateDetector:
    def __init__(self, threshold: float = 0.9):
        self.threshold = threshold
        self.lsh = MinHashLSH(threshold=threshold, num_perm=128)
        self.minhashes = {}

    def compute_minhash(self, text: str) -> MinHash:
        """Compute MinHash for text"""
        minhash = MinHash(num_perm=128)
        words = text.lower().split()
        for word in words:
            minhash.update(word.encode())
        return minhash

    def is_duplicate(self, doc_id: str, text: str) -> tuple[bool, List[str]]:
        """Check if document is duplicate"""
        minhash = self.compute_minhash(text)

        # Query LSH for similar documents
        similar = self.lsh.query(minhash)

        if similar:
            return True, similar

        # Add to index
        self.lsh.insert(doc_id, minhash)
        self.minhashes[doc_id] = minhash

        return False, []
```

**New dependency:** `datasketch==1.6.4`

---

## 8. API Improvements

**Current Score: 6/10 → Target: 9/10**

### Critical Issues
- ❌ No API versioning
- ❌ No webhook support
- ❌ No async task queue
- ❌ No bulk operations
- ❌ Using deprecated `@app.on_event` (api.py:80)

### Improvements

#### 8.1 Add API Versioning
```python
# src/api/v1/router.py
from fastapi import APIRouter

api_v1 = APIRouter(prefix="/api/v1", tags=["v1"])

@api_v1.post("/query")
async def query_v1(request: QueryRequest):
    """V1 query endpoint"""
    pass

@api_v1.post("/ingest")
async def ingest_v1(file: UploadFile):
    """V1 ingest endpoint"""
    pass

# Main app
from src.api.v1.router import api_v1
from src.api.v2.router import api_v2

app = FastAPI(title="RAG Chatbot API")
app.include_router(api_v1)
app.include_router(api_v2)
```

**New directory structure:**
```
src/
  api/
    v1/
      __init__.py
      router.py
      models.py
    v2/
      __init__.py
      router.py
      models.py
```

#### 8.2 Fix Deprecated `on_event`
```python
# ❌ Before (api.py:80)
@app.on_event("startup")
async def startup_event():
    global chatbot
    chatbot = RAGChatbot()

# ✅ After
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global chatbot
    logger.info("Initializing RAG Chatbot...")
    chatbot = RAGChatbot(
        embedding_provider=Config.EMBEDDING_PROVIDER,
        llm_provider=Config.LLM_PROVIDER,
        llm_model=Config.LLM_MODEL,
        reranker_type=Config.RERANKER_TYPE
    )
    logger.info("✅ RAG Chatbot initialized successfully!")

    yield

    # Shutdown
    logger.info("Shutting down RAG Chatbot...")
    if chatbot:
        # Cleanup resources
        chatbot.cleanup()
    logger.info("✅ Shutdown complete")

app = FastAPI(lifespan=lifespan)
```

**Files to modify:**
- `api.py`

#### 8.3 Add Async Task Queue (Celery)
```python
# src/tasks/celery_app.py
from celery import Celery

celery_app = Celery(
    'rag_chatbot',
    broker=f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/1',
    backend=f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/2'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True)
def ingest_document_task(self, file_path: str):
    """Background task for document ingestion"""
    try:
        chatbot = RAGChatbot()
        num_chunks = chatbot.ingest_document(file_path)
        return {
            "status": "success",
            "chunks": num_chunks,
            "file": file_path
        }
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)

# API endpoint
@app.post("/ingest/async")
async def ingest_async(request: IngestRequest):
    """Async document ingestion"""
    task = ingest_document_task.delay(request.file_path)
    return {
        "task_id": task.id,
        "status": "processing"
    }

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status"""
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

**New dependency:** `celery[redis]==5.3.4`

#### 8.4 Add Bulk Operations
```python
@app.post("/query/bulk")
async def query_bulk(queries: List[str]) -> List[QueryResponse]:
    """Bulk query processing"""
    if len(queries) > 100:
        raise HTTPException(400, "Maximum 100 queries per batch")

    results = []
    for query in queries:
        try:
            result = chatbot.query(query)
            results.append(QueryResponse(**result))
        except Exception as e:
            results.append(QueryResponse(
                question=query,
                answer=f"Error: {str(e)}",
                sources=None
            ))

    return results

@app.post("/ingest/bulk")
async def ingest_bulk(files: List[UploadFile]):
    """Bulk document ingestion"""
    results = []

    for file in files:
        try:
            # Save and ingest
            file_path = save_uploaded_file(file)
            num_chunks = chatbot.ingest_document(file_path)

            results.append({
                "filename": file.filename,
                "status": "success",
                "chunks": num_chunks
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })

    return {"results": results}
```

#### 8.5 Add Webhook Support
```python
# src/webhooks/manager.py
from typing import List, Dict
import httpx

class WebhookManager:
    def __init__(self):
        self.webhooks: Dict[str, List[str]] = {}

    async def register(self, url: str, events: List[str]):
        """Register webhook for events"""
        for event in events:
            if event not in self.webhooks:
                self.webhooks[event] = []
            if url not in self.webhooks[event]:
                self.webhooks[event].append(url)

    async def trigger(self, event: str, data: dict):
        """Trigger webhook for event"""
        if event not in self.webhooks:
            return

        async with httpx.AsyncClient() as client:
            for url in self.webhooks[event]:
                try:
                    await client.post(url, json={
                        "event": event,
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    }, timeout=5.0)
                except Exception as e:
                    logger.error(f"Webhook error for {url}: {e}")

# API endpoints
@app.post("/webhooks/register")
async def register_webhook(url: str, events: List[str]):
    """Register webhook"""
    await webhook_manager.register(url, events)
    return {"status": "registered", "url": url, "events": events}

# Usage in code
await webhook_manager.trigger("document.ingested", {
    "filename": file.filename,
    "chunks": num_chunks
})
```

---

## 9. User Experience

**Current Score: 6/10 → Target: 9/10**

### Improvements

#### 9.1 Add Query Suggestions
```python
@app.get("/suggestions")
async def get_suggestions(partial_query: str, limit: int = 5):
    """Get query autocomplete suggestions"""
    # Get from recent queries or pre-defined templates
    suggestions = [
        "What is machine learning?",
        "Explain neural networks",
        "How does RAG work?",
        "What are embeddings?"
    ]

    # Filter based on partial query
    matches = [s for s in suggestions if partial_query.lower() in s.lower()]
    return {"suggestions": matches[:limit]}
```

#### 9.2 Add Session Management
```python
# src/session/manager.py
from uuid import uuid4

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationMemory] = {}
        self.session_ttl = 3600  # 1 hour

    def get_or_create(self, session_id: Optional[str] = None) -> tuple[str, ConversationMemory]:
        """Get or create session"""
        if session_id and session_id in self.sessions:
            return session_id, self.sessions[session_id]

        new_session_id = str(uuid4())
        self.sessions[new_session_id] = ConversationMemory()
        return new_session_id, self.sessions[new_session_id]

    def cleanup_expired(self):
        """Remove expired sessions"""
        # Implement TTL cleanup
        pass

@app.post("/query")
async def query_with_session(
    request: QueryRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Query with session support"""
    session_id, memory = session_manager.get_or_create(session_id)

    # Use session memory
    result = chatbot.query(
        request.question,
        use_memory=True,
        memory=memory
    )

    return {
        **result,
        "session_id": session_id
    }
```

#### 9.3 Add Feedback System
```python
# src/feedback/storage.py
class FeedbackStorage:
    def __init__(self):
        self.feedback_db = []

    def store(self, query_id: str, rating: int, comment: str):
        """Store user feedback"""
        self.feedback_db.append({
            "query_id": query_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now()
        })

@app.post("/feedback")
async def submit_feedback(
    query_id: str,
    rating: int = Field(..., ge=1, le=5),
    comment: Optional[str] = None
):
    """Submit feedback for a query"""
    feedback_storage.store(query_id, rating, comment)
    return {"status": "success", "message": "Thank you for your feedback!"}
```

#### 9.4 Add Export Functionality
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@app.get("/conversations/{session_id}/export")
async def export_conversation(
    session_id: str,
    format: str = Query("json", regex="^(json|pdf|txt)$")
):
    """Export conversation history"""
    if session_id not in session_manager.sessions:
        raise HTTPException(404, "Session not found")

    history = session_manager.sessions[session_id].get_history()

    if format == "json":
        return JSONResponse({"history": history})

    elif format == "pdf":
        pdf_buffer = generate_pdf(history)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=conversation_{session_id}.pdf"}
        )

    elif format == "txt":
        txt_content = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in history
        ])
        return Response(
            content=txt_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=conversation_{session_id}.txt"}
        )
```

---

## 10. Documentation

**Current Score: 6/10 → Target: 9/10**

### Improvements

#### 10.1 Enhanced API Documentation
```python
app = FastAPI(
    title="RAG Chatbot API",
    description="""
# RAG Chatbot API

A production-ready Retrieval-Augmented Generation chatbot API.

## Features

- 📄 **Multi-format document ingestion** (PDF, TXT, CSV, HTML, Markdown)
- 🔍 **Semantic search** with vector embeddings
- 🤖 **Multiple LLM providers** (Google Gemini, OpenAI, Anthropic)
- 🔄 **Re-ranking** with BM25 and cross-encoder
- 💬 **Conversation memory** for contextual responses
- 🚀 **Production-ready** with caching, monitoring, and rate limiting

## Authentication

All endpoints require Bearer token authentication:

```
Authorization: Bearer <your-api-key>
```

## Rate Limits

- **Free tier**: 10 requests/minute
- **Pro tier**: 100 requests/minute
- **Enterprise**: Custom limits

## Support

- Documentation: https://docs.example.com
- Issues: https://github.com/yourusername/rag-chatbot/issues
- Email: support@example.com
    """,
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    contact={
        "name": "API Support",
        "email": "support@example.com",
        "url": "https://example.com/support"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

@app.post(
    "/query",
    summary="Query the chatbot",
    description="""
    Submit a question to the RAG chatbot and receive an AI-generated answer.

    The chatbot will:
    1. Search for relevant documents in the vector database
    2. Re-rank results for better relevance
    3. Generate a response using the selected LLM

    **Parameters:**
    - `question`: Your question (max 5000 characters)
    - `use_memory`: Include conversation history (default: false)
    - `return_sources`: Return source documents (default: false)

    **Response:**
    - `answer`: AI-generated answer
    - `sources`: Source documents (if requested)
    """,
    response_model=QueryResponse,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "question": "What is machine learning?",
                        "answer": "Machine learning is...",
                        "sources": [...]
                    }
                }
            }
        },
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Service unavailable"}
    },
    tags=["query"]
)
async def query_chatbot(request: QueryRequest):
    pass
```

#### 10.2 Add Architecture Documentation
Create `ARCHITECTURE.md`:

```markdown
# Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                 │
│  - Authentication  - Rate Limiting  - Request Validation │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   RAG Orchestrator                       │
│  - Query Processing  - Result Aggregation  - Caching    │
└──┬────────┬────────┬────────┬────────┬──────────────────┘
   │        │        │        │        │
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌──────┐
│Doc │  │Emb │  │Vec │  │Ret │  │ LLM  │
│Ing │  │Gen │  │Str │  │Rnk │  │ Int  │
└────┘  └────┘  └────┘  └────┘  └──────┘

External Services:
├─ Redis (Caching)
├─ Prometheus (Metrics)
├─ Jaeger (Tracing)
└─ ChromaDB (Vector Store)
```

## Data Flow

1. **Ingestion Pipeline**
   - Document uploaded → Validation → Text extraction
   - Chunking → Embedding generation → Vector store

2. **Query Pipeline**
   - Query received → Cache check → Embedding generation
   - Vector search → Re-ranking → Context building
   - LLM generation → Response caching → Return result

## Technology Stack

- **Framework**: FastAPI 0.109+
- **LLM Providers**: Google Gemini, OpenAI, Anthropic
- **Vector DB**: ChromaDB
- **Cache**: Redis
- **Monitoring**: Prometheus + Grafana
- **Tracing**: OpenTelemetry + Jaeger
```

#### 10.3 Add Troubleshooting Guide
Create `TROUBLESHOOTING.md`:

```markdown
# Troubleshooting Guide

## Common Issues

### 1. API Returns 503 "Chatbot not initialized"

**Cause**: Chatbot failed to initialize on startup

**Solution**:
1. Check logs: `docker logs api`
2. Verify API keys in `.env`
3. Check ChromaDB directory permissions
4. Restart container: `docker-compose restart api`

### 2. Slow Query Response Times

**Cause**: Multiple possible causes

**Solutions**:
- Check Redis connection: `redis-cli ping`
- Monitor metrics: http://localhost:9090
- Check vector DB size: `GET /stats`
- Enable caching in config

### 3. Out of Memory Errors

**Cause**: Large documents or batch processing

**Solutions**:
- Reduce batch size in config
- Increase container memory limit
- Enable streaming for large files
- Use pagination for results

## Performance Tuning

### Optimize Retrieval
- Adjust `TOP_K_RETRIEVAL` (default: 10)
- Tune `TOP_K_RERANK` (default: 5)
- Choose appropriate reranker type

### Optimize Embeddings
- Use smaller embedding models for speed
- Enable batch processing
- Use GPU if available

## Logs

View application logs:
```bash
# Docker
docker logs -f api

# Direct
tail -f logs/app.log
```

## Support

If issues persist:
1. Check GitHub Issues
2. Enable debug logging
3. Contact support with logs
```

---

## Priority Roadmap

### **Phase 1: Critical Security & Stability (Week 1-2)**
**Goal: Make the system secure and production-ready**

- [ ] 1.1 Add JWT authentication
- [ ] 1.2 Implement rate limiting (slowapi)
- [ ] 1.3 Fix CORS configuration (environment-specific)
- [ ] 1.4 Add input validation and sanitization
- [ ] 1.5 Implement retry logic with exponential backoff
- [ ] 1.6 Fix deprecated `@app.on_event` usage
- [ ] 1.7 Add strict file upload validation
- [ ] 1.8 Replace bare exception catches

**Expected Improvement**: 6.5/10 → 7.5/10

---

### **Phase 2: Testing & Quality (Week 3-4)**
**Goal: Ensure reliability and code quality**

- [ ] 2.1 Add unit tests (target 60% coverage)
- [ ] 2.2 Add integration tests
- [ ] 2.3 Set up CI/CD pipeline (GitHub Actions)
- [ ] 2.4 Add type checking (mypy)
- [ ] 2.5 Add property-based tests (hypothesis)
- [ ] 2.6 Set up code coverage tracking (codecov)
- [ ] 2.7 Add linting (flake8, black)

**Expected Improvement**: 7.5/10 → 8.5/10

---

### **Phase 3: Monitoring & Observability (Week 5-6)**
**Goal: Full visibility into system behavior**

- [ ] 3.1 Add Prometheus metrics
- [ ] 3.2 Set up Grafana dashboards
- [ ] 3.3 Implement OpenTelemetry tracing
- [ ] 3.4 Add structured logging (structlog)
- [ ] 3.5 Implement health check endpoints
- [ ] 3.6 Set up alerting (Prometheus Alertmanager)
- [ ] 3.7 Add request ID tracking

**Expected Improvement**: 8.5/10 → 9.0/10

---

### **Phase 4: Performance & Scalability (Week 7-8)**
**Goal: Optimize for production load**

- [ ] 4.1 Implement Redis caching
- [ ] 4.2 Add async operations
- [ ] 4.3 Implement batch processing
- [ ] 4.4 Add pagination
- [ ] 4.5 Set up load testing (Locust)
- [ ] 4.6 Add connection pooling
- [ ] 4.7 Implement streaming responses
- [ ] 4.8 Optimize database queries

**Expected Improvement**: 9.0/10 → 9.3/10

---

### **Phase 5: Enhanced Features (Week 9-10)**
**Goal: Improve user experience and functionality**

- [ ] 5.1 Add API versioning
- [ ] 5.2 Implement async task queue (Celery)
- [ ] 5.3 Add webhook support
- [ ] 5.4 Implement bulk operations
- [ ] 5.5 Add session management
- [ ] 5.6 Implement feedback system
- [ ] 5.7 Add query suggestions
- [ ] 5.8 Add export functionality

**Expected Improvement**: 9.3/10 → 9.5/10

---

### **Phase 6: Data Management & DevOps (Week 11-12)**
**Goal: Production deployment readiness**

- [ ] 6.1 Add document versioning
- [ ] 6.2 Implement backup/restore
- [ ] 6.3 Add duplicate detection
- [ ] 6.4 Create Dockerfile
- [ ] 6.5 Create docker-compose.yml
- [ ] 6.6 Add Kubernetes manifests
- [ ] 6.7 Set up secret management
- [ ] 6.8 Create deployment documentation

**Expected Improvement**: 9.5/10 → 9.8/10

---

## Quick Wins (Can Complete in 1-2 Days)

These improvements provide immediate value with minimal effort:

1. **Fix CORS** → +0.3 points (30 minutes)
2. **Add rate limiting** → +0.4 points (1 hour)
3. **Fix deprecated on_event** → +0.2 points (30 minutes)
4. **Add input validation** → +0.3 points (2 hours)
5. **Add health check endpoints** → +0.2 points (1 hour)
6. **Set up Docker** → +0.5 points (3 hours)
7. **Add basic unit tests** → +0.6 points (4 hours)
8. **Add API key auth** → +0.5 points (3 hours)

**Total Quick Wins**: +3.0 points → **9.5/10**

---

## Estimated Effort

| Phase | Estimated Time | Priority | Impact |
|-------|---------------|----------|--------|
| Phase 1 (Security) | 40-60 hours | 🔴 Critical | High |
| Phase 2 (Testing) | 50-70 hours | 🟠 High | High |
| Phase 3 (Monitoring) | 30-40 hours | 🟠 High | Medium |
| Phase 4 (Performance) | 40-50 hours | 🟡 Medium | High |
| Phase 5 (Features) | 40-50 hours | 🟡 Medium | Medium |
| Phase 6 (DevOps) | 30-40 hours | 🟢 Low | Medium |
| **Total** | **230-310 hours** | - | - |
| **Weeks (40h/week)** | **6-8 weeks** | - | - |

---

## Success Metrics

Track these metrics to measure improvement:

### Security
- [ ] 100% of endpoints require authentication
- [ ] Zero SAST security findings
- [ ] All inputs validated and sanitized
- [ ] Rate limiting active on all public endpoints

### Reliability
- [ ] 99.9% uptime SLA
- [ ] < 1% error rate
- [ ] Mean time to recovery < 5 minutes
- [ ] Zero data loss incidents

### Performance
- [ ] P95 latency < 500ms
- [ ] Cache hit rate > 60%
- [ ] Throughput > 100 req/sec
- [ ] Database query time < 50ms

### Quality
- [ ] Code coverage > 80%
- [ ] All critical paths tested
- [ ] Zero high-priority bugs
- [ ] Type coverage > 90%

### Observability
- [ ] All metrics collected
- [ ] Alerts configured
- [ ] Dashboards created
- [ ] Traces captured for all requests

---

## Maintenance

### Daily
- Monitor error rates and latency
- Check alert notifications
- Review system logs

### Weekly
- Review metrics trends
- Update dependencies
- Run security scans
- Check backup integrity

### Monthly
- Load testing
- Review and optimize queries
- Update documentation
- Security audit

---

## Resources

### Tools
- **FastAPI**: https://fastapi.tiangolo.com/
- **ChromaDB**: https://docs.trychroma.com/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/
- **OpenTelemetry**: https://opentelemetry.io/docs/

### Best Practices
- **REST API Design**: https://restfulapi.net/
- **12-Factor App**: https://12factor.net/
- **Security**: https://cheatsheetseries.owasp.org/

---

**Last Updated**: 2025-01-12
**Version**: 1.0
**Target Completion**: 8-10 weeks from start
