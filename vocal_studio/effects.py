import numpy as np
from pedalboard import Pedalboard, Reverb, HighpassFilter, Compressor
from .config import VocalStudioConfig

def normalize_audio(audio_data: np.ndarray, target_db: float = -1.0) -> np.ndarray:
    """
    Normalizes audio data to target peak dBFS without clipping.
    """
    peak = np.max(np.abs(audio_data))
    if peak <= 0:
        return audio_data
    target_amplitude = 10 ** (target_db / 20.0)
    return audio_data * (target_amplitude / peak)

def apply_studio_reverb(
    audio_data: np.ndarray,
    sample_rate: int,
    config: VocalStudioConfig
) -> np.ndarray:
    """
    Applies professional studio vocal chain:
    - Highpass filter to eliminate sub-rumble
    - Dynamic compressor to smooth vocal delivery
    - Algorithmic Reverb with customizable space, damping, and stereo width
    - Peak normalization
    """
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=config.highpass_cutoff_hz),
        Compressor(
            threshold_db=config.compressor_threshold_db,
            ratio=config.compressor_ratio,
            attack_ms=10.0,
            release_ms=120.0
        ),
        Reverb(
            room_size=config.reverb_room_size,
            damping=config.reverb_damping,
            wet_level=config.reverb_wet_level,
            dry_level=config.reverb_dry_level,
            width=config.reverb_width,
            freeze_mode=0.0
        )
    ])
    
    processed = board(audio_data, sample_rate)
    return normalize_audio(processed, target_db=config.peak_target_db)
