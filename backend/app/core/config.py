from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration parameters."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # Server Settings
    PROJECT_NAME: str = "VoiceNote AI Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ALLOWED_ORIGINS: Union[List[str], str] = Field(
        default=["*"],
        description="Allowed CORS origins (comma-separated or list)"
    )

    # ASR Settings
    # Supported models: tiny, base, small, medium, large-v2, large-v3
    ASR_MODEL_SIZE: str = Field(default="small", description="Whisper model size to load")
    DEVICE: str = Field(default="cpu", description="Computation device: cpu or cuda")
    COMPUTE_TYPE: str = Field(default="int8", description="Quantization compute type: int8, float16, float32")

    # Audio Processing Settings
    MAX_FILE_SIZE_MB: int = Field(default=25, description="Maximum allowed audio file upload size in MB")
    ALLOWED_AUDIO_FORMATS: Union[List[str], str] = Field(
        default=["wav", "mp3", "m4a", "flac", "ogg", "webm", "opus"],
        description="Supported audio file extensions"
    )

    # NLP Analysis Defaults
    DEFAULT_SUMMARY_SENTENCES: int = Field(default=3, description="Default number of sentences in extractive summary")
    DEFAULT_KEYWORD_COUNT: int = Field(default=5, description="Default number of keywords to extract")

    @field_validator("ALLOWED_AUDIO_FORMATS", mode="before")
    @classmethod
    def parse_allowed_formats(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [fmt.strip().lower().lstrip(".") for fmt in v.split(",") if fmt.strip()]
        return [fmt.lower().lstrip(".") for fmt in v]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
