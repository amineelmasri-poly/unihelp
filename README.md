# UniHelp: University Administrative Assistant

UniHelp is a complete RAG (Retrieval-Augmented Generation) system designed for university administration (e.g., IIT/NAU Tunisia). It features an interactive chatbot that answers student questions based on official university documents, and an email generator for common requests (scholarships, absences, etc.).

## Architecture
- **Document Processing Pipeline**: Reads PDF, DOCX, XLSX, and TXT files, chunks them while preserving semantic meaning, and extracts metadata.
- **Vector Database**: Local ChromaDB instance with multilingual embeddings (`paraphrase-multilingual-MiniLM-L12-v2`).
- **Engine**: Langchain + OpenAI API (`gpt-4o-mini`) for prompt chaining and accurate, cited responses.
- **Backend**: FastAPI providing endpoints for RAG queries and email generation.
- **Frontend**: Streamlit application with Chat, Email Generation, and Admin dashboard views.

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- An OpenAI API key

### 2. Installation
```bash
# Optional: Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy the `.env.example` to `.env` and fill in your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

### 4. Data Generation & Ingestion
Run the following commands to generate 5 sample university documents and ingest them into the local ChromaDB vector store:
```bash
# Generates documents in data/raw/
python generate_samples.py

# Processes documents and saves embeddings to data/chroma_db/
python ingest.py
```

### 5. Running the Application
A demo script is provided to spin up both the FastAPI backend and Streamlit frontend concurrently:
```bash
python demo_script.py
```
- Streamlit UI will be available at: http://localhost:8501
- FastAPI Swagger Docs will be available at: http://localhost:8000/docs
