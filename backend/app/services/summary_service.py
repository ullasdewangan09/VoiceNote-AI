import re
from typing import Dict, Any, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.logging import logger


class SummaryService:
    """
    Extractive Summarization Service.
    
    Design Rationale:
    -----------------
    This service performs deterministic, extractive summarization by scoring sentences using
    TF-IDF term importance and cosine sentence relationships. It does NOT use a generative LLM API.
    Sentences with high key information density are selected and presented in their original sequential
    order to preserve readability and context.
    """

    @classmethod
    def generate_summary(cls, text: str, summary_sentences: int = 3) -> Dict[str, Any]:
        """
        Generates an extractive summary containing the top `summary_sentences` most informative sentences.
        """
        clean_text = text.strip()
        if not clean_text:
            return {
                "summary_sentences": 0,
                "total_sentences": 0,
                "summary_text": "",
            }

        # 1. Segment text into sentences
        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_text) if s.strip()]
        if not raw_sentences:
            raw_sentences = [clean_text]

        total_sentences = len(raw_sentences)

        # If sentence count is smaller than or equal to requested summary length, return full text
        if total_sentences <= summary_sentences:
            return {
                "summary_sentences": total_sentences,
                "total_sentences": total_sentences,
                "summary_text": " ".join(raw_sentences),
            }

        try:
            # 2. Vectorize sentences using TF-IDF
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(raw_sentences)

            # 3. Calculate sentence importance scores: average TF-IDF weight of non-zero terms in sentence
            sentence_scores = []
            for i in range(total_sentences):
                row = tfidf_matrix.getrow(i)
                non_zero_count = row.nnz
                if non_zero_count > 0:
                    score = row.sum() / non_zero_count
                else:
                    score = 0.0
                sentence_scores.append((i, score))

            # 4. Rank sentences by importance score
            sentence_scores.sort(key=lambda x: x[1], reverse=True)

            # 5. Select top N sentence indices and sort them back into original chronological order
            selected_indices = [idx for idx, _ in sentence_scores[:summary_sentences]]
            selected_indices.sort()

            summary_list = [raw_sentences[idx] for idx in selected_indices]
            summary_text = " ".join(summary_list)

            return {
                "summary_sentences": len(summary_list),
                "total_sentences": total_sentences,
                "summary_text": summary_text,
            }

        except Exception as e:
            logger.error(f"Extractive summarization error: {e}")
            # Fallback: Return first N sentences
            fallback_sentences = raw_sentences[:summary_sentences]
            return {
                "summary_sentences": len(fallback_sentences),
                "total_sentences": total_sentences,
                "summary_text": " ".join(fallback_sentences),
            }
