from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.transcription import TranscriptionResponse
from app.services.audio_service import AudioService
from app.services.asr_service import asr_service
from app.utils.validators import VoiceNoteException
from app.core.logging import logger

router = APIRouter(tags=["Transcription"])


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe Audio File",
    description="Upload an audio file (WAV, MP3, M4A, FLAC, OGG) to receive timestamped transcription and metadata."
)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    1. Receives audio file via UploadFile.
    2. Validates format and file size limit.
    3. Preprocesses and normalizes audio into 16kHz WAV format.
    4. Executes ASR using faster-whisper.
    5. Returns timestamped transcript segments and metadata.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file provided in request."
        )

    temp_files = []
    try:
        # Read file contents into bytes
        file_bytes = await file.read()

        # Audio Validation & Preprocessing
        audio_info = AudioService.process_upload(file_bytes=file_bytes, filename=file.filename)
        temp_files.extend([audio_info["raw_path"], audio_info["processed_path"]])

        # Run ASR Service
        asr_result = asr_service.transcribe(audio_path=audio_info["processed_path"])

        return TranscriptionResponse(
            language=asr_result["language"],
            duration=audio_info["duration"],
            text=asr_result["text"],
            segments=asr_result["segments"],
        )

    except VoiceNoteException as ve:
        logger.warning(f"Validation or domain error during transcription endpoint call: {ve.message}")
        raise HTTPException(status_code=ve.status_code, detail=ve.message)
    except Exception as e:
        logger.error(f"Unexpected error in /transcribe route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the audio transcription."
        )
    finally:
        # Ensure temporary files are cleaned up
        AudioService.cleanup_files(*temp_files)
