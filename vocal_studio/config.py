from dataclasses import dataclass
from typing import Optional

@dataclass
class VocalStudioConfig:
    # YouTube / File Download
    audio_format: str = "wav"
    output_dir: str = "./output"
    
    # Demucs Separation
    demucs_model: str = "htdemucs"
    device: str = "cpu"
    two_stems: str = "vocals"
    
    # Vocal Detection / Trimming
    trim_to_vocal_start: bool = True
    preroll_seconds: float = 0.35
    detection_window_ms: int = 100
    detection_threshold_ratio: float = 0.08
    min_speech_duration_sec: float = 0.25
    manual_start_seconds: Optional[float] = None
    
    # Studio Effects & Reverb
    enable_reverb: bool = True
    highpass_cutoff_hz: float = 80.0
    compressor_threshold_db: float = -16.0
    compressor_ratio: float = 2.5
    reverb_room_size: float = 0.68
    reverb_damping: float = 0.45
    reverb_wet_level: float = 0.35
    reverb_dry_level: float = 0.85
    reverb_width: float = 1.0
    peak_target_db: float = -1.0
    
    # Export formats
    export_mp3: bool = True
    export_wav: bool = True
    mp3_bitrate: str = "320k"
    export_backing_mix: bool = True
