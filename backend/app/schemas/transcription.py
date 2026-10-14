from typing import List, Optional
from pydantic import BaseModel, Field


class SegmentSchema(BaseModel):
    """Timestamped segment schema from ASR model."""
    start: float = Field(..., description="Start timestamp in seconds")
    end: float = Field(..., description="End timestamp in seconds")
    text: str = Field(..., description="Transcribed text for this segment")
    avg_logprob: Optional[float] = Field(None, description="Average log probability of the segment tokens")
    no_speech_prob: Optional[float] = Field(None, description="Probability that the segment contains no speech")
    confidence: Optional[float] = Field(None, description="Estimated confidence score if available")


class TranscriptionResponse(BaseModel):
    """Response schema for transcription API endpoint."""
    language: str = Field(..., description="Detected audio language code (e.g., 'en')")
    duration: float = Field(..., description="Audio duration in seconds")
    text: str = Field(..., description="Full combined transcript text")
    segments: List[SegmentSchema] = Field(default_factory=list, description="List of timestamped transcript segments")
