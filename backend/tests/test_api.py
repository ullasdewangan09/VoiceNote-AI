import io
import os
import tempfile
import numpy as np
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


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


def test_api_health():
    """Verify GET /api/v1/health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_evaluate_success():
    """Verify POST /api/v1/evaluate endpoint."""
    payload = {
        "reference_transcript": "Artificial intelligence transforms education",
        "predicted_transcript": "Artificial intelligence transforms education"
    }
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["wer"] == 0.0
    assert data["substitutions"] == 0


def test_api_evaluate_validation_error():
    """Verify POST /api/v1/evaluate returns 422 on empty reference."""
    payload = {
        "reference_transcript": "",
        "predicted_transcript": "Prediction"
    }
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code in {400, 422}


def test_api_keywords_endpoint():
    """Verify POST /api/v1/analyze/keywords endpoint."""
    payload = {
        "text": "Cloud computing and virtual machines enable distributed scaling.",
        "top_n": 3
    }
    response = client.post("/api/v1/analyze/keywords", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "keywords" in data
    assert len(data["keywords"]) <= 3


def test_api_summary_endpoint():
    """Verify POST /api/v1/analyze/summary endpoint."""
    payload = {
        "text": "Sentence one is clear. Sentence two explains further. Sentence three concludes.",
        "summary_sentences": 2
    }
    response = client.post("/api/v1/analyze/summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary_sentences"] == 2
    assert "summary_text" in data


def test_api_action_items_endpoint():
    """Verify POST /api/v1/analyze/action-items endpoint."""
    response = client.post("/api/v1/analyze/action-items", data={"text": "Rahul needs to review the PR by Friday."})
    assert response.status_code == 200
    data = response.json()
    assert data["total_detected"] == 1
    assert data["action_items"][0]["owner"] == "Rahul"


@patch("app.api.routes.transcription.asr_service.transcribe")
def test_api_transcribe_with_sample_wav(mock_transcribe):
    """Verify POST /api/v1/transcribe with sample WAV file."""
    mock_transcribe.return_value = {
        "language": "en",
        "duration": 3.0,
        "text": "Synthetic test speech transcript.",
        "segments": [{"start": 0.0, "end": 3.0, "text": "Synthetic test speech transcript.", "avg_logprob": -0.1, "no_speech_prob": 0.01, "confidence": 0.905}],
        "processing_time": 0.1
    }

    sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "samples", "sample.wav")
    assert os.path.exists(sample_path)

    with open(sample_path, "rb") as f:
        files = {"file": ("sample.wav", f, "audio/wav")}
        response = client.post("/api/v1/transcribe", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert "Synthetic test speech" in data["text"]
    assert len(data["segments"]) == 1


def test_api_transcribe_invalid_extension():
    """Verify POST /api/v1/transcribe returns 400 for unsupported extension."""
    files = {"file": ("document.txt", b"Hello world", "text/plain")}
    response = client.post("/api/v1/transcribe", files=files)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]


@patch("app.api.routes.transcription.asr_service.transcribe")
def test_api_transcribe_with_webm_recording(mock_transcribe):
    """Verify browser MediaRecorder WebM/Opus uploads are accepted, not marked corrupt."""
    mock_transcribe.return_value = {
        "language": "en",
        "duration": 1.0,
        "text": "Live microphone recording transcript.",
        "segments": [{"start": 0.0, "end": 1.0, "text": "Live microphone recording transcript.", "avg_logprob": -0.1, "no_speech_prob": 0.01, "confidence": 0.9}],
        "processing_time": 0.05
    }

    webm_path = os.path.join(tempfile.gettempdir(), "api_recording.webm")
    _write_opus_webm(webm_path)

    with open(webm_path, "rb") as f:
        files = {"file": ("recording.webm", f, "audio/webm")}
        response = client.post("/api/v1/transcribe", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "Live microphone recording" in data["text"]
    assert data["duration"] > 0


@patch("app.api.routes.analysis.asr_service.transcribe")
def test_api_analyze_with_sample_wav(mock_transcribe):
    """Verify POST /api/v1/analyze end-to-end pipeline response."""
    mock_transcribe.return_value = {
        "language": "en",
        "duration": 3.0,
        "text": "Rahul needs to deploy cloud services by Friday.",
        "segments": [{"start": 0.0, "end": 3.0, "text": "Rahul needs to deploy cloud services by Friday.", "avg_logprob": -0.1, "no_speech_prob": 0.01, "confidence": 0.95}],
        "processing_time": 0.15
    }

    sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "samples", "sample.wav")

    with open(sample_path, "rb") as f:
        files = {"file": ("sample.wav", f, "audio/wav")}
        response = client.post("/api/v1/analyze", files=files, data={"summary_sentences": 1, "top_keywords": 3})

    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert "keywords" in data
    assert "summary" in data
    assert "action_items" in data
    assert "analytics" in data
    assert data["analytics"]["real_time_factor_rtf"] >= 0.0
