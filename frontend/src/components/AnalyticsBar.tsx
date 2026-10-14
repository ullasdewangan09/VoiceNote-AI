import styles from './AnalyticsBar.module.css';
import type { AnalyticsResponse } from '../types';

interface Props {
  analytics: AnalyticsResponse;
}

interface MetricProps {
  label: string;
  value: string;
  sub?: string;
  badge?: string;
  highlight?: boolean;
}

function Metric({ label, value, sub, badge, highlight }: MetricProps) {
  return (
    <div className={`${styles.metric}${highlight ? ' ' + styles.highlight : ''}`}>
      <span className={styles.label}>{label}</span>
      <div className={styles.valueRow}>
        <span className={styles.value}>{value}</span>
        {badge && <span className="badge badge-green">{badge}</span>}
      </div>
      {sub && <span className={styles.sub}>{sub}</span>}
    </div>
  );
}

export function AnalyticsBar({ analytics: a }: Props) {
  const rtfSpeed = a.real_time_factor_rtf > 0
    ? `${(1 / a.real_time_factor_rtf).toFixed(1)}× RT`
    : null;

  return (
    <div className={styles.bar}>
      <Metric
        label="Duration"
        value={`${a.duration.toFixed(1)}s`}
        sub="16kHz normalized"
      />
      <Metric
        label="Processing Time"
        value={a.processing_time > 0 ? `${a.processing_time.toFixed(2)}s` : '—'}
        sub={`Whisper ${a.language?.toUpperCase() ?? 'EN'}`}
      />
      <Metric
        label="Real-Time Factor"
        value={a.real_time_factor_rtf > 0 ? `${a.real_time_factor_rtf.toFixed(3)}x` : '—'}
        sub="Proc time / audio duration"
        badge={rtfSpeed ?? undefined}
        highlight
      />
      <Metric
        label="Speaking Rate"
        value={a.speaking_rate_wpm > 0 ? `${Math.round(a.speaking_rate_wpm)} WPM` : '—'}
        sub="Words per minute"
      />
      <Metric
        label="Words / Sentences"
        value={`${a.word_count}w · ${a.sentence_count}s`}
        sub={`Language: ${a.language?.toUpperCase() ?? 'EN'}`}
      />
    </div>
  );
}
