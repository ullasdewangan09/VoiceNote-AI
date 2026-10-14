from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.transcription import SegmentSchema


class ActionItemSchema(BaseModel):
    """Schema for a single detected action item statement."""
    task: str = Field(..., description="Extracted core action task description")
    owner: Optional[str] = Field(None, description="Detected person/role assigned to the task (null if unidentified)")
    deadline: Optional[str] = Field(None, description="Detected time or deadline expression (null if unidentified)")
    source_sentence: str = Field(..., description="Original full transcript sentence")
    confidence_score: float = Field(..., description="Pattern detection confidence score (0.0 - 1.0)")


class ActionItemResponse(BaseModel):
    """Response schema for standalone action item detection endpoint."""
    total_detected: int = Field(..., description="Number of action items detected")
    action_items: List[ActionItemSchema] = Field(default_factory=list, description="Detected action items")


class KeywordRequest(BaseModel):
    """Request payload for standalone keyword extraction."""
    text: str = Field(..., min_length=1, description="Transcript text to analyze")
    top_n: Optional[int] = Field(5, ge=1, le=50, description="Number of keywords to extract")


class KeywordResponse(BaseModel):
    """Response schema for keyword extraction."""
    keywords: List[str] = Field(default_factory=list, description="Extracted top keywords/topics")


class SummaryRequest(BaseModel):
    """Request payload for standalone extractive summary."""
    text: str = Field(..., min_length=1, description="Transcript text to summarize")
    summary_sentences: Optional[int] = Field(3, ge=1, le=20, description="Number of sentences to include in summary")


class SummaryResponse(BaseModel):
    """Response schema for extractive summarization."""
    summary_sentences: int = Field(..., description="Number of sentences included in summary")
    total_sentences: int = Field(..., description="Total sentences present in original transcript")
    summary_text: str = Field(..., description="Extractive summary text preserving logical ordering")


class TranscriptStatsSchema(BaseModel):
    """Schema for raw transcript statistics."""
    word_count: int = Field(..., description="Total word count in transcript")
    sentence_count: int = Field(..., description="Total sentence count in transcript")
    character_count: int = Field(..., description="Total character count in transcript")
    speaking_rate_wpm: float = Field(..., description="Estimated speaking rate in Words Per Minute")


class AnalyticsResponse(BaseModel):
    """ASR & Transcript processing performance analytics schema."""
    duration: float = Field(..., description="Audio duration in seconds")
    processing_time: float = Field(..., description="Total processing wall time in seconds")
    real_time_factor_rtf: float = Field(..., description="Real Time Factor (processing_time / duration)")
    word_count: int = Field(..., description="Total word count")
    sentence_count: int = Field(..., description="Total sentence count")
    speaking_rate_wpm: float = Field(..., description="Speaking rate in WPM")
    segment_count: int = Field(..., description="Total timestamped ASR segments")
    language: str = Field(..., description="Detected audio language code")


class CombinedAnalysisResponse(BaseModel):
    """Complete pipeline response payload combining ASR, NLP, and performance metrics."""
    transcript: str = Field(..., description="Full text transcript")
    language: str = Field(..., description="Detected language code")
    timestamps: List[SegmentSchema] = Field(default_factory=list, description="Timestamped segments")
    keywords: List[str] = Field(default_factory=list, description="Extracted key topics and terms")
    summary: str = Field(..., description="Extractive transcript summary")
    action_items: List[ActionItemSchema] = Field(default_factory=list, description="Extracted action items")
    analytics: AnalyticsResponse = Field(..., description="ASR processing and transcript metrics")
