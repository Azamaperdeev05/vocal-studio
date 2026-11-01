import numpy as np
import pytest
from vocal_studio.detector import detect_vocal_start
from vocal_studio.effects import normalize_audio, apply_studio_reverb
from vocal_studio.config import VocalStudioConfig

def test_normalize_audio():
    # Test normalization to -1.0 dBFS
    data = np.array([0.1, -0.5, 0.2, -0.4])
    normalized = normalize_audio(data, target_db=-1.0)
    expected_peak = 10 ** (-1.0 / 20.0)
    assert np.isclose(np.max(np.abs(normalized)), expected_peak)

def test_detect_vocal_start():
    # 2 seconds of silence followed by 2 seconds of sound at 44100 Hz
    sr = 44100
    silence = np.zeros(sr * 2)
    signal = np.sin(2 * np.pi * 440 * np.linspace(0, 2, sr * 2)) * 0.5
    audio = np.concatenate([silence, signal])
    
    idx, sec = detect_vocal_start(audio, sr, preroll_seconds=0.2)
    # The signal starts at 2.0s, with 0.2s preroll it should be around 1.8s
    assert 1.6 <= sec <= 2.05

def test_apply_studio_reverb():
    sr = 44100
    config = VocalStudioConfig()
    # 1 second sine wave stereo
    audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr)) * 0.3
    stereo_audio = np.stack([audio, audio])
    
    reverb_audio = apply_studio_reverb(stereo_audio, sr, config)
    assert reverb_audio.shape[0] == 2
    assert reverb_audio.shape[1] == stereo_audio.shape[1]
    peak = np.max(np.abs(reverb_audio))
    assert peak <= 1.0

