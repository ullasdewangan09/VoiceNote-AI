import styles from './AppHeader.module.css';
import { useApiHealth } from '../hooks/useApiHealth';
import { useTheme } from '../hooks/useTheme';
import type { ActiveView } from '../types';

interface Props {
  activeView: ActiveView;
  onViewChange: (v: ActiveView) => void;
}

const MoonIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);
const SunIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1" x2="12" y2="3" />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
);
const WaveIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2v20M17 5v14M7 5v14M2 9v6M22 9v6" />
  </svg>
);

export function AppHeader({ activeView, onViewChange }: Props) {
  const { theme, toggle } = useTheme();
  const { status, data } = useApiHealth();

  const statusLabel =
    status === 'checking'
      ? 'Connecting…'
      : status === 'online'
      ? `Online · ${data?.model_size ?? 'ASR'} (${data?.compute_type ?? 'int8'})`
      : 'Backend Offline';

  return (
    <header className={styles.header}>
      {/* Brand */}
      <button
        type="button"
        className={styles.brand}
        onClick={() => onViewChange('workspace')}
        aria-label="Go to Workspace"
      >
        <div className={styles.brandMark}>
          <WaveIcon />
        </div>
        <div className={styles.brandText}>
          <span className={styles.brandName}>VoiceNote</span>
          <span className={styles.brandTag}>ASR Studio</span>
        </div>
      </button>

      {/* Tab navigation */}
      <nav className="tab-group" aria-label="Primary Navigation">
        <button
          className={`tab-item${activeView === 'workspace' ? ' active' : ''}`}
          onClick={() => onViewChange('workspace')}
          id="nav-workspace"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          Workspace
        </button>
        <button
          className={`tab-item${activeView === 'evaluator' ? ' active' : ''}`}
          onClick={() => onViewChange('evaluator')}
          id="nav-evaluator"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="m9 12 2 2 4-4" />
          </svg>
          WER Evaluator
        </button>
      </nav>

      {/* Right cluster */}
      <div className={styles.actions}>
        {/* API Status pill */}
        <div className={styles.statusPill}>
          <span className={`status-dot ${status}`} />
          <span className={styles.statusText}>{statusLabel}</span>
        </div>

        {/* Theme toggle */}
        <button className="icon-btn" onClick={toggle} aria-label="Toggle theme" title="Toggle light / dark">
          {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
        </button>
      </div>
    </header>
  );
}
