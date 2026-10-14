import time
import math
from typing import Dict, Any, Optional
from faster_whisper import WhisperModel

from app.core.config import settings
from app.core.logging import logger
from app.utils.validators import ModelLoadError, TranscriptionError


class ASRService:
    """ASR Service utilizing faster-whisper for local speech recognition."""

    def __init__(self, model_size: Optional[str] = None, device: Optional[str] = None, compute_type: Optional[str] = None):
        self.model_size = model_size or settings.ASR_MODEL_SIZE
        self.device = device or settings.DEVICE
        self.compute_type = compute_type or settings.COMPUTE_TYPE
        self._model: Optional[WhisperModel] = None

    def load_model(self) -> WhisperModel:
        """Lazily loads the WhisperModel instance."""
        if self._model is None:
            logger.info(
                f"Loading faster-whisper model '{self.model_size}' "
                f"(device={self.device}, compute_type={self.compute_type})..."
            )
            start_time = time.time()
            try:
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                load_duration = time.time() - start_time
                logger.info(f"Model '{self.model_size}' loaded successfully in {load_duration:.2f} seconds.")
            except Exception as e:
                logger.error(f"Failed to load faster-whisper model: {e}")
                raise ModelLoadError(f"Failed to initialize Whisper model '{self.model_size}': {str(e)}")
        return self._model

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribes audio file at audio_path.
        Returns:
            {
                "language": str,
                "duration": float,
                "text": str,
                "segments": [
                    {
                        "start": float,
                        "end": float,
                        "text": str,
                        "avg_logprob": float,
                        "no_speech_prob": float,
                        "confidence": float
                    }
                ],
                "processing_time": float
            }
        """
        model = self.load_model()
        logger.info(f"Starting ASR transcription for '{audio_path}'...")
        start_time = time.time()

        try:
            segments_gen, info = model.transcribe(
                audio_path,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            segments = []
            full_text_list = []

            for seg in segments_gen:
                seg_text = seg.text.strip()
                if not seg_text:
                    continue

                full_text_list.append(seg_text)

                # Estimate segment confidence score from average log probability: p = exp(avg_logprob)
                avg_logprob = getattr(seg, "avg_logprob", None)
                no_speech_prob = getattr(seg, "no_speech_prob", None)
                
                confidence = None
                if avg_logprob is not None:
                    # Clip log probability to avoid math domain errors
                    confidence = round(float(math.exp(max(-10.0, avg_logprob))), 4)

                segments.append({
                    "start": round(float(seg.start), 2),
                    "end": round(float(seg.end), 2),
                    "text": seg_text,
                    "avg_logprob": round(float(avg_logprob), 4) if avg_logprob is not None else None,
                    "no_speech_prob": round(float(no_speech_prob), 4) if no_speech_prob is not None else None,
                    "confidence": confidence,
                })

            full_text = " ".join(full_text_list)
            processing_time = round(time.time() - start_time, 4)

            logger.info(
                f"Transcription finished in {processing_time:.2f}s. "
                f"Language='{info.language}', Segments={len(segments)}, Words={len(full_text.split())}"
            )

            return {
                "language": info.language or "en",
                "duration": round(float(info.duration), 2) if getattr(info, "duration", None) else 0.0,
                "text": full_text,
                "segments": segments,
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"ASR Transcription error for '{audio_path}': {e}")
            raise TranscriptionError(f"Error during audio transcription: {str(e)}")


# Shared singleton instance
asr_service = ASRService()
