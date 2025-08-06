import os
import shutil
import uuid
from typing import Optional
from pathlib import Path
from fastapi import UploadFile

def create_session_directory() -> str:
    """Create a unique session directory for resume uploads"""
    session_id = str(uuid.uuid4())
    temp_dir = Path(f"./app/temp_uploads/{session_id}")
    temp_dir.mkdir(parents=True, exist_ok=True)
    return session_id

def save_uploaded_file(file: UploadFile, session_id: str) -> str:
    """Save uploaded file to session directory"""
    temp_dir = Path(f"./app/temp_uploads/{session_id}")
    file_path = temp_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(file_path)

def cleanup_session(session_id: str):
    """Remove session files and directory"""
    temp_dir = Path(f"./app/temp_uploads/{session_id}")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

def validate_file_extension(filename: str):
    """Check for allowed file types"""
    allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise ValueError("Unsupported file type")