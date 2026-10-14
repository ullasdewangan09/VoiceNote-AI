import { useState } from 'react';
import styles from './TranscriptPanel.module.css';
import type { TranscriptSegment, CombinedAnalysisResponse, TranscriptionResponse } from '../types';
import { escapeRegExp, formatTime, formatSrtTime, downloadText } from '../utils';

type Result = CombinedAnalysisResponse | TranscriptionResponse;

interface Props {
  result: Result;
  currentTime: number;
  onSeek: (t: number) => void;
  onSendToEval: (text: string) => void;
  show: (msg: string, type?: 'info' | 'success' | 'error') => void;
}

function getSegments(r: Result): TranscriptSegment[] {
  if ('timestamps' in r) return r.timestamps;
  return r.segments;
}
function getFullText(r: Result): string {
  if ('transcript' in r) return r.transcript;
  return r.text;
}

export function TranscriptPanel({ result, currentTime, onSeek, onSendToEval, show }: Props) {
  const [query, setQuery] = useState('');
  const [exportOpen, setExportOpen] = useState(false);
  const segments = getSegments(result);
  const fullText = getFullText(result);
  const baseName = 'transcript';

  function matchesQuery(text: string): boolean {
    if (!query.trim()) return true;
    return text.toLowerCase().includes(query.toLowerCase());
  }

  function highlightText(text: string): React.ReactNode {
    if (!query.trim()) return text;
    const parts = text.split(new RegExp(`(${escapeRegExp(query)})`, 'gi'));
    return parts.map((p, i) =>
      p.toLowerCase() === query.toLowerCase()
        ? <mark key={i} className={styles.highlight}>{p}</mark>
        : p
    );
  }

  function copyText(text: string, label: string) {
    navigator.clipboard.writeText(text);
    show(`${label} copied to clipboard`, 'success');
  }

  function exportAs(format: string) {
    setExportOpen(false);
    const stem = baseName;
    if (format === 'txt') {
      downloadText(fullText, `${stem}.txt`);
    } else if (format === 'md') {
      let md = `# Transcript\n\n`;
      segments.forEach(s => { md += `**[${formatTime(s.start)} – ${formatTime(s.end)}]** ${s.text}\n\n`; });
      downloadText(md, `${stem}.md`, 'text/markdown');
    } else if (format === 'srt') {
      let srt = '';
      segments.forEach((s, i) => { srt += `${i + 1}\n${formatSrtTime(s.start)} --> ${formatSrtTime(s.end)}\n${s.text}\n\n`; });
      downloadText(srt, `${stem}.srt`);
    } else if (format === 'json') {
      downloadText(JSON.stringify(result, null, 2), `${stem}.json`, 'application/json');
    }
    show(`Exported ${stem}.${format}`, 'success');
  }

  const visible = segments.filter(s => matchesQuery(s.text));

  return (
    <div className={`card ${styles.card}`}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
          </svg>
          <span className={styles.title}>Transcript</span>
          <span className="badge">{segments.length} seg{segments.length !== 1 ? 's' : ''}</span>
        </div>

        <div className={styles.toolbar}>
          {/* Search */}
          <div className={styles.searchBox}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={styles.searchIcon}>
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              className={styles.searchInput}
              placeholder="Search…"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
            {query && (
              <button className={styles.clearSearch} onClick={() => setQuery('')}>&times;</button>
            )}
          </div>

          <button className="btn-ghost-sm" onClick={() => copyText(fullText, 'Transcript')}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
            Copy
          </button>

          {/* Export dropdown */}
          <div className={styles.dropdownWrap}>
            <button className="btn-ghost-sm" onClick={() => setExportOpen(v => !v)}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
              Export
            </button>
            {exportOpen && (
              <div className={styles.dropdownMenu} onMouseLeave={() => setExportOpen(false)}>
                {(['txt', 'md', 'srt', 'json'] as const).map(f => (
                  <button key={f} className={styles.dropdownItem} onClick={() => exportAs(f)}>
                    {f === 'txt' ? 'Plain Text (.txt)' : f === 'md' ? 'Markdown (.md)' : f === 'srt' ? 'Subtitles (.srt)' : 'Raw JSON (.json)'}
                  </button>
                ))}
              </div>
            )}
          </div>

          <button className="btn-ghost-sm" onClick={() => { onSendToEval(fullText); show('Transcript sent to WER Evaluator', 'info'); }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="m9 12 2 2 4-4" /></svg>
            Evaluate
          </button>
        </div>
      </div>

      {/* Segments list */}
      <div className={styles.segmentsList}>
        {visible.length === 0 && (
          <p className={styles.emptyHint}>{query ? `No segments match "${query}"` : 'No transcript segments.'}</p>
        )}
        {visible.map((seg, i) => {
          const isActive = currentTime >= seg.start && currentTime <= seg.end;
          return (
            <div
              key={i}
              className={`${styles.segment}${isActive ? ' ' + styles.active : ''}`}
              onClick={() => onSeek(seg.start)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && onSeek(seg.start)}
              aria-label={`Segment at ${formatTime(seg.start)}`}
            >
              <div className={styles.segHeader}>
                <span className={styles.tsPill}>
                  {formatTime(seg.start)} — {formatTime(seg.end)}
                </span>
                <div className={styles.segMeta}>
                  {seg.confidence != null && (
                    <span className={styles.conf}>{Math.round(seg.confidence * 100)}%</span>
                  )}
                  <button
                    className={styles.copySegBtn}
                    onClick={(e) => { e.stopPropagation(); copyText(seg.text, 'Segment'); }}
                    aria-label="Copy segment"
                    title="Copy segment text"
                  >
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
                  </button>
                </div>
              </div>
              <p className={styles.segText}>{highlightText(seg.text)}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
