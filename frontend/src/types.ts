// API Types — mirrors the FastAPI Pydantic schemas exactly

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  avg_logprob: number;
  no_speech_prob: number;
  confidence: number;
}

export interface TranscriptionResponse {
  language: string;
  duration: number;
  text: string;
  segments: TranscriptSegment[];
}

export interface ActionItem {
  task: string;
  owner: string | null;
  deadline: string | null;
  source_sentence: string;
  confidence_score: number;
}

export interface AnalyticsResponse {
  duration: number;
  processing_time: number;
  real_time_factor_rtf: number;
  word_count: number;
  sentence_count: number;
  speaking_rate_wpm: number;
  segment_count: number;
  language: string;
}

export interface CombinedAnalysisResponse {
  transcript: string;
  language: string;
  timestamps: TranscriptSegment[];
  keywords: string[];
  summary: string;
  action_items: ActionItem[];
  analytics: AnalyticsResponse;
}

export interface EvaluationRequest {
  reference_transcript: string;
  predicted_transcript: string;
}

export interface EvaluationResponse {
  wer: number;
  substitutions: number;
  deletions: number;
  insertions: number;
  hits: number;
  reference_word_count: number;
  explanation: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  model_size: string;
  device: string;
  compute_type: string;
}

// App-level types
export type PipelineMode = 'analyze' | 'transcribe';
export type Theme = 'light' | 'dark';
export type ActiveView = 'workspace' | 'evaluator';
export type AudioSource = 'upload' | 'record';

export type ApiStatus = 'checking' | 'online' | 'offline';

export interface AppState {
  theme: Theme;
  activeView: ActiveView;
  apiStatus: ApiStatus;
  apiHealthData: HealthResponse | null;
}

// Word diff token for WER alignment visualization
export type TokenType = 'hit' | 'sub' | 'del' | 'ins';
export interface DiffToken {
  type: TokenType;
  text: string;
}
