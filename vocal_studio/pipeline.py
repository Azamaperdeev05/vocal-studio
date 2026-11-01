import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
from pedalboard.io import AudioFile

from .config import VocalStudioConfig
from .downloader import download_audio
from .separator import separate_vocals
from .detector import detect_vocal_start
from .effects import apply_studio_reverb, normalize_audio

def _save_track(
    data: np.ndarray,
    sr: int,
    base_path: Path,
    export_mp3: bool = True,
    export_wav: bool = True,
    mp3_bitrate: str = "320k"
) -> Dict[str, str]:
    results = {}
    base_path.parent.mkdir(parents=True, exist_ok=True)
    wav_path = base_path.with_suffix(".wav")
    mp3_path = base_path.with_suffix(".mp3")
    
    if export_wav or export_mp3:
        with AudioFile(str(wav_path), 'w', sr, data.shape[0]) as f:
            f.write(data)
        if export_wav:
            results["wav"] = str(wav_path)
            
    if export_mp3:
        cmd = [
            "ffmpeg", "-y", "-i", str(wav_path),
            "-b:a", mp3_bitrate, str(mp3_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        results["mp3"] = str(mp3_path)
        if not export_wav:
            wav_path.unlink(missing_ok=True)
            
    return results

def process_audio(
    source: str,
    config: Optional[VocalStudioConfig] = None
) -> Dict[str, Any]:
    """
    Main processing pipeline:
    1. Download YouTube or locate file
    2. Separate vocals via Demucs
    3. Detect vocal start timestamp
    4. Trim intro
    5. Apply studio reverb and normalization
    6. Export audio tracks (dry, reverb, mix, trimmed full)
    """
    if config is None:
        config = VocalStudioConfig()
        
    out_dir = Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[1/5] Fetching audio from {source}...")
    audio_file, title = download_audio(source, str(out_dir / "raw"))
    
    print("[2/5] Separating vocals and instruments with Demucs...")
    vocals_wav, no_vocals_wav = separate_vocals(
        audio_file,
        output_dir=str(out_dir / "separated"),
        model=config.demucs_model,
        device=config.device
    )
    
    print("[3/5] Loading separated stems...")
    with AudioFile(vocals_wav) as f:
        vocal_data = f.read(f.frames)
        sr = f.samplerate
        
    with AudioFile(no_vocals_wav) as f:
        inst_data = f.read(f.frames)
        
    with AudioFile(audio_file) as f:
        full_data = f.read(f.frames)
        full_sr = f.samplerate

    # Vocal onset detection
    if config.manual_start_seconds is not None:
        start_sec = config.manual_start_seconds
        start_idx = int(start_sec * sr)
        print(f"[4/5] Manual start time used: {start_sec:.2f}s")
    elif config.trim_to_vocal_start:
        start_idx, start_sec = detect_vocal_start(
            vocal_data,
            sr,
            window_ms=config.detection_window_ms,
            threshold_ratio=config.detection_threshold_ratio,
            min_speech_duration_sec=config.min_speech_duration_sec,
            preroll_seconds=config.preroll_seconds
        )
        print(f"[4/5] Detected vocal start: {start_sec:.2f}s (trimmed leading music)")
    else:
        start_idx = 0
        start_sec = 0.0

    vocal_trimmed = vocal_data[:, start_idx:]
    inst_trimmed = inst_data[:, start_idx:]
    
    full_start_idx = int(start_sec * full_sr)
    full_trimmed = full_data[:, full_start_idx:]
    
    print("[5/5] Processing studio effects & exporting tracks...")
    sanitized_title = "".join(c for c in title if c.isalnum() or c in ("-", "_", " ")).strip().replace(" ", "_")
    
    # Normalize dry vocal
    dry_vocal = normalize_audio(vocal_trimmed, target_db=config.peak_target_db)
    dry_files = _save_track(
        dry_vocal, sr,
        out_dir / f"{sanitized_title}_vocal_dry",
        export_mp3=config.export_mp3,
        export_wav=config.export_wav,
        mp3_bitrate=config.mp3_bitrate
    )
    
    # Reverb vocal
    reverb_vocal = apply_studio_reverb(vocal_trimmed, sr, config)
    reverb_files = _save_track(
        reverb_vocal, sr,
        out_dir / f"{sanitized_title}_vocal_reverb",
        export_mp3=config.export_mp3,
        export_wav=config.export_wav,
        mp3_bitrate=config.mp3_bitrate
    )
    
    # Full original song trimmed
    full_files = _save_track(
        normalize_audio(full_trimmed, target_db=config.peak_target_db),
        full_sr,
        out_dir / f"{sanitized_title}_full_trimmed",
        export_mp3=config.export_mp3,
        export_wav=config.export_wav,
        mp3_bitrate=config.mp3_bitrate
    )
    
    mix_files = {}
    if config.export_backing_mix:
        min_len = min(reverb_vocal.shape[1], inst_trimmed.shape[1])
        mix_audio = reverb_vocal[:, :min_len] * 0.95 + inst_trimmed[:, :min_len] * 0.85
        mix_audio = normalize_audio(mix_audio, target_db=config.peak_target_db)
        mix_files = _save_track(
            mix_audio, sr,
            out_dir / f"{sanitized_title}_reverb_mix",
            export_mp3=config.export_mp3,
            export_wav=config.export_wav,
            mp3_bitrate=config.mp3_bitrate
        )

    return {
        "title": title,
        "vocal_start_seconds": start_sec,
        "sample_rate": sr,
        "tracks": {
            "vocal_reverb": reverb_files,
            "vocal_dry": dry_files,
            "full_trimmed": full_files,
            "reverb_mix": mix_files
        }
    }

