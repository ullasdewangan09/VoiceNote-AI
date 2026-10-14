from fastapi import APIRouter, HTTPException, status
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import EvaluationService
from app.utils.validators import EvaluationError
from app.core.logging import logger

router = APIRouter(tags=["ASR Evaluation"])


@router.post(
    "/evaluate",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Word Error Rate (WER)",
    description="Compares reference ground-truth transcript against predicted ASR transcript to compute WER, Substitutions, Deletions, and Insertions."
)
async def evaluate_transcription(req: EvaluationRequest):
    """
    Evaluates ASR accuracy using Word Error Rate (WER) formula:
    WER = (Substitutions + Deletions + Insertions) / Reference_Word_Count
    """
    try:
        res = EvaluationService.evaluate_transcription(
            reference=req.reference_transcript,
            prediction=req.predicted_transcript,
        )
        return EvaluationResponse(**res)
    except EvaluationError as ee:
        logger.warning(f"Evaluation request error: {ee.message}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ee.message)
    except Exception as e:
        logger.error(f"Unexpected error in /evaluate route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while performing WER evaluation."
        )
