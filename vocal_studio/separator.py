import os
import subprocess
from pathlib import Path
from typing import Tuple

def separate_vocals(
    audio_path: str,
    output_dir: str = "./separated",
    model: str = "htdemucs",
    device: str = "cpu"
) -> Tuple[str, str]:
    """
    Separates vocals and accompaniment using Demucs.
    Returns:
        (vocals_wav_path, no_vocals_wav_path)
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "demucs",
        "--two-stems", "vocals",
        "-n", model,
        "-d", device,
        "-o", str(out_dir),
        audio_path
    ]
    
    subprocess.run(cmd, check=True)
    
    track_name = Path(audio_path).stem
    model_folder = out_dir / model / track_name
    
    vocals_path = model_folder / "vocals.wav"
    no_vocals_path = model_folder / "no_vocals.wav"
    
    if not vocals_path.exists():
        raise FileNotFoundError(f"Demucs did not produce vocals at {vocals_path}")
        
    return str(vocals_path), str(no_vocals_path)

