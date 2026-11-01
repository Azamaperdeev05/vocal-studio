import os
import subprocess
from pathlib import Path
from typing import Tuple

def is_youtube_url(source: str) -> bool:
    return any(domain in source for domain in ("youtube.com", "youtu.be"))

def download_audio(source: str, output_dir: str = ".") -> Tuple[str, str]:
    """
    Downloads audio from YouTube using yt-dlp, or verifies an existing local file.
    Returns:
        (filepath, track_title)
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    if not is_youtube_url(source):
        src_file = Path(source)
        if not src_file.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        return str(src_file.resolve()), src_file.stem

    output_template = str(out_path / "%(title)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "wav",
        "--print", "after_move:filepath",
        "-o", output_template,
        source
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"yt-dlp failed to output downloaded path for {source}")
        
    downloaded_path = lines[-1]
    title = Path(downloaded_path).stem
    return downloaded_path, title
