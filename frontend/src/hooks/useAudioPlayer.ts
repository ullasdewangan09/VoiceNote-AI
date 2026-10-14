import { useCallback, useRef, useState } from 'react';

type HandlerEntry = [string, EventListenerOrEventListenerObject];

export function useAudioPlayer() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const handlersRef = useRef<{ audio: HTMLAudioElement; handlers: HandlerEntry[] } | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);

  const detach = useCallback(() => {
    const current = handlersRef.current;
    if (current) {
      for (const [type, fn] of current.handlers) {
        current.audio.removeEventListener(type, fn);
      }
      current.audio.pause();
      current.audio.src = '';
      handlersRef.current = null;
    }
  }, []);

  const load = useCallback((src: string) => {
    detach();

    const audio = new Audio(src);
    audio.preload = 'metadata';

    const handlers: HandlerEntry[] = [];
    const on = (type: string, fn: EventListenerOrEventListenerObject) => {
      audio.addEventListener(type, fn);
      handlers.push([type, fn]);
    };

    on('loadedmetadata', () => setDuration(audio.duration));
    on('timeupdate', () => setCurrentTime(audio.currentTime));
    on('ended', () => setIsPlaying(false));

    handlersRef.current = { audio, handlers };
    audioRef.current = audio;
    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(false);
  }, [detach]);

  const togglePlay = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      audio.play();
      setIsPlaying(true);
    } else {
      audio.pause();
      setIsPlaying(false);
    }
  }, []);

  const seek = useCallback((time: number) => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  }, []);

  const changeRate = useCallback((rate: number) => {
    setPlaybackRate(rate);
    if (audioRef.current) audioRef.current.playbackRate = rate;
  }, []);

  const destroy = useCallback(() => {
    detach();
    audioRef.current = null;
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
  }, [detach]);

  return { isPlaying, currentTime, duration, playbackRate, load, togglePlay, seek, changeRate, destroy };
}