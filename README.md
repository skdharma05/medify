# 🧠 Resume Q&A System with Gemini AI

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![Gemini](https://img.shields.io/badge/Gemini_AI-FF5F15.svg)

## 🌟 Features

- 📄 Upload resumes (PDF/DOCX/TXT)
- ❓ Ask questions about resume content
- 🧠 Gemini AI-powered analysis
- 🔒 Session-based security
- ⚡ FastAPI backend

## 🛠️ Tech Stack

- Python 3.10+
- FastAPI
- Google Gemini AI
- LlamaIndex
- Pydantic

## 🚀 Quick Start

1. Clone repository:
    ```bash
      git clone https://github.com/yourusername/resume-qa-system.git
      cd resume-qa-system

2. Set up environment:
    ```bash
      python -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt

4. Configure environment
   Create .env file in root directory:
   ```bash
      GOOGLE_API_KEY=your_gemini_api_key_here
      # Optional:
      # TEMPERATURE=0.1
      # MAX_FILE_SIZE_MB=5

  ##  📂 Project Structure
          resume-qa-system/
          ├── app/
          │   ├── __init__.py         # Package initialization
          │   ├── main.py             # FastAPI application
          │   ├── models.py           # Pydantic models
          │   ├── prompts.py          # AI prompt templates
          │   └── utils.py            # Utility functions
          ├── .env                    # Environment configuration
          ├── requirements.txt        # Python dependencies
          └── README.md               # This file

3. Run server:
    ```bash
       uvicorn app.main:app --reload

## 📡 API Endpoints

      Endpoint    Method	Description
      /health	    GET	   Service health check
      /upload	    POST	  Upload resume file
      /query	    POST	  Ask questions about resume
      /session/{id}	DELETE	  Clear session

## Example Requests

Upload Resume:

     curl -X POST -F "file=@resume.pdf" http://localhost:8000/upload
uery Resume:

      curl -X POST -H "Content-Type: application/json" -d '{
        "session_id": "abc123",
        "query": "What technical skills are listed?"
      }' http://localhost:8000/query


## 🛠 Troubleshooting
    Issue: Missing API key error
    Fix: Verify .env file contains GOOGLE_API_KEY
    
    Issue: Module not found errors
    Fix: Run pip install llama-index-llms-gemini llama-index-embeddings-gemini
    
    Issue: Invalid session errors
    Fix: Use exact session_id from upload response

##  📄 License
MIT License — See LICENSE for details.


