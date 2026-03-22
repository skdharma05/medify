import os
import shutil
import uuid
import logging
import filetype
from pathlib import Path
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# Resolve upload dir relative to this file so it works no matter where uvicorn is launched from
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "temp_uploads"

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}


def validate_file_extension(filename: str) -> None:
    """Raise ValueError if the file extension is not in the allowed set."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def validate_file_size(content: bytes, max_mb: int) -> None:
    """Raise ValueError if the file content exceeds the size limit."""
    max_bytes = max_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise ValueError(f"File size exceeds the {max_mb} MB limit.")


def validate_file_mime(content: bytes, filename: str) -> None:
    """
    Raise ValueError if the detected MIME type does not match any allowed type.
    Falls back gracefully for plain text files that filetype can't detect.
    """
    kind = filetype.guess(content)
    if kind is None:
        # filetype can't detect plain‑text or markdown — allow it through
        # and rely on extension validation done earlier
        logger.debug("MIME type could not be detected for '%s'; skipping MIME check.", filename)
        return
    if kind.mime not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Detected MIME type '{kind.mime}' is not allowed."
        )


def create_session_directory() -> str:
    """Create a unique session directory for resume uploads and return the session ID."""
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Created session directory for session_id=%s", session_id)
    return session_id


def save_uploaded_file(content: bytes, filename: str, session_id: str) -> Path:
    """Save raw file bytes to the session directory and return the full path."""
    file_path = UPLOAD_DIR / session_id / filename
    file_path.write_bytes(content)
    logger.info("Saved file '%s' for session_id=%s (%d bytes)", filename, session_id, len(content))
    return file_path


def cleanup_session(session_id: str) -> None:
    """Remove the session upload directory and all its contents."""
    session_dir = UPLOAD_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)
        logger.info("Cleaned up session directory for session_id=%s", session_id)