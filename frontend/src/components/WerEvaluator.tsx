import { useState } from 'react';
import styles from './WerEvaluator.module.css';
import { api } from '../api';
import type { EvaluationResponse } from '../types';
import { computeWordDiff, getWerRating } from '../utils/werDiff';
import { countWords } from '../utils';

interface Props {
  prefillPred?: string;
  show: (msg: string, type?: 'info' | 'success' | 'error') => void;
}

const DEMO_REF = 'Artificial intelligence is transforming education and scientific research across universities worldwide.';
const DEMO_PRED = 'Artificial intelligence transforms education and scientific research through universities worldwide.';

export function WerEvaluator({ prefillPred, show }: Props) {
  const [ref, setRef] = useState('');
  const [pred, setPred] = useState(prefillPred ?? '');
  const [result, setResult] = useState<EvaluationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!ref.trim()) { show('Enter the reference transcript (ground truth).', 'error'); return; }
    if (!pred.trim()) { show('Enter the predicted ASR transcript.', 'error'); return; }

    setLoading(true);
    try {
      const res = await api.evaluate({ reference_transcript: ref, predicted_transcript: pred });
      setResult(res);
    } catch (err) {
      show(`Evaluation failed: ${(err as Error).message}`, 'error');
    } finally {
      setLoading(false);
    }
  }

  function clear() {
    setRef(''); setPred(''); setResult(null);
  }

  function loadDemo() {
    setRef(DEMO_REF); setPred(DEMO_PRED); setResult(null);
  }

  const rating = result ? getWerRating(result.wer) : null;
  const tokens = result ? computeWordDiff(ref, pred) : [];

  return (
    <div className={`card ${styles.root}`}>
      {/* Header */}
      <div className={styles.evalHeader}>
        <div>
          <h1 className={styles.title}>Word Error Rate Evaluation</h1>
          <p className={styles.desc}>Compare a reference transcript against ASR output to measure accuracy and error distribution.</p>
        </div>
        <button className="btn-ghost-sm" onClick={loadDemo}>Load Example</button>
      </div>

      {/* Input grid */}
      <div className={styles.inputGrid}>
        <div className={styles.inputCol}>
          <div className={styles.fieldHeader}>
            <label htmlFor="evalRef" className={styles.fieldLabel}>Reference Transcript (Ground Truth)</label>
            <span className={styles.wordCount}>{countWords(ref)} words</span>
          </div>
          <textarea
            id="evalRef"
            className="textarea-clean"
            rows={7}
            placeholder="Paste the exact expected transcript here…"
            value={ref}
            onChange={e => setRef(e.target.value)}
          />
        </div>
        <div className={styles.inputCol}>
          <div className={styles.fieldHeader}>
            <label htmlFor="evalPred" className={styles.fieldLabel}>Predicted Transcript (ASR Output)</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              {prefillPred && (
                <button className={styles.pasteBtn} onClick={() => setPred(prefillPred)}>Use latest ASR</button>
              )}
              <span className={styles.wordCount}>{countWords(pred)} words</span>
            </div>
          </div>
          <textarea
            id="evalPred"
            className="textarea-clean"
            rows={7}
            placeholder="Paste the ASR recognised output here…"
            value={pred}
            onChange={e => setPred(e.target.value)}
          />
        </div>
      </div>

      {/* Action bar */}
      <div className={styles.actionBar}>
        <button className="btn btn-primary" onClick={run} disabled={loading}>
          {loading ? <span className="spinner" /> : (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <circle cx="12" cy="12" r="10" /><path d="m9 12 2 2 4-4" />
            </svg>
          )}
          {loading ? 'Calculating…' : 'Calculate Word Error Rate'}
        </button>
        <button className="btn btn-subtle" onClick={clear}>Clear</button>
      </div>

      {/* Results */}
      {result && (
        <div className={styles.results}>
          {/* WER hero */}
          <div className={styles.heroGrid}>
            <div className={styles.werDisplay}>
              <span className={styles.werLabel}>Word Error Rate</span>
              <span className={styles.werValue} style={{ color: rating?.color }}>{(result.wer * 100).toFixed(1)}%</span>
              <span className={styles.werRating} style={{ color: rating?.color }}>{rating?.label}</span>
            </div>

            <div className={styles.breakdown}>
              {[
                { label: 'Hits (H)', value: result.hits, cls: 'text-green', desc: 'Correct matches' },
                { label: 'Substitutions (S)', value: result.substitutions, cls: 'text-amber', desc: 'Replaced words' },
                { label: 'Deletions (D)', value: result.deletions, cls: 'text-red', desc: 'Omitted words' },
                { label: 'Insertions (I)', value: result.insertions, cls: 'text-blue', desc: 'Extra words' },
                { label: 'Reference Words (N)', value: result.reference_word_count, cls: '', desc: 'Ground-truth count' },
              ].map(m => (
                <div key={m.label} className={styles.bItem}>
                  <span className={styles.bLabel}>{m.label}</span>
                  <span className={`${styles.bVal} ${m.cls}`}>{m.value}</span>
                  <span className={styles.bDesc}>{m.desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Alignment diff */}
          <div className={`card ${styles.diffCard}`}>
            <div className={styles.diffHeader}>
              <span className={styles.diffTitle}>Token-Level Alignment</span>
              <div className={styles.legend}>
                {[
                  { cls: styles.chipHit, label: 'Correct' },
                  { cls: styles.chipSub, label: 'Substituted' },
                  { cls: styles.chipDel, label: 'Deleted' },
                  { cls: styles.chipIns, label: 'Inserted' },
                ].map(l => (
                  <span key={l.label} className={styles.legendItem}>
                    <span className={`${styles.legendDot} ${l.cls}`} />
                    {l.label}
                  </span>
                ))}
              </div>
            </div>

            <div className={styles.tokens}>
              {tokens.map((tok, i) => (
                <span
                  key={i}
                  className={`${styles.chip} ${
                    tok.type === 'hit' ? styles.chipHit :
                    tok.type === 'sub' ? styles.chipSub :
                    tok.type === 'del' ? styles.chipDel :
                    styles.chipIns
                  }`}
                >
                  {tok.text}
                </span>
              ))}
            </div>

            <div className={styles.formula}>
              <code>WER = (S + D + I) / N = ({result.substitutions} + {result.deletions} + {result.insertions}) / {result.reference_word_count} = {(result.wer * 100).toFixed(1)}%</code>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
