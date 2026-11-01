"""
Vocal Studio - Python package for YouTube/audio vocal isolation, onset trimming, and studio reverb processing.
"""

from .config import VocalStudioConfig
from .downloader import download_audio
from .separator import separate_vocals
from .detector import detect_vocal_start
from .effects import apply_studio_reverb, normalize_audio
from .pipeline import process_audio

__version__ = "0.1.0"
__all__ = [
    "VocalStudioConfig",
    "download_audio",
    "separate_vocals",
    "detect_vocal_start",
    "apply_studio_reverb",
    "normalize_audio",
    "process_audio",
]
