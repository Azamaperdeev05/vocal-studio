import numpy as np
from typing import Tuple

def detect_vocal_start(
    audio_data: np.ndarray,
    sample_rate: int,
    window_ms: int = 100,
    threshold_ratio: float = 0.08,
    min_speech_duration_sec: float = 0.25,
    preroll_seconds: float = 0.35
) -> Tuple[int, float]:
    """
    Detects the onset timestamp where singing/vocals begin.
    Calculates sliding window RMS energy, finding sustained vocal energy
    and adding a small preroll to prevent cutting consonants/breath.
    
    Returns:
        (start_sample_index, start_seconds)
    """
    # Collapse multi-channel audio to mono for energy envelope
    if audio_data.ndim == 2:
        if audio_data.shape[0] < audio_data.shape[1]:
            mono = np.mean(np.abs(audio_data), axis=0)
        else:
            mono = np.mean(np.abs(audio_data), axis=1)
    else:
        mono = np.abs(audio_data)

    window_size = int(sample_rate * (window_ms / 1000.0))
    hop_size = max(1, window_size // 2)
    
    num_hops = max(1, (len(mono) - window_size) // hop_size)
    rms = np.zeros(num_hops)
    for i in range(num_hops):
        segment = mono[i * hop_size : i * hop_size + window_size]
        rms[i] = np.sqrt(np.mean(segment**2))
        
    peak_rms = np.max(rms) if len(rms) > 0 else 0
    if peak_rms <= 0:
        return 0, 0.0
        
    p95_rms = np.percentile(rms, 95)
    effective_peak = max(peak_rms * 0.7, p95_rms)
    threshold = effective_peak * threshold_ratio
    
    consecutive_needed = max(1, int(min_speech_duration_sec / (hop_size / sample_rate)))
    
    vocal_start_idx = 0
    consecutive = 0
    found = False
    
    for i, val in enumerate(rms):
        if val >= threshold:
            consecutive += 1
            if consecutive >= consecutive_needed:
                start_hop = max(0, i - consecutive)
                vocal_start_idx = start_hop * hop_size
                found = True
                break
        else:
            consecutive = 0
            
    if not found:
        vocal_start_idx = 0

    preroll_samples = int(preroll_seconds * sample_rate)
    vocal_start_idx = max(0, vocal_start_idx - preroll_samples)
    start_sec = vocal_start_idx / sample_rate
    
    return vocal_start_idx, start_sec

