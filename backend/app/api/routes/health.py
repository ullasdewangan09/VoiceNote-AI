from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health Check"])


@router.get("/health", summary="Service Health Check")
async def health_check():
    """
    Returns the health status and metadata of the VoiceNote AI Backend service.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "model_size": settings.ASR_MODEL_SIZE,
        "device": settings.DEVICE,
        "compute_type": settings.COMPUTE_TYPE,
    }
