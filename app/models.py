# app/models.py
from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    session_id: str
    query: str
    temperature: Optional[float] = 0.1

class QueryResponse(BaseModel):
    session_id: str
    query: str
    response: str

class UploadResponse(BaseModel):
    session_id: str
    message: str
    filename: str

class ErrorResponse(BaseModel):
    detail: str