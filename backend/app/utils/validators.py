import os
from typing import Tuple
import soundfile as sf

from app.core.config import settings
from app.core.logging import logger
from app.utils.audio_io import probe_audio


class VoiceNoteException(Exception):
    """Base exception for VoiceNote AI domain errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AudioValidationError(VoiceNoteException):
    """Raised when uploaded audio fails format, size, or header validation."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code=status_code)


class FileTooLargeError(VoiceNoteException):
    """Raised when uploaded audio file exceeds maximum file size limit."""
    def __init__(self, message: str):
        super().__init__(message, status_code=413)


class TranscriptionError(VoiceNoteException):
    """Raised when ASR model fails during audio transcription."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ModelLoadError(VoiceNoteException):
    """Raised when ASR model loading fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class EvaluationError(VoiceNoteException):
    """Raised when WER evaluation inputs are invalid."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


def validate_file_extension(filename: str) -> str:
    """Validates if filename has an allowed audio file extension."""
    if not filename or "." not in filename:
        raise AudioValidationError("Uploaded file has no valid file extension.", status_code=400)

    ext = filename.rsplit(".", 1)[-1].lower()
    allowed_formats = [fmt.lower() for fmt in settings.ALLOWED_AUDIO_FORMATS]

    if ext not in allowed_formats:
        raise AudioValidationError(
            f"Unsupported file extension '.{ext}'. Allowed formats: {', '.join(allowed_formats)}",
            status_code=400
        )
    return ext


def validate_file_size(file_bytes: bytes) -> None:
    """Validates if file size is within limits and non-empty."""
    size_bytes = len(file_bytes)
    if size_bytes == 0:
        raise AudioValidationError("Uploaded file is empty (0 bytes).", status_code=400)

    if size_bytes > settings.max_file_size_bytes:
        size_mb = size_bytes / (1024 * 1024)
        raise FileTooLargeError(
            f"File size ({size_mb:.2f} MB) exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB."
        )


def validate_and_inspect_audio(file_path: str) -> Tuple[float, int, int]:
    """
    Verifies that the file at file_path is valid, readable audio and returns (duration, sample_rate, channels).
    Uses soundfile with fallback to PyAV.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        raise AudioValidationError("Audio file does not exist or is empty.", status_code=400)

    # WebM/Opus containers are not supported by soundfile; go straight to PyAV
    _sf_unsupported = {".webm", ".opus"}
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in _sf_unsupported:
        # First attempt: soundfile (fast header reading)
        try:
            info = sf.info(file_path)
            duration = info.duration
            sample_rate = info.samplerate
            channels = info.channels
            if duration <= 0:
                raise AudioValidationError("Audio duration is zero or negative.", status_code=400)
            return float(duration), int(sample_rate), int(channels)
        except Exception as sf_err:
            logger.warning(f"Soundfile inspection failed ({sf_err}). Trying PyAV fallback...")

    # Second attempt: PyAV (bundles FFmpeg) handles webm/opus and most formats without system FFmpeg
    try:
        duration, sample_rate, channels = probe_audio(file_path)
        if duration <= 0:
            raise AudioValidationError("Audio duration is zero or negative.", status_code=400)
        return float(duration), int(sample_rate), int(channels)
    except AudioValidationError:
        raise
    except Exception as av_err:
        logger.error(f"PyAV audio verification failed: {av_err}")
        raise AudioValidationError(
            "Uploaded file is corrupted or not a readable audio format.",
            status_code=400
        )
