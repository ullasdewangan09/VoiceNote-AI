import re
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
import spacy

from app.core.logging import logger

# Lazy load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


class KeywordService:
    """
    Service for local keyword and topic extraction using lightweight TF-IDF and N-gram term analysis.
    
    Design Rationale:
    -----------------
    1. Zero External Paid APIs: Operates 100% locally with deterministic mathematical scoring (TF-IDF).
    2. High Performance: Low latency, predictable memory usage, and no network dependencies.
    3. Scalable: Uses term frequency-inverse document frequency over unigrams & bigrams combined
       with English stopword filtering and spaCy POS tagging / noun-phrase extraction where available.
    """

    # Custom domain stopwords to supplement standard English stopwords
    CUSTOM_STOPWORDS = {
        "yeah", "um", "uh", "like", "know", "mean", "right", "okay", "so", "well",
        "going", "think", "said", "say", "saying", "get", "got", "also", "one", "thing",
        "basically", "really", "actually", "just", "yes", "no"
    }

    @classmethod
    def extract_keywords(cls, text: str, top_n: int = 5) -> List[str]:
        """
        Extracts the top_n most important keywords/keyphrases from text.
        """
        clean_text = text.strip()
        if not clean_text:
            return []

        # Combine default sklearn ENGLISH_STOP_WORDS with custom conversational stopwords
        stop_words = list(ENGLISH_STOP_WORDS.union(cls.CUSTOM_STOPWORDS))

        extracted_keywords = []

        # 1. Try spaCy noun chunk & entity extraction combined with frequency if spaCy is available
        if nlp is not None:
            try:
                doc = nlp(clean_text)
                phrase_counts = {}

                # Extract Named Entities (ORG, PRODUCT, GPE, EVENT, LAW, NORP)
                for ent in doc.ents:
                    if ent.label_ in {"ORG", "PRODUCT", "GPE", "EVENT", "LAW", "WORK_OF_ART", "PERSON"}:
                        term = ent.text.strip().lower()
                        if len(term) > 2 and term not in stop_words:
                            phrase_counts[term] = phrase_counts.get(term, 0) + 3

                # Extract Noun Chunks (e.g. "cloud computing", "virtual machines")
                for chunk in doc.noun_chunks:
                    # Clean chunk text by filtering out stop words and determiners
                    words = [
                        token.text.lower() for token in chunk
                        if not token.is_stop and not token.is_punct and len(token.text) > 2
                        and token.text.lower() not in stop_words
                    ]
                    if words:
                        phrase = " ".join(words)
                        phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

                # Sort by count frequency
                sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
                for phrase, _ in sorted_phrases:
                    if phrase not in extracted_keywords:
                        extracted_keywords.append(phrase)
                    if len(extracted_keywords) >= top_n:
                        return extracted_keywords[:top_n]
            except Exception as e:
                logger.warning(f"spaCy keyword extraction encountered warning: {e}. Falling back to TF-IDF vectorization...")

        # 2. Fallback or primary TF-IDF N-gram extraction using scikit-learn
        try:
            sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if len(s.strip()) > 5]
            if not sentences:
                sentences = [clean_text]

            vectorizer = TfidfVectorizer(
                stop_words=stop_words,
                ngram_range=(1, 2),  # Extract unigrams and bigrams (e.g. "cloud", "cloud computing")
                max_features=100,
                token_pattern=r"(?u)\b[a-zA-Z]{3,}\b"
            )

            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()

            # Sum TF-IDF scores across sentences
            scores = tfidf_matrix.sum(axis=0).A1
            word_score_tuples = list(zip(feature_names, scores))
            word_score_tuples.sort(key=lambda x: x[1], reverse=True)

            for word, _ in word_score_tuples:
                if word not in extracted_keywords:
                    extracted_keywords.append(word)
                if len(extracted_keywords) >= top_n:
                    break

        except Exception as e:
            logger.error(f"TF-IDF keyword extraction error: {e}")
            # Final fallback: Simple word frequency
            words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", clean_text)]
            freq = {}
            for w in words:
                if w not in stop_words:
                    freq[w] = freq.get(w, 0) + 1
            sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            extracted_keywords = [w for w, _ in sorted_words[:top_n]]

        return extracted_keywords[:top_n]
