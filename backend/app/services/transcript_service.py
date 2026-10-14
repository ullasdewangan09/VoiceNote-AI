import re
from typing import Dict, Any


class TranscriptService:
    """Service providing core statistical metrics for text transcripts."""

    @staticmethod
    def analyze_transcript(text: str, duration: float = 0.0) -> Dict[str, Any]:
        """
        Computes text statistics: word_count, sentence_count, character_count, speaking_rate_wpm.
        """
        clean_text = text.strip()
        if not clean_text:
            return {
                "word_count": 0,
                "sentence_count": 0,
                "character_count": 0,
                "speaking_rate_wpm": 0.0,
            }

        # Calculate word count
        words = [w for w in re.split(r"\s+", clean_text) if w]
        word_count = len(words)

        # Calculate sentence count (splitting on sentence ending punctuation)
        sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if s.strip()]
        sentence_count = max(1, len(sentences))

        # Calculate character count
        character_count = len(clean_text)

        # Calculate Speaking Rate in Words Per Minute (WPM)
        speaking_rate_wpm = 0.0
        if duration > 0:
            speaking_rate_wpm = round((word_count / duration) * 60.0, 2)

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "character_count": character_count,
            "speaking_rate_wpm": speaking_rate_wpm,
        }
