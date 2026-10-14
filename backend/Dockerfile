FROM python:3.11-slim

# Install system dependencies (ffmpeg and build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy backend source code
COPY . .

# Set environment defaults
ENV PORT=8000
ENV DEVICE=cpu
ENV COMPUTE_TYPE=int8
ENV ASR_MODEL_SIZE=base

EXPOSE 8000

# Start FastAPI server using dynamic port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
