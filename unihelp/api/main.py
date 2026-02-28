from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from unihelp.core.logging import setup_logger
from .routes import router

logger = setup_logger(__name__)

app = FastAPI(
    title="UniHelp API",
    description="University Administrative Assistant API for IIT/NAU Tunisia",
    version="1.0.0"
)

# Configure CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting UniHelp API...")

@app.get("/")
def read_root():
    return {"message": "Welcome to UniHelp API. Access /docs for Swagger UI."}
