import os
import numpy as np
import soundfile as sf

def generate_sample_wav(output_path: str, duration_sec: float = 3.0, sample_rate: int = 16000):
    """
    Generates a synthetic 16kHz mono WAV file containing clean multi-frequency tones
    simulating audio activity for testing audio preprocessing and pipeline endpoints.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)
    
    # Generate speech-like harmonic tone signal (440Hz + 880Hz + amplitude envelope)
    signal = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.25 * np.sin(2 * np.pi * 880 * t)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * 2 * t))
    audio_data = (signal * envelope).astype(np.float32)

    sf.write(output_path, audio_data, sample_rate)
    print(f"Generated sample WAV audio file at '{output_path}' ({duration_sec}s, {sample_rate}Hz)")

if __name__ == "__main__":
    target = os.path.join(os.path.dirname(__file__), "sample.wav")
    generate_sample_wav(target)
