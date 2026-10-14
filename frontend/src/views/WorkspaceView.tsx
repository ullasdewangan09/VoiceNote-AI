import { useCallback, useRef, useState } from 'react';
import styles from './WorkspaceView.module.css';
import { AudioSource } from '../components/AudioSource';
import { AudioPlayer } from '../components/AudioPlayer';
import { AnalyticsBar } from '../components/AnalyticsBar';
import { InsightsPanel } from '../components/InsightsPanel';
import { TranscriptPanel } from '../components/TranscriptPanel';
import { api } from '../api';
import type {
  CombinedAnalysisResponse,
  TranscriptionResponse,
  PipelineMode,
} from '../types';

type Result = CombinedAnalysisResponse | TranscriptionResponse;

interface Props {
  onSendToEval: (text: string) => void;
  show: (msg: string, type?: 'info' | 'success' | 'error') => void;
}

function isAnalysis(r: Result): r is CombinedAnalysisResponse {
  return 'analytics' in r;
}

export function WorkspaceView({ onSendToEval, show }: Props) {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [mode, setMode] = useState<PipelineMode>('analyze');
  const [summarySentences, setSummarySentences] = useState(3);
  const [topKeywords, setTopKeywords] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [runId, setRunId] = useState(0);

  // Pipeline elapsed timer
  const [elapsed, setElapsed] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Expose audio seek so TranscriptPanel can jump the player
  const seekRef = useRef<((t: number) => void) | null>(null);
  const handleSeekExposed = useCallback((seekFn: (t: number) => void) => {
    seekRef.current = seekFn;
  }, []);
  const handleSeek = useCallback((t: number) => {
    seekRef.current?.(t);
  }, []);

  function handleFileLoaded(file: File, url: string) {
    setAudioFile(file);
    setAudioUrl(url);
    setResult(null);
  }

  function handleClear() {
    setAudioFile(null);
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setResult(null);
  }

  async function runPipeline() {
    if (!audioFile) return;

    setLoading(true);
    setElapsed(0);
    const start = Date.now();
    timerRef.current = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 1000));
    }, 500);

    try {
      let res: Result;
      if (mode === 'analyze') {
        res = await api.analyze(audioFile, summarySentences, topKeywords);
      } else {
        res = await api.transcribe(audioFile);
      }
      setResult(res);
      setRunId((id) => id + 1);
      show('Processing complete', 'success');
    } catch (err) {
      show(`Error: ${(err as Error).message}`, 'error');
    } finally {
      clearInterval(timerRef.current!);
      setLoading(false);
    }
  }

  const canRun = !!audioFile && !loading;

  function fmtElapsed(s: number) {
    return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  }

  return (
    <div className={styles.root}>
      {/* Empty-state hero */}
      {!audioFile && !result && (
        <div className={styles.hero}>
          <span className={styles.heroEyebrow}>
            <span className="status-dot online" />
            faster-whisper ASR · 100% local · Zero external APIs
          </span>
          <h2 className={styles.heroTitle}>From raw audio to actionable notes</h2>
          <p className={styles.heroSub}>
            Upload a lecture or meeting recording, or record live with your mic. VoiceNote transcribes
            speech and automatically extracts summaries, keywords, and action items — entirely on-device.
          </p>
        </div>
      )}

      {/* Audio Source Card */}
      <div className={`card ${styles.sourceCard}`}>
        <AudioSource
          onFileLoaded={handleFileLoaded}
          onClear={handleClear}
          loadedFile={audioFile}
          show={show}
        />

        {/* Audio Player — shown only when a file is loaded */}
        {audioUrl && (
          <AudioPlayer
            src={audioUrl}
            onTimeUpdate={setCurrentTime}
            onSeekTo={handleSeekExposed}
          />
        )}

        {/* Pipeline Options Bar */}
        <div className={styles.configBar}>
          <div className={styles.configOptions}>
            <div className={styles.fieldGroup}>
              <label htmlFor="pipelineMode" className={styles.fieldLabel}>Pipeline</label>
              <select
                id="pipelineMode"
                className="select-clean"
                value={mode}
                onChange={e => setMode(e.target.value as PipelineMode)}
              >
                <option value="analyze">Full Analysis (NLP + ASR)</option>
                <option value="transcribe">Transcription Only</option>
              </select>
            </div>

            {mode === 'analyze' && (
              <>
                <div className={styles.fieldGroup}>
                  <label htmlFor="summaryN" className={styles.fieldLabel}>Summary sentences</label>
                  <input
                    id="summaryN"
                    type="number"
                    className="input-number"
                    min={1}
                    max={10}
                    value={summarySentences}
                    onChange={e => setSummarySentences(Math.max(1, Math.min(10, +e.target.value)))}
                  />
                </div>
                <div className={styles.fieldGroup}>
                  <label htmlFor="kwN" className={styles.fieldLabel}>Keywords</label>
                  <input
                    id="kwN"
                    type="number"
                    className="input-number"
                    min={1}
                    max={15}
                    value={topKeywords}
                    onChange={e => setTopKeywords(Math.max(1, Math.min(15, +e.target.value)))}
                  />
                </div>
              </>
            )}
          </div>

          <button className="btn btn-primary" onClick={runPipeline} disabled={!canRun} id="run-pipeline-btn">
            {loading ? (
              <>
                <span className="spinner" />
                Processing… {fmtElapsed(elapsed)}
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                {audioFile ? (mode === 'analyze' ? 'Run Full Analysis' : 'Transcribe Audio') : 'Select Audio First'}
              </>
            )}
          </button>
        </div>

        {/* Indeterminate progress strip */}
        {loading && (
          <div className={styles.progressWrap}>
            <div className="progress-bar-wrap">
              <div className="progress-bar-fill" />
            </div>
            <p className={styles.progressNote}>
              Sending to faster-whisper ASR engine — please wait…
            </p>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className={styles.results}>
          {/* Analytics strip — only for full analysis */}
          {isAnalysis(result) && (
            <AnalyticsBar analytics={result.analytics} />
          )}

          {/* Two-column grid: Insights (left) + Transcript (right) */}
          <div className={`${styles.resultsGrid}${isAnalysis(result) ? '' : ' ' + styles.resultsGridSingle}`}>
            {/* Insights column — only for full analysis */}
            {isAnalysis(result) && (
              <InsightsPanel key={`insights-${runId}`} result={result} show={show} />
            )}

            {/* Transcript always shown */}
            <TranscriptPanel
              key={`transcript-${runId}`}
              result={result}
              currentTime={currentTime}
              onSeek={handleSeek}
              onSendToEval={onSendToEval}
              show={show}
            />
          </div>
        </div>
      )}
    </div>
  );
}
