from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    """Payload for WER (Word Error Rate) evaluation."""
    reference_transcript: str = Field(..., min_length=1, description="Ground truth reference transcript text")
    predicted_transcript: str = Field(..., description="ASR model predicted transcript text")


class EvaluationResponse(BaseModel):
    """Response schema for Word Error Rate calculation."""
    wer: float = Field(..., description="Word Error Rate ( (S + D + I) / N )")
    substitutions: int = Field(..., description="Number of word substitutions (S)")
    deletions: int = Field(..., description="Number of deleted words (D)")
    insertions: int = Field(..., description="Number of inserted words (I)")
    hits: int = Field(..., description="Number of correctly matched words (H)")
    reference_word_count: int = Field(..., description="Total reference word count (N)")
    explanation: str = Field(
        "WER = (Substitutions + Deletions + Insertions) / Reference_Word_Count",
        description="Mathematical formula used for WER calculation"
    )
