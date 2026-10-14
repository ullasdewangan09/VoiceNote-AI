"""PyAV-based audio decoding utilities.

PyAV ships its own FFmpeg build, so these helpers can decode container formats
that libsndfile (used by soundfile/librosa) cannot read -- most importantly the
Opus-in-WebM files produced by the browser's MediaRecorder -- without requiring
a system FFmpeg installation.
"""

from typing import Tuple

import numpy as np
import av

from app.core.logging import logger


def _first_audio_stream(container: av.container.InputContainer):
    """Return the first audio stream of a container or raise ValueError."""
    audio_streams = [s for s in container.streams if s.type == "audio"]
    if not audio_streams:
        raise ValueError("File contains no audio stream.")
    return audio_streams[0]


def _stream_channels(stream) -> int:
    """Best-effort channel count lookup across PyAV versions."""
    try:
        channels = int(stream.channels)
    except Exception:
        channels = 0
    if not channels:
        try:
            channels = int(stream.codec_context.channels)
        except Exception:
            channels = 0
    return max(channels, 1)


def decode_audio_to_mono(file_path: str, target_sr: int = 16000) -> np.ndarray:
    """
    Decode any FFmpeg-supported audio file into a mono float32 numpy array
    resampled to target_sr using PyAV (no system FFmpeg required).
    """
    with av.open(file_path) as container:
        stream = _first_audio_stream(container)
        resampler = av.AudioResampler(format="flt", layout="mono", rate=target_sr)

        chunks = []
        for frame in container.decode(stream):
            for resampled in resampler.resample(frame):
                chunks.append(resampled.to_ndarray())
        for resampled in resampler.resample(None):
            chunks.append(resampled.to_ndarray())

    if not chunks:
        raise ValueError("Decoded audio contains no samples.")

    audio = np.concatenate(chunks, axis=1).reshape(-1).astype(np.float32)
    logger.debug(
        f"PyAV decoded '{file_path}' to {audio.shape[0]} samples @ {target_sr}Hz mono"
    )
    return audio


def probe_audio(file_path: str) -> Tuple[float, int, int]:
    """
    Inspect an audio file with PyAV without fully decoding it.

    Returns:
        (duration_seconds, sample_rate, channels)
    """
    with av.open(file_path) as container:
        stream = _first_audio_stream(container)
        sample_rate = int(stream.rate or 0)
        channels = _stream_channels(stream)

        duration = None
        if container.duration is not None:
            duration = container.duration / av.time_base
        elif stream.duration is not None and stream.time_base is not None:
            duration = float(stream.duration * stream.time_base)

        if duration is None or duration <= 0:
            fallback_sr = sample_rate or 16000
            samples = decode_audio_to_mono(file_path, target_sr=fallback_sr)
            duration = len(samples) / float(fallback_sr)

        if sample_rate <= 0:
            sample_rate = 16000

        return float(duration), sample_rate, channels
