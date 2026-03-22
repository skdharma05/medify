# 🧠 Medify — Resume Q&A System with Gemini AI

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)
![Gemini](https://img.shields.io/badge/Gemini_AI-FF5F15.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

A stateless, asynchronous, and scalable backend API that lets you upload resumes (PDF, DOCX, TXT, MD) and ask intelligent questions about them using Google Gemini AI and LlamaIndex.

## 🌟 Features

- **📄 Universal Uploads**: Supports multiple resume formats (PDF, DOCX, TXT, MD).
- **❓ Intelligent Q&A**: Employs Google's Gemini Flash model with specialized RAG (Retrieval-Augmented Generation) prompts.
- **⚡ Fully Asynchronous**: Uses FastAPI and `aiofiles` for non-blocking file I/O, ensuring high throughput.
- **🛡️ Secure & Validated**: Built-in MIME-type validation, configurable file size limits, and query length constraints.
- **🐳 Docker Ready**: Comes with a multi-stage Dockerfile and Docker Compose setup for instant deployment and isolated execution.
- **🧪 Automated Tests**: Includes a built-in smoke testing suite to verify system health and API contracts.

---

## 🚀 Quick Start

### 1. Set Up Environment Variables
Create a `.env` file in the root directory by copying the example template:
```bash
cp .env.example .env
```
Open `.env` and add your [Google AI Studio API Key](https://aistudio.google.com/app/apikey):
```env
GOOGLE_API_KEY=your_gemini_api_key_here
MAX_FILE_SIZE_MB=5
ALLOWED_ORIGINS=*
```

### 2. Run with Docker (Recommended)
You can bring up the entire system with a single command:
```bash
docker compose up --build -d
```
The API will be available at `http://localhost:8000`.

### 3. Run Manually (Without Docker)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🧪 Running Tests
We've included a comprehensive smoke test script to verify all endpoints are working correctly. With the server running, open a new terminal and run:

```bash
python test_api.py
```
This will upload a sample resume, test the Q&A engine, verify file size limits, and test session deletion automatically.

---

## 📡 API Endpoints

| Endpoint         | Method | Description                                      |
|------------------|--------|--------------------------------------------------|
| `/health`        | GET    | View service health, active sessions, config      |
| `/upload`        | POST   | Upload a resume (returns a `session_id`)         |
| `/query`         | POST   | Ask questions using a valid `session_id`          |
| `/session/{id}`  | DELETE | Clear a session and delete uploaded files        |

---

## 📌 Example Workflow

**1. Upload a Resume**:
```bash
curl -X POST -F "file=@tests/sample_resume.txt" http://localhost:8000/upload
```
*Response will contain a `session_id`.*

**2. Query the Resume**:
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "session_id": "<PASTE_SESSION_ID_HERE>",
  "query": "What are this person technical skills?"
}' http://localhost:8000/query
```

---

## 📂 Project Structure

```
resume-qa-system/
├── app/
│   ├── __init__.py         # Package initialization
│   ├── main.py             # FastAPI routing and application lifecycle
│   ├── models.py           # Strict Pydantic models for request/response
│   ├── prompts.py          # AI prompt templates for LlamaIndex
│   └── utils.py            # Async I/O, validation, and path management
├── tests/
│   └── sample_resume.txt   # Sample resume data
├── .env.example            # Environment configuration template
├── docker-compose.yml      # Local development Docker setup
├── Dockerfile              # Multi-stage production Docker build
├── requirements.txt        # Python dependencies
├── test_api.py             # Automated API smoke tests
└── README.md               # This file
```

## 📄 License
MIT License — See `LICENSE` for details.
