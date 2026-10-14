import re
from typing import List, Dict, Any, Optional
import spacy

from app.core.logging import logger

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


class ActionItemService:
    """
    Service for extracting actionable tasks from meeting and lecture transcripts.
    
    Design Rationale:
    -----------------
    Uses rule-based NLP and Named Entity Recognition (NER) to locate task triggers
    (e.g., 'need to', 'must', 'should', 'prepare', 'submit').
    Strict non-hallucination constraint: Owner and deadline fields return None if not
    explicitly detected in the source sentence.
    """

    # Primary modal and action verb trigger regex patterns
    TRIGGER_PATTERNS = [
        r"\b(?:need|needs)\s+to\b",
        r"\bshould\b",
        r"\bmust\b",
        r"\bhave\s+to\b",
        r"\bwill\s+(?:prepare|submit|complete|review|deploy|update|follow up|assign|schedule|fix|send|create|build)\b",
        r"\b(?:please|make sure to)\s+(?:prepare|submit|complete|review|deploy|update|follow up|assign|schedule|fix|send|create|build)\b",
        r"\b(?:assigned|tasked)\s+to\b",
        r"\baction\s+item\b"
    ]

    # Common days and date expression triggers for deadline fallback regex
    DEADLINE_REGEX = r"\b(?:by\s+)?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|today|tomorrow|next week|end of day|EOD|this week|by\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b"

    @classmethod
    def detect_action_items(cls, text: str) -> List[Dict[str, Any]]:
        """
        Scans text for action items and extracts structured tasks with detected owners/deadlines.
        """
        clean_text = text.strip()
        if not clean_text:
            return []

        # Segment sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_text) if s.strip()]
        detected_items = []

        combined_trigger_re = re.compile("|".join(cls.TRIGGER_PATTERNS), re.IGNORECASE)
        deadline_re = re.compile(cls.DEADLINE_REGEX, re.IGNORECASE)

        for sentence in sentences:
            match = combined_trigger_re.search(sentence)
            if not match:
                continue

            owner: Optional[str] = None
            deadline: Optional[str] = None
            task: str = sentence
            confidence: float = 0.80

            # Use spaCy for NER entity extraction if available
            if nlp is not None:
                try:
                    doc = nlp(sentence)
                    
                    # 1. Detect Owner (PERSON / ORG)
                    persons = [ent.text for ent in doc.ents if ent.label_ in {"PERSON"}]
                    if persons:
                        owner = persons[0]
                    else:
                        # Fallback subject heuristic: look for capitalized proper noun before trigger
                        trigger_start = match.start()
                        prefix = sentence[:trigger_start].strip()
                        words = prefix.split()
                        if words and words[-1][0].isupper() and words[-1].lower() not in {"i", "we", "you", "they", "he", "she", "the", "a"}:
                            owner = words[-1]

                    # 2. Detect Deadline (DATE / TIME)
                    dates = [ent.text for ent in doc.ents if ent.label_ in {"DATE", "TIME"}]
                    if dates:
                        deadline = dates[0]
                except Exception as e:
                    logger.warning(f"spaCy NER processing warning on sentence '{sentence}': {e}")

            # Fallback deadline regex if spaCy returned None
            if not deadline:
                d_match = deadline_re.search(sentence)
                if d_match:
                    deadline = d_match.group(0).strip()

            # 3. Clean Task predicate phrase from sentence
            # Strip out leading subjects / modals to leave the action verb phrase
            trigger_end = match.end()
            raw_task = sentence[match.start():].strip()
            
            # If trigger was 'needs to', extract text after 'needs to'
            task_clean = re.sub(r"^(?:Rahul|John|Alex|\w+)?\s*(?:needs to|need to|should|must|have to|will|please|make sure to)\s*", "", raw_task, flags=re.IGNORECASE)
            if not task_clean:
                task_clean = raw_task

            # Strip trailing punctuation
            task_clean = task_clean.rstrip(".!?,")

            if owner or deadline:
                confidence = 0.92

            detected_items.append({
                "task": task_clean.capitalize(),
                "owner": owner,
                "deadline": deadline,
                "source_sentence": sentence,
                "confidence_score": round(confidence, 2)
            })

        return detected_items
