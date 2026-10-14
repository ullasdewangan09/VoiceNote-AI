import os
import pytest
from unittest.mock import MagicMock, patch

from app.services.asr_service import ASRService
from app.utils.validators import TranscriptionError, ModelLoadError


class DummySegment:
    def __init__(self, start, end, text, avg_logprob=-0.2, no_speech_prob=0.01):
        self.start = start
        self.end = end
        self.text = text
        self.avg_logprob = avg_logprob
        self.no_speech_prob = no_speech_prob


class DummyInfo:
    def __init__(self, language="en", duration=5.0):
        self.language = language
        self.duration = duration


def test_asr_service_transcribe_mocked():
    """Verify ASRService returns structured transcript result from segments."""
    mock_model = MagicMock()
    mock_segments = [
        DummySegment(0.0, 2.5, "Welcome to cloud computing."),
        DummySegment(2.5, 5.0, "Today we will discuss virtualization.")
    ]
    mock_info = DummyInfo(language="en", duration=5.0)
    mock_model.transcribe.return_value = (mock_segments, mock_info)

    asr = ASRService(model_size="tiny")
    asr._model = mock_model  # Bypass actual model loading for unit test

    res = asr.transcribe("fake_path.wav")

    assert res["language"] == "en"
    assert res["duration"] == 5.0
    assert "Welcome to cloud computing" in res["text"]
    assert len(res["segments"]) == 2
    assert res["segments"][0]["start"] == 0.0
    assert res["segments"][0]["end"] == 2.5
    assert res["segments"][0]["confidence"] is not None
    assert res["processing_time"] >= 0.0


def test_asr_service_failure_raises_transcription_error():
    """Verify transcription failure raises domain TranscriptionError."""
    mock_model = MagicMock()
    mock_model.transcribe.side_effect = Exception("Model runtime error")

    asr = ASRService(model_size="tiny")
    asr._model = mock_model

    with pytest.raises(TranscriptionError) as exc_info:
        asr.transcribe("fake_path.wav")
    assert "Error during audio transcription" in str(exc_info.value.message)
