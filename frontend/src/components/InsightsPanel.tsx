import { useState } from 'react';
import styles from './InsightsPanel.module.css';
import type { CombinedAnalysisResponse } from '../types';

interface Props {
  result: CombinedAnalysisResponse;
  show: (msg: string, type?: 'info' | 'success' | 'error') => void;
}

export function InsightsPanel({ result, show }: Props) {
  const [activeKeyword, setActiveKeyword] = useState<string | null>(null);
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set());

  async function copy(text: string, label: string) {
    try {
      await navigator.clipboard.writeText(text);
      show(`${label} copied`, 'success');
    } catch {
      show(`Could not copy ${label} to clipboard`, 'error');
    }
  }

  function toggleCheck(idx: number) {
    setCheckedItems(prev => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  }

  const actionChecklist = result.action_items
    .map(a => `- [ ] ${a.task}${a.owner ? ` (@${a.owner})` : ''}${a.deadline ? ` [${a.deadline}]` : ''}`)
    .join('\n');

  return (
    <div className={styles.column}>
      {/* Extractive Summary */}
      <div className={`card ${styles.card}`}>
        <div className={styles.cardHeader}>
          <div className={styles.titleGroup}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="21" y1="10" x2="3" y2="10" /><line x1="21" y1="6" x2="3" y2="6" /><line x1="21" y1="14" x2="3" y2="14" /><line x1="21" y1="18" x2="3" y2="18" />
            </svg>
            <span className={styles.cardTitle}>Extractive Summary</span>
          </div>
          <button className="btn-ghost-sm" onClick={() => copy(result.summary, 'Summary')}>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
            Copy
          </button>
        </div>
        <div className={styles.cardBody}>
          <blockquote className={styles.summary}>{result.summary || 'No summary available.'}</blockquote>
        </div>
      </div>

      {/* Action Items */}
      <div className={`card ${styles.card}`}>
        <div className={styles.cardHeader}>
          <div className={styles.titleGroup}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" /><path d="m9 12 2 2 4-4" />
            </svg>
            <span className={styles.cardTitle}>Action Items</span>
            <span className="badge">{result.action_items.length}</span>
          </div>
          {result.action_items.length > 0 && (
            <button className="btn-ghost-sm" onClick={() => copy(actionChecklist, 'Action items')}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
              Copy List
            </button>
          )}
        </div>
        <div className={styles.cardBody}>
          {result.action_items.length === 0 ? (
            <p className={styles.emptyHint}>No actionable tasks detected.</p>
          ) : (
            <div className={styles.actionList}>
              {result.action_items.map((item, idx) => (
                <div key={idx} className={`${styles.actionCard}${checkedItems.has(idx) ? ' ' + styles.done : ''}`}>
                  <label className={styles.actionRow}>
                    <input
                      type="checkbox"
                      checked={checkedItems.has(idx)}
                      onChange={() => toggleCheck(idx)}
                      className={styles.checkbox}
                    />
                    <span className={styles.actionTask}>{item.task}</span>
                  </label>
                  <div className={styles.actionTags}>
                    {item.owner && <span className="badge badge-blue">@{item.owner}</span>}
                    {item.deadline && (
                      <span className="badge badge-amber">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                          <rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                        {item.deadline}
                      </span>
                    )}
                    <span className={styles.confLabel}>{Math.round(item.confidence_score * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Keywords */}
      <div className={`card ${styles.card}`}>
        <div className={styles.cardHeader}>
          <div className={styles.titleGroup}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" />
            </svg>
            <span className={styles.cardTitle}>Keywords & Topics</span>
          </div>
        </div>
        <div className={styles.cardBody}>
          <div className={styles.tagCloud}>
            {result.keywords.map((kw) => (
              <button
                key={kw}
                className={`${styles.kwTag}${activeKeyword === kw ? ' ' + styles.kwActive : ''}`}
                onClick={() => setActiveKeyword(activeKeyword === kw ? null : kw)}
              >
                {kw}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
