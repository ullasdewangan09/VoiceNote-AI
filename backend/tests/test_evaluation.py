import pytest
from app.services.evaluation_service import EvaluationService
from app.utils.validators import EvaluationError


def test_wer_perfect_match():
    """Verify identical reference and prediction result in WER = 0.0."""
    ref = "Speech recognition using Whisper is highly accurate."
    pred = "Speech recognition using Whisper is highly accurate."
    res = EvaluationService.evaluate_transcription(ref, pred)

    assert res["wer"] == 0.0
    assert res["substitutions"] == 0
    assert res["deletions"] == 0
    assert res["insertions"] == 0
    assert res["hits"] == 7
    assert res["reference_word_count"] == 7


def test_wer_substitution():
    """Verify single word substitution calculation."""
    ref = "Cloud computing is scalable."
    pred = "Cloud computing was scalable."
    res = EvaluationService.evaluate_transcription(ref, pred)

    assert res["substitutions"] == 1
    assert res["deletions"] == 0
    assert res["insertions"] == 0
    assert res["wer"] == round(1 / 4, 4)


def test_wer_insertion():
    """Verify extra inserted word calculation."""
    ref = "Artificial intelligence transforms education."
    pred = "Artificial intelligence now transforms education."
    res = EvaluationService.evaluate_transcription(ref, pred)

    assert res["insertions"] == 1
    assert res["substitutions"] == 0
    assert res["deletions"] == 0
    assert res["wer"] == round(1 / 4, 4)


def test_wer_deletion():
    """Verify deleted word calculation."""
    ref = " Rahul needs to prepare the deployment documentation."
    pred = "Rahul needs to prepare deployment documentation."
    res = EvaluationService.evaluate_transcription(ref, pred)

    assert res["deletions"] == 1
    assert res["wer"] == round(1 / 7, 4)


def test_wer_empty_reference():
    """Verify empty reference throws EvaluationError."""
    with pytest.raises(EvaluationError):
        EvaluationService.evaluate_transcription("", "Some prediction")
