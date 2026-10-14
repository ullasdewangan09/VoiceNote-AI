import type { DiffToken } from '../types';

/**
 * Computes a word-level alignment between reference and predicted
 * transcripts using dynamic programming (Levenshtein).
 * Returns an array of DiffTokens for rendering the alignment view.
 */
export function computeWordDiff(ref: string, pred: string): DiffToken[] {
  const normalize = (w: string) => w.toLowerCase().replace(/[^a-z0-9]/g, '');

  const refW = ref.split(/\s+/).filter(Boolean);
  const predW = pred.split(/\s+/).filter(Boolean);
  const n = refW.length;
  const m = predW.length;

  // DP table
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = 0; i <= n; i++) dp[i][0] = i;
  for (let j = 0; j <= m; j++) dp[0][j] = j;

  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (normalize(refW[i - 1]) === normalize(predW[j - 1])) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
      }
    }
  }

  // Backtrack
  let i = n;
  let j = m;
  const ops: DiffToken[] = [];

  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && normalize(refW[i - 1]) === normalize(predW[j - 1])) {
      ops.push({ type: 'hit', text: refW[i - 1] });
      i--;
      j--;
    } else if (i > 0 && j > 0 && dp[i][j] === dp[i - 1][j - 1] + 1) {
      // substitution: show pred word (what ASR said), then ref in parens
      ops.push({ type: 'sub', text: `${predW[j - 1]} (${refW[i - 1]})` });
      i--;
      j--;
    } else if (i > 0 && dp[i][j] === dp[i - 1][j] + 1) {
      ops.push({ type: 'del', text: refW[i - 1] });
      i--;
    } else {
      ops.push({ type: 'ins', text: predW[j - 1] });
      j--;
    }
  }

  ops.reverse();
  return ops;
}

export function getWerRating(wer: number): { label: string; color: string } {
  if (wer === 0) return { label: '100% Accurate — Perfect Match', color: 'var(--accent-green)' };
  if (wer < 0.1) return { label: 'Excellent Accuracy', color: 'var(--accent-green)' };
  if (wer < 0.25) return { label: 'Good Accuracy', color: 'var(--accent-green)' };
  if (wer < 0.4) return { label: 'Moderate Accuracy', color: 'var(--accent-amber)' };
  return { label: 'High Error Rate', color: 'var(--accent-red)' };
}
