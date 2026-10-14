import os
import tempfile
import soundfile as sf
import librosa
import numpy as np

from app.core.logging import logger
from app.utils.audio_io import decode_audio_to_mono
from app.utils.validators import (
    validate_file_extension,
    validate_file_size,
    validate_and_inspect_audio,
    AudioValidationError,
)


class AudioService:
    """Service handling audio file validation, conversion, and preprocessing."""

    @staticmethod
    def process_upload(file_bytes: bytes, filename: str) -> dict:
        """
        Validates file extension, size, reads audio metadata, and normalizes audio into a standard
        16kHz mono WAV file format for optimal ASR processing.
        Returns dictionary containing processed audio path and metadata.
        """
        logger.info(f"Received audio file upload: '{filename}' ({len(file_bytes)} bytes)")

        # 1. Validate Extension & Size
        ext = validate_file_extension(filename)
        validate_file_size(file_bytes)

        # 2. Save raw upload to temp file
        temp_dir = tempfile.gettempdir()
        temp_raw_path = os.path.join(temp_dir, f"raw_{os.urandom(8).hex()}.{ext}")
        
        with open(temp_raw_path, "wb") as f:
            f.write(file_bytes)

        try:
            # 3. Validate audio contents and read properties
            duration, orig_sr, channels = validate_and_inspect_audio(temp_raw_path)
            logger.info(
                f"Audio inspection passed: duration={duration:.2f}s, samplerate={orig_sr}Hz, channels={channels}"
            )

            # 4. Normalize & Convert to 16kHz Mono WAV if required
            processed_path = AudioService._preprocess_to_16k_mono_wav(
                raw_path=temp_raw_path,
                ext=ext,
                orig_sr=orig_sr,
                channels=channels
            )

            return {
                "raw_path": temp_raw_path,
                "processed_path": processed_path,
                "duration": duration,
                "sample_rate": 16000,
                "channels": 1,
                "filename": filename,
                "format": ext,
            }
        except Exception as e:
            # Clean up raw file if validation fails
            AudioService.cleanup_files(temp_raw_path)
            if isinstance(e, AudioValidationError):
                raise e
            logger.error(f"Failed during audio processing: {e}")
            raise AudioValidationError(f"Audio processing failure: {str(e)}")

    @staticmethod
    def _preprocess_to_16k_mono_wav(raw_path: str, ext: str, orig_sr: int, channels: int) -> str:
        """
        Resamples audio to 16kHz mono PCM float32 WAV suitable for Whisper.
        """
        temp_dir = tempfile.gettempdir()
        processed_path = os.path.join(temp_dir, f"proc_{os.urandom(8).hex()}.wav")

        try:
            # Load audio using PyAV (bundles FFmpeg, so handles webm/opus/mp3/etc.
            # without a system FFmpeg install); fall back to librosa if needed.
            try:
                audio = decode_audio_to_mono(raw_path, target_sr=16000)
            except Exception as av_err:
                logger.warning(f"PyAV decoding failed ({av_err}). Falling back to librosa...")
                audio, _ = librosa.load(raw_path, sr=16000, mono=True)

            # Peak amplitude normalization if signal is present
            max_val = np.max(np.abs(audio)) if audio.size else 0.0
            if max_val > 0:
                audio = audio / max_val

            sf.write(processed_path, audio, samplerate=16000, subtype='PCM_16')
            logger.info(f"Normalized audio written to '{processed_path}' (16kHz mono WAV)")
            return processed_path
        except Exception as e:
            logger.error(f"Audio normalization failed: {e}")
            # If conversion fails but raw file was already WAV, fallback to raw_path
            if ext == "wav":
                return raw_path
            raise AudioValidationError(f"Could not convert .{ext} audio file to WAV format: {str(e)}")

    @staticmethod
    def cleanup_files(*file_paths: str) -> None:
        """Helper to remove temporary audio files safely."""
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.debug(f"Cleaned up temporary file: {path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temp file '{path}': {e}")
