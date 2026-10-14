import time
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.schemas.analysis import (
    CombinedAnalysisResponse,
    AnalyticsResponse,
    KeywordRequest,
    KeywordResponse,
    SummaryRequest,
    SummaryResponse,
    ActionItemResponse,
)
from app.services.audio_service import AudioService
from app.services.asr_service import asr_service
from app.services.transcript_service import TranscriptService
from app.services.keyword_service import KeywordService
from app.services.summary_service import SummaryService
from app.services.action_item_service import ActionItemService
from app.utils.validators import VoiceNoteException
from app.core.logging import logger

router = APIRouter(tags=["Transcript Analysis"])


@router.post(
    "/analyze",
    response_model=CombinedAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Combined Audio Analysis Pipeline",
    description="Upload an audio file to run ASR transcription, keyword extraction, extractive summary, action item detection, and analytics."
)
async def analyze_audio(
    file: UploadFile = File(...),
    summary_sentences: Optional[int] = Form(3),
    top_keywords: Optional[int] = Form(5),
):
    """
    Executes complete end-to-end audio processing and NLP analysis pipeline:
    1. Audio validation & 16kHz mono WAV preprocessing.
    2. Whisper ASR transcription & timestamped segmentation.
    3. Transcript statistical metrics (Word count, sentence count, speaking rate WPM).
    4. Local TF-IDF / N-gram keyword extraction.
    5. Extractive summarization preserving original sentence ordering.
    6. Rule-based & NER action item detection.
    7. ASR performance analytics (Real Time Factor RTF).
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file provided in request."
        )

    pipeline_start = time.time()
    temp_files = []

    try:
        file_bytes = await file.read()

        # 1. Preprocess Audio
        audio_info = AudioService.process_upload(file_bytes=file_bytes, filename=file.filename)
        temp_files.extend([audio_info["raw_path"], audio_info["processed_path"]])
        duration = audio_info["duration"]

        # 2. Run ASR
        asr_result = asr_service.transcribe(audio_path=audio_info["processed_path"])
        full_text = asr_result["text"]
        language = asr_result["language"]
        segments = asr_result["segments"]
        asr_processing_time = asr_result["processing_time"]

        # 3. Transcript Statistics
        stats = TranscriptService.analyze_transcript(text=full_text, duration=duration)

        # 4. Keyword Extraction
        num_keywords = top_keywords if top_keywords and top_keywords > 0 else 5
        keywords = KeywordService.extract_keywords(text=full_text, top_n=num_keywords)

        # 5. Extractive Summarization
        num_summary = summary_sentences if summary_sentences and summary_sentences > 0 else 3
        summary_res = SummaryService.generate_summary(text=full_text, summary_sentences=num_summary)

        # 6. Action Item Detection
        action_items = ActionItemService.detect_action_items(text=full_text)

        # 7. Compute Analytics
        total_pipeline_time = round(time.time() - pipeline_start, 4)
        rtf = round(total_pipeline_time / duration, 4) if duration > 0 else 0.0

        analytics = AnalyticsResponse(
            duration=duration,
            processing_time=total_pipeline_time,
            real_time_factor_rtf=rtf,
            word_count=stats["word_count"],
            sentence_count=stats["sentence_count"],
            speaking_rate_wpm=stats["speaking_rate_wpm"],
            segment_count=len(segments),
            language=language,
        )

        return CombinedAnalysisResponse(
            transcript=full_text,
            language=language,
            timestamps=segments,
            keywords=keywords,
            summary=summary_res["summary_text"],
            action_items=action_items,
            analytics=analytics,
        )

    except VoiceNoteException as ve:
        logger.warning(f"Domain validation error during /analyze: {ve.message}")
        raise HTTPException(status_code=ve.status_code, detail=ve.message)
    except Exception as e:
        logger.error(f"Unexpected error in /analyze route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during transcript analysis."
        )
    finally:
        AudioService.cleanup_files(*temp_files)


@router.post(
    "/analyze/keywords",
    response_model=KeywordResponse,
    summary="Extract Keywords from Text",
    description="Extract key topics/terms from raw text payload without audio."
)
async def extract_keywords_route(req: KeywordRequest):
    """Extract top keywords from provided text string."""
    keywords = KeywordService.extract_keywords(text=req.text, top_n=req.top_n or 5)
    return KeywordResponse(keywords=keywords)


@router.post(
    "/analyze/summary",
    response_model=SummaryResponse,
    summary="Generate Extractive Summary from Text",
    description="Generate an extractive text summary without audio."
)
async def extract_summary_route(req: SummaryRequest):
    """Generate extractive summary from provided text string."""
    summary_res = SummaryService.generate_summary(text=req.text, summary_sentences=req.summary_sentences or 3)
    return SummaryResponse(
        summary_sentences=summary_res["summary_sentences"],
        total_sentences=summary_res["total_sentences"],
        summary_text=summary_res["summary_text"],
    )


@router.post(
    "/analyze/action-items",
    response_model=ActionItemResponse,
    summary="Detect Action Items from Text",
    description="Detect action items from raw text payload without audio."
)
async def extract_action_items_route(text: str = Form(...)):
    """Detect action items from provided text string."""
    action_items = ActionItemService.detect_action_items(text=text)
    return ActionItemResponse(
        total_detected=len(action_items),
        action_items=action_items,
    )
