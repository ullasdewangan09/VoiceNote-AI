import re
from typing import Dict, Any
import jiwer

from app.core.logging import logger
from app.utils.validators import EvaluationError


class EvaluationService:
    """
    Service for calculating Word Error Rate (WER) and edit distance metrics.
    
    Mathematical Explanation:
    -------------------------
    Word Error Rate (WER) is the standard metric used to evaluate Automatic Speech Recognition (ASR) performance.
    
    Formula:
        WER = (Substitutions + Deletions + Insertions) / Reference_Word_Count
        
    Where:
    - Reference_Word_Count (N): Total number of words in ground-truth reference transcript (N = S + D + H).
    - Substitutions (S): Count of reference words incorrectly transcribed as a different word.
    - Deletions (D): Count of reference words missing from the prediction.
    - Insertions (I): Count of extra words present in prediction that were not in reference.
    - Hits (H): Count of correctly matched words (H = N - S - D).
    """

    @classmethod
    def evaluate_transcription(cls, reference: str, prediction: str) -> Dict[str, Any]:
        """
        Calculates WER and detailed error breakdown (Substitutions, Deletions, Insertions, Hits).
        """
        ref_clean = reference.strip()
        pred_clean = prediction.strip()

        if not ref_clean:
            raise EvaluationError("Reference transcript cannot be empty.")

        # Tokenize words, converting to lowercase and stripping punctuation
        ref_words = cls._tokenize(ref_clean)
        pred_words = cls._tokenize(pred_clean)

        N = len(ref_words)
        if N == 0:
            raise EvaluationError("Reference transcript must contain at least one valid word.")

        try:
            # 1. Primary evaluation using jiwer library process
            out = jiwer.process_words(ref_words, pred_words)

            substitutions = int(out.substitutions)
            deletions = int(out.deletions)
            insertions = int(out.insertions)
            hits = int(out.hits)
            wer = float(out.wer)

            # Round WER to 4 decimal places
            wer = round(wer, 4)

            logger.info(
                f"WER Evaluation complete: WER={wer} (S={substitutions}, D={deletions}, I={insertions}, H={hits}, N={N})"
            )

            return {
                "wer": wer,
                "substitutions": substitutions,
                "deletions": deletions,
                "insertions": insertions,
                "hits": hits,
                "reference_word_count": N,
                "explanation": "WER = (Substitutions + Deletions + Insertions) / Reference_Word_Count"
            }

        except Exception as e:
            logger.warning(f"jiwer evaluation encountered error: {e}. Falling back to dynamic programming Levenshtein solver...")
            return cls._calculate_wer_custom(ref_words, pred_words)

    @classmethod
    def _tokenize(cls, text: str) -> list:
        """Tokenizes text into lowercase word tokens excluding punctuation."""
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9']+\b", text)]

    @classmethod
    def _calculate_wer_custom(cls, ref_words: list, pred_words: list) -> Dict[str, Any]:
        """
        Fallback Levenshtein distance matrix alignment calculation.
        """
        r_len = len(ref_words)
        p_len = len(pred_words)

        # Initialize DP cost matrix
        dp = [[0] * (p_len + 1) for _ in range(r_len + 1)]

        for i in range(r_len + 1):
            dp[i][0] = i
        for j in range(p_len + 1):
            dp[0][j] = j

        for i in range(1, r_len + 1):
            for j in range(1, p_len + 1):
                if ref_words[i - 1] == pred_words[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    sub_cost = dp[i - 1][j - 1] + 1
                    del_cost = dp[i - 1][j] + 1
                    ins_cost = dp[i][j - 1] + 1
                    dp[i][j] = min(sub_cost, del_cost, ins_cost)

        # Backtrack to count S, D, I, H
        i, j = r_len, p_len
        S = D = I = H = 0

        while i > 0 or j > 0:
            if i > 0 and j > 0 and ref_words[i - 1] == pred_words[j - 1]:
                H += 1
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
                S += 1
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
                D += 1
                i -= 1
            elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
                I += 1
                j -= 1
            else:
                i -= 1
                j -= 1

        wer = round((S + D + I) / r_len, 4)

        return {
            "wer": wer,
            "substitutions": S,
            "deletions": D,
            "insertions": I,
            "hits": H,
            "reference_word_count": r_len,
            "explanation": "WER = (Substitutions + Deletions + Insertions) / Reference_Word_Count"
        }
