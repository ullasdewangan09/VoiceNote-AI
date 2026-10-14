import os
import tempfile
import pytest
import soundfile as sf
import numpy as np

from app.services.audio_service import AudioService
from app.utils.validators import (
    validate_file_extension,
    validate_file_size,
    AudioValidationError,
    FileTooLargeError,
)


def test_validate_file_extension_valid():
    """Verify valid extensions pass validation."""
    assert validate_file_extension("audio.wav") == "wav"
    assert validate_file_extension("recording.MP3") == "mp3"
    assert validate_file_extension("speech.flac") == "flac"


def test_validate_file_extension_invalid():
    """Verify invalid extensions raise AudioValidationError."""
    with pytest.raises(AudioValidationError) as exc_info:
        validate_file_extension("document.pdf")
    assert "Unsupported file extension" in str(exc_info.value.message)


def test_validate_file_size_empty():
    """Verify 0-byte file raises AudioValidationError."""
    with pytest.raises(AudioValidationError) as exc_info:
        validate_file_size(b"")
    assert "empty" in str(exc_info.value.message)


def test_validate_file_size_too_large(monkeypatch):
    """Verify file exceeding limit raises FileTooLargeError."""
    fake_bytes = b"0" * (26 * 1024 * 1024)  # 26 MB
    with pytest.raises(FileTooLargeError):
        validate_file_size(fake_bytes)


def test_audio_service_process_valid_upload():
    """Verify processing valid synthetic WAV file returns metadata."""
    temp_dir = tempfile.gettempdir()
    sample_path = os.path.join(temp_dir, "test_synth.wav")
    
    # Generate 1-second sine wave
    sr = 16000
    t = np.linspace(0, 1.0, sr, False)
    audio = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    sf.write(sample_path, audio, sr)

    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    result = AudioService.process_upload(file_bytes=file_bytes, filename="test_synth.wav")
    assert result["duration"] > 0
    assert result["sample_rate"] == 16000
    assert result["channels"] == 1
    assert os.path.exists(result["processed_path"])

    AudioService.cleanup_files(sample_path, result["raw_path"], result["processed_path"])


def test_audio_service_corrupted_file():
    """Verify corrupted non-audio bytes raise AudioValidationError."""
    fake_corrupted_bytes = b"CORRUPTED_AUDIO_HEADER_DATA_12345"
    with pytest.raises(AudioValidationError):
        AudioService.process_upload(file_bytes=fake_corrupted_bytes, filename="corrupt.wav")


def _write_opus_webm(path: str, duration: float = 1.0, sr: int = 16000) -> None:
    """Encode a sine tone to Opus-in-WebM, mimicking browser MediaRecorder output."""
    import av

    t = np.linspace(0, duration, int(sr * duration), False)
    audio = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

    container = av.open(path, "w", format="webm")
    stream = container.add_stream("libopus", rate=sr)
    stream.layout = "mono"
    frame = av.AudioFrame.from_ndarray(audio.reshape(1, -1), format="flt", layout="mono")
    frame.rate = sr
    for packet in stream.encode(frame):
        container.mux(packet)
    for packet in stream.encode(None):
        container.mux(packet)
    container.close()


def test_audio_service_process_webm_opus_upload():
    """Browser mic recordings are Opus-in-WebM; ensure they decode without system FFmpeg."""
    webm_path = os.path.join(tempfile.gettempdir(), "test_recording.webm")
    _write_opus_webm(webm_path)

    with open(webm_path, "rb") as f:
        file_bytes = f.read()

    result = AudioService.process_upload(file_bytes=file_bytes, filename="recording.webm")
    assert result["duration"] > 0
    assert result["sample_rate"] == 16000
    assert result["channels"] == 1
    assert os.path.exists(result["processed_path"])
    assert os.path.getsize(result["processed_path"]) > 0

    AudioService.cleanup_files(webm_path, result["raw_path"], result["processed_path"])
