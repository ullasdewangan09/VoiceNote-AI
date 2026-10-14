---
title: VoiceNote AI Backend
emoji: 🎙️
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
---

# VoiceNote AI — Intelligent ASR-Based Lecture & Meeting Assistant Backend

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![ASR](https://img.shields.io/badge/ASR-faster--whisper-orange.svg)](https://github.com/SYSTRAN/faster-whisper)
[![Tests](https://img.shields.io/badge/Tests-Pytest%2033%2F33%20Passed-brightgreen.svg)]()

VoiceNote AI is an enterprise-grade, modular Automatic Speech Recognition (ASR) backend designed specifically for lectures, academic presentations, and corporate meeting recordings.

Unlike basic speech-to-text scripts, VoiceNote AI implements a full-fledged speech processing pipeline: audio validation & 16kHz mono normalization, faster-whisper speech recognition with segment-level timestamps, TF-IDF topic/keyword extraction, deterministic extractive summarization, rule-based & NER action item detection, Real-Time Factor (RTF) processing analytics, and Word Error Rate (WER) evaluation.

---

## 1. Features

- **Audio Validation & Preprocessing**: File format, extension, and file size checks. Automatic audio conversion and peak amplitude normalization into 16kHz mono WAV suitable for Whisper.
- **Local ASR Engine**: Powered by `faster-whisper` (CTranslate2 implementation of OpenAI's Whisper model). Runs 100% locally with zero external API dependencies.
- **Timestamped Transcripts**: Provides segment-level start/end timestamps, average log probability, and confidence scores.
- **Statistical Text Metrics**: Calculates word count, sentence count, character count, and estimated speaking rate in Words Per Minute (WPM).
- **Local Keyword & Topic Extraction**: Deterministic TF-IDF and spaCy N-gram phrase extraction with stopword filtering.
- **Extractive Summarization**: Selects top informative sentences using sentence-level TF-IDF vectorization while preserving chronological sentence order.
- **Action-Item Detection**: Uses transparent NLP rules and spaCy Named Entity Recognition (NER) to extract tasks, assigned owners, and deadlines without hallucination.
- **ASR Performance Analytics**: Measures wall-clock execution time and Real-Time Factor ($\text{RTF} = \frac{\text{processing\_time}}{\text{audio\_duration}}$).
- **ASR Accuracy Evaluation**: Calculates Word Error Rate (WER), Substitutions ($S$), Deletions ($D$), Insertions ($I$), and Hits ($H$).

---

## 2. Architecture

```
                    +-------------------------------------------------+
                    |               HTTP REST API Request             |
                    +-------------------------------------------------+
                                             |
                                             v
                    +-------------------------------------------------+
                    |              FastAPI Router Routing             |
                    |   /transcribe   |   /analyze   |   /evaluate    |
                    +-------------------------------------------------+
                                             |
                                             v
                    +-------------------------------------------------+
                    |                AudioService                     |
                    |   Validate Size/Ext -> Librosa/SoundFile        |
                    |   Resample 16kHz Mono -> Peak Normalization     |
                    +-------------------------------------------------+
                                             |
                                             v
                    +-------------------------------------------------+
                    |                 ASRService                      |
                    |   faster-whisper (CTranslate2 int8 CPU/CUDA)    |
                    |   Transcribe -> Segments & Timestamps           |
                    +-------------------------------------------------+
                                             |
                         +-------------------+-------------------+
                         |                   |                   |
                         v                   v                   v
              +--------------------+ +---------------+ +------------------+
              | TranscriptService  | |KeywordService | | SummaryService   |
              | WPM, Words, Sents  | |TF-IDF / Ngram | | Extractive TFIDF |
              +--------------------+ +---------------+ +------------------+
                         |                   |                   |
                         +-------------------+-------------------+
                                             |
                                             v
                    +-------------------------------------------------+
                    |              ActionItemService                  |
                    |   Modal Triggers + spaCy NER (Owner/Deadline)   |
                    +-------------------------------------------------+
                                             |
                                             v
                    +-------------------------------------------------+
                    |           Combined Analytics & Schema           |
                    |         Returns JSON Response Payload           |
                    +-------------------------------------------------+
```

---

## 3. Technology Stack

| Technology | Purpose | Selection Rationale |
| :--- | :--- | :--- |
| **Python 3.11+** | Core Runtime | High performance, excellent ML/ASR ecosystem support |
| **FastAPI** | REST API Framework | Automatic OpenAPI documentation (`/docs`), async I/O, Pydantic validation |
| **Pydantic v2** | Data Validation | Type-safe request/response payload validation and settings management |
| **faster-whisper** | ASR Engine | 4x faster than standard PyTorch Whisper with int8 quantization on CPU |
| **FFmpeg / Librosa** | Audio Preprocessing | Robust audio decoding, resampling to 16kHz mono, peak amplitude normalization |
| **spaCy & scikit-learn**| NLP & Vectorization | Lightweight local keyword extraction, sentence scoring, and NER without paid LLMs |
| **jiwer** | Evaluation Metric | Industry standard Word Error Rate (WER) calculation engine |
| **pytest** | Testing Framework | Comprehensive unit and integration test suite |

---

## 4. Installation & Environment Setup

### Prerequisites
- Python 3.11 or higher installed
- FFmpeg installed and accessible in system PATH

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/your-username/voicenote-ai.git
cd voicenote-ai

python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Linux / macOS:
source venv/bin/activate
```

### Step 2: Install Python Dependencies
```bash
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm
```

### Step 3: Configure Environment Variables
Copy `.env.example` to create your local `.env` configuration file:
```bash
cp backend/.env.example .env
```

`.env` default contents:
```ini
PROJECT_NAME="VoiceNote AI Backend"
API_V1_STR="/api/v1"
DEBUG=True
ASR_MODEL_SIZE=small
DEVICE=cpu
COMPUTE_TYPE=int8
MAX_FILE_SIZE_MB=25
ALLOWED_AUDIO_FORMATS="wav,mp3,m4a,flac,ogg"
DEFAULT_SUMMARY_SENTENCES=3
DEFAULT_KEYWORD_COUNT=5
```

---

## 5. FFmpeg Installation Guide

### Windows
1. Download FFmpeg build from [Gyan.dev FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/).
2. Extract zip folder to `C:\ffmpeg`.
3. Add `C:\ffmpeg\bin` to your System Environment Variables under `PATH`.
4. Verify via PowerShell: `ffmpeg -version`.

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y ffmpeg
ffmpeg -version
```

### macOS (Homebrew)
```bash
brew install ffmpeg
ffmpeg -version
```

---

## 6. Running the Backend Server

To launch the FastAPI backend application with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

Once started, access:
- **Interactive Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 7. API Reference & Curl Examples

### 1. Service Health Check
**GET** `/api/v1/health`

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**Response (HTTP 200)**:
```json
{
  "status": "healthy",
  "service": "VoiceNote AI Backend",
  "version": "1.0.0",
  "model_size": "small",
  "device": "cpu",
  "compute_type": "int8"
}
```

---

### 2. Audio Transcription
**POST** `/api/v1/transcribe`

Accepts audio file (`multipart/form-data`).

```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
  -F "file=@samples/sample.wav"
```

**Response (HTTP 200)**:
```json
{
  "language": "en",
  "duration": 3.0,
  "text": "Today we are discussing cloud computing infrastructure.",
  "segments": [
    {
      "start": 0.0,
      "end": 3.0,
      "text": "Today we are discussing cloud computing infrastructure.",
      "avg_logprob": -0.1524,
      "no_speech_prob": 0.0012,
      "confidence": 0.8586
    }
  ]
}
```

---

### 3. Combined Pipeline Analysis
**POST** `/api/v1/analyze`

Accepts audio file and optional form parameters `summary_sentences` and `top_keywords`.

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@samples/sample.wav" \
  -F "summary_sentences=2" \
  -F "top_keywords=3"
```

**Response (HTTP 200)**:
```json
{
  "transcript": "Rahul needs to prepare the deployment documentation by Friday. We should review cloud container architecture.",
  "language": "en",
  "timestamps": [
    {
      "start": 0.0,
      "end": 3.0,
      "text": "Rahul needs to prepare the deployment documentation by Friday.",
      "avg_logprob": -0.12,
      "no_speech_prob": 0.005,
      "confidence": 0.8869
    }
  ],
  "keywords": [
    "deployment documentation",
    "cloud container architecture",
    "rahul"
  ],
  "summary": "Rahul needs to prepare the deployment documentation by Friday.",
  "action_items": [
    {
      "task": "Prepare the deployment documentation by friday",
      "owner": "Rahul",
      "deadline": "Friday",
      "source_sentence": "Rahul needs to prepare the deployment documentation by Friday.",
      "confidence_score": 0.92
    }
  ],
  "analytics": {
    "duration": 3.0,
    "processing_time": 0.2415,
    "real_time_factor_rtf": 0.0805,
    "word_count": 14,
    "sentence_count": 2,
    "speaking_rate_wpm": 280.0,
    "segment_count": 1,
    "language": "en"
  }
}
```

---

### 4. Word Error Rate Evaluation
**POST** `/api/v1/evaluate`

```bash
curl -X POST "http://localhost:8000/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "reference_transcript": "Artificial intelligence is transforming education",
    "predicted_transcript": "Artificial intelligence transforms education"
  }'
```

**Response (HTTP 200)**:
```json
{
  "wer": 0.4,
  "substitutions": 1,
  "deletions": 1,
  "insertions": 0,
  "hits": 3,
  "reference_word_count": 5,
  "explanation": "WER = (Substitutions + Deletions + Insertions) / Reference_Word_Count"
}
```

---

## 8. ASR Evaluation & Word Error Rate (WER)

Word Error Rate (WER) is the primary quantitative standard used to evaluate speech recognition systems.

### Mathematical Definition
$$\text{WER} = \frac{S + D + I}{N}$$

Where:
- **$N$ (Reference Word Count)**: Total words in ground-truth transcript ($N = S + D + H$).
- **$S$ (Substitutions)**: Words incorrectly replaced by another word.
- **$D$ (Deletions)**: Words present in reference but omitted in predicted transcript.
- **$I$ (Insertions)**: Extra words added in predicted transcript not in reference.
- **$H$ (Hits)**: Correctly matched words.

---

## 9. Model Size Tradeoffs

| Model Size | Parameters | Required VRAM / RAM | Relative Speed | Target Use Case |
| :--- | :--- | :--- | :--- | :--- |
| `tiny` | 39 M | ~1 GB | ~10x | Fast unit testing, low-power IoT |
| `base` | 74 M | ~1 GB | ~7x | Quick quick drafts & testing |
| **`small` (Default)** | **244 M** | **~2 GB** | **~4x** | **Optimal balance for standard laptops** |
| `medium` | 769 M | ~5 GB | ~2x | High accuracy academic lectures |
| `large-v3` | 1550 M | ~10 GB | 1x | Enterprise accuracy with GPU acceleration |

---

## 10. Automated Testing

Run the full pytest test suite:

```bash
# Execute test suite
python -m pytest backend/tests -v
```

### Test Suite Summary
- `test_health.py`: Verifies `/health` & root `/` endpoint status codes and metadata.
- `test_audio.py`: Tests file extension validation, file size limit enforcement, empty files, corrupted byte detection.
- `test_asr.py`: Tests transcription logic, segment timestamps, confidence calculation, error handling.
- `test_keywords.py`: Verifies TF-IDF keyword extraction, top_n limits, custom conversational stopword filtering.
- `test_summary.py`: Tests extractive summarization sentence selection and order preservation.
- `test_action_items.py`: Verifies task detection, owner/deadline NER extraction, non-hallucination constraints.
- `test_evaluation.py`: Tests WER calculation, perfect match ($WER=0.0$), substitutions, insertions, deletions.
- `test_api.py`: End-to-end integration tests using FastAPI `TestClient`.

---

## 11. Known Limitations

1. **Speaker Diarization**: Current implementation transcribes full audio chronologically without separating individual speaker IDs (e.g. Speaker 1 vs Speaker 2).
2. **Background Noise**: Heavy background noise or overlapping speakers may reduce Whisper segment boundary precision.
3. **Domain-Specific Terminology**: Niche medical or rare technical jargon may experience higher substitution rates on smaller model sizes (`small` or `base`).

---

## 12. Future Improvements (Phase 2+)

- **Speaker Diarization**: Integration with `pyannote.audio` for multi-speaker identification.
- **Real-Time Streaming**: WebSocket endpoints for live microphone transcription.
- **Generative Summarization**: Optional local LLM support (e.g. Ollama / Llama 3) for abstractive summaries.
- **Frontend UI**: React/Next.js interface with waveform visualizer and interactive timestamp jumping.
