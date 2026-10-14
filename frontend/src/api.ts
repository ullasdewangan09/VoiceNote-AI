import type {
  TranscriptionResponse,
  CombinedAnalysisResponse,
  EvaluationRequest,
  EvaluationResponse,
  HealthResponse,
} from './types';

// The Vite proxy forwards /api/* → http://localhost:8000/api/*
// so in production you'd set VITE_API_BASE_URL env var.
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, init);
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response body was not JSON — fall back to the HTTP status text
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health(): Promise<HealthResponse> {
    return request('/api/v1/health');
  },

  transcribe(file: File): Promise<TranscriptionResponse> {
    const fd = new FormData();
    fd.append('file', file);
    return request('/api/v1/transcribe', { method: 'POST', body: fd });
  },

  analyze(
    file: File,
    summarySentences: number,
    topKeywords: number
  ): Promise<CombinedAnalysisResponse> {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('summary_sentences', String(summarySentences));
    fd.append('top_keywords', String(topKeywords));
    return request('/api/v1/analyze', { method: 'POST', body: fd });
  },

  evaluate(body: EvaluationRequest): Promise<EvaluationResponse> {
    return request('/api/v1/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  },
};
