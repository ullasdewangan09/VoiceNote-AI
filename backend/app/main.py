from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.utils.validators import VoiceNoteException

from app.api.routes.health import router as health_router
from app.api.routes.transcription import router as transcription_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.evaluation import router as evaluation_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "VoiceNote AI — Intelligent ASR-Based Lecture & Meeting Assistant Backend. "
        "Provides modular APIs for audio preprocessing, Whisper-based speech-to-text, "
        "keyword extraction, extractive summarization, action-item detection, and WER evaluation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for frontend and deployment environments
cors_origins = settings.ALLOWED_ORIGINS
allow_creds = False if "*" in cors_origins else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handler for Domain Exceptions
@app.exception_handler(VoiceNoteException)
async def voicenote_exception_handler(request: Request, exc: VoiceNoteException):
    logger.warning(f"VoiceNoteException [{exc.status_code}]: {exc.message} on path {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


# Register API Routes
v1_prefix = settings.API_V1_STR
app.include_router(health_router, prefix=v1_prefix)
app.include_router(transcription_router, prefix=v1_prefix)
app.include_router(analysis_router, prefix=v1_prefix)
app.include_router(evaluation_router, prefix=v1_prefix)


@app.get("/", summary="Root Endpoint", include_in_schema=False)
async def root():
    return {
        "message": "Welcome to VoiceNote AI Backend API",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }

