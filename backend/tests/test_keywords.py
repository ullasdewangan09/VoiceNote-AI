from app.services.keyword_service import KeywordService


def test_extract_keywords_basic():
    """Verify extracting key topics from cloud computing lecture text."""
    sample_text = (
        "Today we are discussing cloud computing and virtualization. "
        "Cloud computing enables scalable infrastructure and virtual machines. "
        "Containers and cloud services streamline software deployment in modern cloud computing environments."
    )
    keywords = KeywordService.extract_keywords(sample_text, top_n=3)
    assert len(keywords) > 0
    assert len(keywords) <= 3
    
    # Check that meaningful terms were extracted rather than stopwords
    lowercase_keywords = [k.lower() for k in keywords]
    assert any("cloud" in k for k in lowercase_keywords)


def test_extract_keywords_empty():
    """Verify empty text returns empty list."""
    assert KeywordService.extract_keywords("", top_n=5) == []


def test_extract_keywords_stopwords_filtered():
    """Verify conversational stopwords like 'um', 'yeah', 'like' are filtered out."""
    sample_text = "Um yeah like we know so basically cloud computing is important."
    keywords = KeywordService.extract_keywords(sample_text, top_n=5)
    for kw in keywords:
        assert kw.lower() not in {"um", "yeah", "like", "basically", "know"}
