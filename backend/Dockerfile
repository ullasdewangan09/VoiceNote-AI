FROM python:3.11-slim

# Install system dependencies (ffmpeg and build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security and Hugging Face Spaces compatibility
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy backend source code & set permissions
COPY . .
RUN chown -R appuser:appuser /app

# Model cache directory for appuser
RUN mkdir -p /app/.cache && chown -R appuser:appuser /app/.cache
ENV HF_HOME=/app/.cache
ENV PYTHONUNBUFFERED=1

USER appuser

# Set environment defaults (7860 is HF Spaces standard, PORT env overrides if set)
ENV PORT=7860
ENV DEVICE=cpu
ENV COMPUTE_TYPE=int8
ENV ASR_MODEL_SIZE=base

EXPOSE 7860

# Start FastAPI server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
