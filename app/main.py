from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from dotenv import load_dotenv
import os
import shutil
import uuid
from pathlib import Path
from typing import Dict
from pydantic import BaseModel  # Added for request validation

load_dotenv()

app = FastAPI(title="Dynamic Resume Q&A System")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
llm = Gemini(api_key=os.getenv("GOOGLE_API_KEY"))
embed_model = GeminiEmbedding(
    model_name="models/embedding-001",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Session storage
user_sessions: Dict[str, VectorStoreIndex] = {}

# Request Model for Query Endpoint
class QueryInput(BaseModel):  # Added for proper request validation
    session_id: str
    query: str

# Helper functions
def create_session_directory() -> str:
    session_id = str(uuid.uuid4())
    Path(f"temp_uploads/{session_id}").mkdir(parents=True, exist_ok=True)
    return session_id

def save_uploaded_file(file: UploadFile, session_id: str) -> str:
    file_path = f"temp_uploads/{session_id}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

def cleanup_session(session_id: str):
    shutil.rmtree(f"temp_uploads/{session_id}", ignore_errors=True)

# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "active_sessions": len(user_sessions)}

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        session_id = create_session_directory()
        file_path = save_uploaded_file(file, session_id)
        
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
        user_sessions[session_id] = index
        
        return {
            "session_id": session_id,
            "message": "Resume processed successfully",
            "filename": file.filename
        }
    except Exception as e:
        cleanup_session(session_id)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

@app.post("/query")
async def answer_query(query_input: QueryInput):  # Changed to use Pydantic model
    if query_input.session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        index = user_sessions[query_input.session_id]
        query_engine = index.as_query_engine(llm=llm)
        response = query_engine.query(query_input.query)
        return {"answer": str(response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in user_sessions:
        del user_sessions[session_id]
    cleanup_session(session_id)
    return {"message": f"Session {session_id} cleared"}

# Create temp directory on startup
Path("temp_uploads").mkdir(exist_ok=True)