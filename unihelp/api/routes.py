from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from unihelp.rag.engine import RAGEngine
from unihelp.tools.email_gen import EmailGenerator
from unihelp.rag.vector_store import VectorStore
from unihelp.core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize engines lazily or at startup
rag_engine = None
email_generator = None
vector_store = None

def get_rag_engine():
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine

def get_email_generator():
    global email_generator
    if email_generator is None:
        email_generator = EmailGenerator()
    return email_generator

def get_vector_store():
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store

class AskRequest(BaseModel):
    question: str
    top_k: int = 4

class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

class EmailRequest(BaseModel):
    template_type: str
    student_info: str
    include_rag_context: bool = False

class FeedbackRequest(BaseModel):
    query: str
    response: str
    rating: int # 1 to 5
    comments: Optional[str] = None

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        engine = get_rag_engine()
        result = engine.answer(request.question, k=request.top_k)
        return AskResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        logger.error(f"Error in /ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
def list_email_templates():
    gen = get_email_generator()
    return {"templates": gen.get_supported_templates()}

@router.post("/generate-email")
def generate_email(request: EmailRequest):
    try:
        gen = get_email_generator()
        context = ""
        
        # Optionally inject context from university rules for the specific request
        if request.include_rag_context:
            engine = get_rag_engine()
            # Simple retrieval for context
            docs = engine.vector_store.similarity_search(request.template_type, k=3)
            context, _ = engine._format_docs(docs)
            
        email_content = gen.generate(request.template_type, request.student_info, context)
        return {"email": email_content}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /generate-email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
def list_documents():
    """Returns basic stats about the loaded documents."""
    try:
        vs = get_vector_store()
        stats = vs.get_collection_stats()
        return {
            "status": "ready",
            "total_chunks": stats["count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Logs user feedback to a file or db for analytics."""
    logger.info(f"Feedback Received: Rating={request.rating}, Comments={request.comments}")
    # In a real app we would write this to a database
    return {"status": "Feedback recorded successfully."}
