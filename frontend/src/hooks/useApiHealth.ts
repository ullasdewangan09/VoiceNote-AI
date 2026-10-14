import { useCallback, useEffect, useState } from 'react';
import type { HealthResponse } from '../types';
import { api } from '../api';

type Status = 'checking' | 'online' | 'offline';

export function useApiHealth(pollMs = 15_000) {
  const [status, setStatus] = useState<Status>('checking');
  const [data, setData] = useState<HealthResponse | null>(null);

  const check = useCallback(async () => {
    try {
      const res = await api.health();
      setData(res);
      setStatus('online');
    } catch {
      setData(null);
      setStatus('offline');
    }
  }, []);

  useEffect(() => {
    const kick = setTimeout(check, 0);
    const interval = setInterval(check, pollMs);
    return () => {
      clearTimeout(kick);
      clearInterval(interval);
    };
  }, [check, pollMs]);

  return { status, data };
}
