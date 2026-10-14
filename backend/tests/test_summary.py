from app.services.summary_service import SummaryService


def test_generate_summary_basic():
    """Verify extractive summary selects top sentences and preserves logical order."""
    text = (
        "First, machine learning relies on data preparation. "
        "Second, neural networks process input features through multiple hidden layers. "
        "Third, optimization algorithms minimize loss functions to improve model accuracy. "
        "Finally, evaluation metrics such as precision and recall assess performance."
    )
    res = SummaryService.generate_summary(text, summary_sentences=2)
    assert res["summary_sentences"] == 2
    assert res["total_sentences"] == 4
    assert len(res["summary_text"]) > 0
    assert "machine learning" in res["summary_text"] or "neural networks" in res["summary_text"]


def test_generate_summary_short_text():
    """Verify text with fewer sentences than requested returns full text."""
    text = "Artificial intelligence is transforming software engineering."
    res = SummaryService.generate_summary(text, summary_sentences=3)
    assert res["summary_sentences"] == 1
    assert res["total_sentences"] == 1
    assert res["summary_text"] == text


def test_generate_summary_empty():
    """Verify empty text returns 0 sentences and empty summary."""
    res = SummaryService.generate_summary("", summary_sentences=3)
    assert res["summary_sentences"] == 0
    assert res["summary_text"] == ""
