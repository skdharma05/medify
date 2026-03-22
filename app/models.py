from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    session_id: str = Field(..., min_length=36, max_length=36, description="UUID session identifier")
    query: str = Field(..., min_length=3, max_length=1000, description="Question to ask about the resume")
    temperature: Optional[float] = Field(0.1, ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    session_id: str
    query: str
    answer: str


class UploadResponse(BaseModel):
    session_id: str
    message: str
    filename: str


class SessionStatusResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    active_sessions: int
    api_key_set: bool


class ErrorResponse(BaseModel):
    detail: str