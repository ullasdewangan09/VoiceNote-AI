FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY backend /app
RUN chown -R appuser:appuser /app

RUN mkdir -p /app/.cache && chown -R appuser:appuser /app/.cache
ENV HF_HOME=/app/.cache
ENV PYTHONUNBUFFERED=1

USER appuser

ENV PORT=7860
ENV DEVICE=cpu
ENV COMPUTE_TYPE=int8
ENV ASR_MODEL_SIZE=base

EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
