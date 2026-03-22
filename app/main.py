import logging
import os
from pathlib import Path

import aiofiles
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from typing import Dict

from app.models import (
    QueryRequest,
    QueryResponse,
    UploadResponse,
    SessionStatusResponse,
    HealthResponse,
)
from app.prompts import QA_PROMPT
from app.utils import (
    UPLOAD_DIR,
    create_session_directory,
    cleanup_session,
    validate_file_extension,
    validate_file_size,
    validate_file_mime,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Medify — Resume Q&A System",
    description="Upload a resume and ask questions powered by Gemini AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy-initialised AI models (set in startup event after key check)
# ---------------------------------------------------------------------------
llm: Gemini | None = None
embed_model: GeminiEmbedding | None = None

# In-memory session store (replaced with Redis in Phase 2)
user_sessions: Dict[str, VectorStoreIndex] = {}


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup() -> None:
    global llm, embed_model

    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY environment variable is not set. "
            "Create a .env file or export the variable before starting the server."
        )

    llm = Gemini(api_key=GOOGLE_API_KEY)
    embed_model = GeminiEmbedding(
        model_name="models/embedding-001",
        api_key=GOOGLE_API_KEY,
    )

    # Ensure the upload root directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Medify started. Upload directory: %s", UPLOAD_DIR)


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Medify shutting down. Active sessions: %d", len(user_sessions))
    user_sessions.clear()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        active_sessions=len(user_sessions),
        api_key_set=bool(GOOGLE_API_KEY),
    )


@app.post("/upload", response_model=UploadResponse, tags=["Resume"])
async def upload_resume(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a resume file (PDF, DOCX, TXT, MD) and build a searchable index."""
    session_id: str | None = None

    try:
        # --- Validation ---
        validate_file_extension(file.filename)
        logger.info("Upload started: filename='%s'", file.filename)

        content = await file.read()
        validate_file_size(content, MAX_FILE_SIZE_MB)
        validate_file_mime(content, file.filename)

        # --- Save & Index ---
        session_id = create_session_directory()
        file_path = UPLOAD_DIR / session_id / file.filename

        async with aiofiles.open(file_path, "wb") as out:
            await out.write(content)

        documents = SimpleDirectoryReader(input_files=[str(file_path)]).load_data()
        index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
        user_sessions[session_id] = index

        logger.info("Resume indexed successfully. session_id=%s", session_id)
        return UploadResponse(
            session_id=session_id,
            message="Resume processed successfully",
            filename=file.filename,
        )

    except ValueError as exc:
        # Validation errors → 400 Bad Request
        logger.warning("Upload validation failed: %s", exc)
        if session_id:
            cleanup_session(session_id)
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.error("Upload failed unexpectedly: %s", exc, exc_info=True)
        if session_id:
            cleanup_session(session_id)
        raise HTTPException(status_code=500, detail=str(exc))

    finally:
        await file.close()


@app.post("/query", response_model=QueryResponse, tags=["Resume"])
async def answer_query(query_input: QueryRequest) -> QueryResponse:
    """Ask a question about a previously uploaded resume."""
    if query_input.session_id not in user_sessions:
        logger.warning("Query on unknown session_id=%s", query_input.session_id)
        raise HTTPException(status_code=404, detail="Session not found. Please upload a resume first.")

    try:
        index = user_sessions[query_input.session_id]
        query_engine = index.as_query_engine(
            llm=llm,
            text_qa_template=QA_PROMPT,
        )
        response = query_engine.query(query_input.query)
        logger.info("Query answered. session_id=%s query='%s'", query_input.session_id, query_input.query)
        return QueryResponse(
            session_id=query_input.session_id,
            query=query_input.query,
            answer=str(response),
        )

    except Exception as exc:
        logger.error("Query failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/session/{session_id}", response_model=SessionStatusResponse, tags=["Session"])
async def clear_session(session_id: str) -> SessionStatusResponse:
    """Remove a session and delete its uploaded files."""
    if session_id in user_sessions:
        del user_sessions[session_id]
        logger.info("Session removed from memory. session_id=%s", session_id)

    cleanup_session(session_id)
    return SessionStatusResponse(message=f"Session {session_id} cleared successfully.")