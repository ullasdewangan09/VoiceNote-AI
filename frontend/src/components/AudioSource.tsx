import { useRef, useState } from 'react';
import styles from './AudioSource.module.css';
import { useMicRecorder } from '../hooks/useMicRecorder';
import { formatBytes, formatTime } from '../utils';

interface Props {
  onFileLoaded: (file: File, objectUrl: string) => void;
  onClear: () => void;
  loadedFile: File | null;
  show: Toast;
}

// Tiny helper type so we don't import the whole hook type
type Toast = (msg: string, type?: 'info' | 'success' | 'error') => void;

type SourceTab = 'upload' | 'record';

const ALLOWED_EXT = ['wav', 'mp3', 'm4a', 'flac', 'ogg'];
const MAX_MB = 25;

export function AudioSource({ onFileLoaded, onClear, loadedFile, show }: Props) {
  const [tab, setTab] = useState<SourceTab>('upload');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const {
    state: recState,
    elapsed: recElapsed,
    canvasRef: recCanvasRef,
    start: startRec,
    stop: stopRec,
    cancel: cancelRec,
  } = useMicRecorder();

  function validate(file: File): string | null {
    const ext = file.name.split('.').pop()?.toLowerCase() ?? '';
    if (!ALLOWED_EXT.includes(ext) && !file.type.startsWith('audio/')) {
      return `Unsupported format (.${ext}). Supported: ${ALLOWED_EXT.join(', ').toUpperCase()}`;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      return `File too large (${(file.size / 1e6).toFixed(1)} MB > ${MAX_MB} MB)`;
    }
    return null;
  }

  function handleFile(file: File) {
    const err = validate(file);
    if (err) { show(err, 'error'); return; }
    onClear();
    const url = URL.createObjectURL(file);
    onFileLoaded(file, url);
    show(`Loaded ${file.name}`, 'success');
  }

  // Drag-and-drop
  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragActive(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  }

  // Sample audio
  async function loadSample() {
    show('Loading sample audio…', 'info');
    try {
      const res = await fetch('/sample.wav');
      if (!res.ok) throw new Error('Not found');
      const blob = await res.blob();
      handleFile(new File([blob], 'sample.wav', { type: 'audio/wav' }));
    } catch {
      show('Could not load /sample.wav — upload a file instead.', 'error');
    }
  }

  // Mic recording
  async function handleStartRec() {
    try {
      await startRec();
    } catch {
      show('Microphone access denied or unavailable.', 'error');
    }
  }

  async function handleStopRec() {
    const file = await stopRec();
    handleFile(file);
  }

  return (
    <div className={styles.root}>
      {/* Tab row */}
      <div className={styles.tabRow}>
        <div className="tab-group">
          <button className={`tab-item${tab === 'upload' ? ' active' : ''}`} onClick={() => { setTab('upload'); if (recState === 'recording') cancelRec(); }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            Upload File
          </button>
          <button className={`tab-item${tab === 'record' ? ' active' : ''}`} onClick={() => setTab('record')}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" y1="19" x2="12" y2="22" />
            </svg>
            Record Mic
          </button>
        </div>
        <button className="btn-ghost-sm" onClick={loadSample}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="5 3 19 12 5 21 5 3" /></svg>
          Load Sample
        </button>
      </div>

      {/* Upload tab */}
      {tab === 'upload' && (
        <div className={styles.body}>
          <div
            className={`${styles.dropzone}${dragActive ? ' ' + styles.dragActive : ''}`}
            tabIndex={0}
            role="button"
            aria-label="Click or drop audio file to upload"
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={ALLOWED_EXT.map(e => `.${e}`).join(',')}
              className={styles.hiddenInput}
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); e.target.value = ''; }}
            />
            <div className={styles.dropzoneIcon}>
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 18V5l12-2v13" /><circle cx="6" cy="18" r="3" /><circle cx="18" cy="16" r="3" />
              </svg>
            </div>
            <p className={styles.dropzoneMain}>Drop audio here or <span className={styles.browseLink}>browse</span></p>
            <p className={styles.dropzoneHint}>WAV · MP3 · M4A · FLAC · OGG — max {MAX_MB} MB</p>
          </div>
        </div>
      )}

      {/* Record tab */}
      {tab === 'record' && (
        <div className={styles.body}>
          <div className={styles.recContainer}>
            <div className={styles.recMeta}>
              <div className={`${styles.recStatusPill}${recState === 'recording' ? ' ' + styles.recActive : ''}`}>
                <span className={styles.recDot} />
                <span>{recState === 'recording' ? 'Recording live audio' : 'Microphone idle'}</span>
              </div>
              <span className={styles.recTimer}>{formatTime(recElapsed)}</span>
            </div>

            <canvas
              ref={recCanvasRef}
              width={540}
              height={60}
              className={styles.visualizer}
            />

            <div className={styles.recControls}>
              {recState !== 'recording' ? (
                <button className="btn btn-record" onClick={handleStartRec}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="8" /></svg>
                  Start Recording
                </button>
              ) : (
                <>
                  <button className="btn btn-stop" onClick={handleStopRec}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2" /></svg>
                    Stop & Use Recording
                  </button>
                  <button className="btn btn-subtle" onClick={cancelRec}>Cancel</button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Loaded file info bar */}
      {loadedFile && (
        <div className={styles.loadedBar}>
          <div className={styles.loadedInfo}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 18V5l12-2v13" /><circle cx="6" cy="18" r="3" /><circle cx="18" cy="16" r="3" />
            </svg>
            <span className={styles.loadedName}>{loadedFile.name}</span>
            <span className={styles.loadedSize}>{formatBytes(loadedFile.size)}</span>
          </div>
          <button className="icon-btn" onClick={onClear} title="Remove audio" aria-label="Remove audio">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
