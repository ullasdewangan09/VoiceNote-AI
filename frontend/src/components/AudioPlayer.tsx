import { useEffect } from 'react';
import styles from './AudioPlayer.module.css';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { formatTime } from '../utils';

interface Props {
  src: string;
  onTimeUpdate?: (time: number) => void;
  onSeekTo?: (seek: (t: number) => void) => void;
}

const RATES = [0.75, 1, 1.25, 1.5, 2];

export function AudioPlayer({ src, onTimeUpdate, onSeekTo }: Props) {
  const player = useAudioPlayer();

  useEffect(() => {
    player.load(src);
    return () => { player.destroy(); };
  }, [src]); // eslint-disable-line react-hooks/exhaustive-deps

  // Expose seek function upward
  useEffect(() => {
    onSeekTo?.(player.seek);
  }, [player.seek, onSeekTo]);

  // Propagate time
  useEffect(() => {
    onTimeUpdate?.(player.currentTime);
  }, [player.currentTime, onTimeUpdate]);

  const pct = player.duration > 0 ? (player.currentTime / player.duration) * 100 : 0;

  return (
    <div className={styles.player}>
      {/* Play / Pause */}
      <button className={styles.playBtn} onClick={player.togglePlay} aria-label={player.isPlaying ? 'Pause' : 'Play'}>
        {player.isPlaying ? (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" />
          </svg>
        ) : (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3" />
          </svg>
        )}
      </button>

      {/* Time */}
      <span className={styles.time}>{formatTime(player.currentTime)}</span>

      {/* Scrubber */}
      <div className={styles.trackWrapper}>
        <div className={styles.trackFill} style={{ width: `${pct}%` }} />
        <input
          type="range"
          min={0}
          max={player.duration || 100}
          step={0.1}
          value={player.currentTime}
          className={styles.slider}
          onChange={(e) => player.seek(parseFloat(e.target.value))}
          aria-label="Seek"
        />
      </div>

      <span className={styles.time}>{formatTime(player.duration)}</span>

      {/* Speed */}
      <select
        className="select-clean"
        value={player.playbackRate}
        onChange={(e) => player.changeRate(parseFloat(e.target.value))}
        aria-label="Playback speed"
      >
        {RATES.map((r) => (
          <option key={r} value={r}>{r}x</option>
        ))}
      </select>
    </div>
  );
}
