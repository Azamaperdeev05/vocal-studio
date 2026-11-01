import os
import shutil
from pathlib import Path
from vocal_studio import process_audio, VocalStudioConfig

URLS = [
    ("https://youtu.be/JY3nEUqBfKc", "Ernar Amandyq - Жарығым"),
    ("https://youtu.be/meuQEmdch0g", "Ernar Amandyq & Yerbol Narimanuly - Параллель"),
    ("https://youtu.be/a5EQGOB5xhQ", "Ernar Amandyq - Жалғыз гүл"),
    ("https://youtu.be/Qomj1eIHny8", "Ernar Amandyq - Сенен кейін"),
    ("https://youtu.be/6g-NTk294fs", "Kyle Ruh - Аңсарым"),
    ("https://youtu.be/iIUz3PCdx_8", "Kyle Ruh - Бұл өмірде"),
    ("https://youtu.be/yenLZPaN6Dk", "Miras Zhugunusov - Жаным"),
    ("https://youtu.be/NFTO3wrKv58", "Darkhan Juzz - Shyraq"),
]

def clean_non_reverb(output_dir: Path):
    # Remove raw, separated, and all files except *_vocal_reverb.wav
    raw_dir = output_dir / "raw"
    sep_dir = output_dir / "separated"
    if raw_dir.exists():
        shutil.rmtree(raw_dir, ignore_errors=True)
    if sep_dir.exists():
        shutil.rmtree(sep_dir, ignore_errors=True)
        
    for p in output_dir.glob("*"):
        if p.is_file() and not p.name.lower().endswith("vocal_reverb.wav"):
            p.unlink(missing_ok=True)

def main():
    out_dir = Path("./output")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    config = VocalStudioConfig(
        output_dir=str(out_dir),
        trim_to_vocal_start=True,
        reverb_room_size=0.68,
        reverb_wet_level=0.35,
        export_mp3=False,           # Only WAV as requested by user
        export_wav=True,
        export_backing_mix=False     # User only wants Vocal Reverb
    )
    
    results = []
    total = len(URLS)
    
    for i, (url, name) in enumerate(URLS, 1):
        print(f"\n==========================================")
        print(f"[{i}/{total}] Processing: {name} ({url})")
        print(f"==========================================")
        try:
            res = process_audio(url, config)
            reverb_wav = res["tracks"]["vocal_reverb"].get("wav")
            print(f"SUCCESS: Generated {reverb_wav}")
            results.append((name, reverb_wav, res["vocal_start_seconds"]))
        except Exception as e:
            print(f"FAILED {name}: {e}")
        finally:
            # Clean up raw/separated and non-reverb files after each track
            clean_non_reverb(out_dir)
            
    print("\n\nAll tracks processed successfully!")
    print("Summary of generated WAV files:")
    for name, wav_path, start_sec in results:
        print(f" - {name} (onset: {start_sec:.2f}s): {wav_path}")

if __name__ == "__main__":
    main()

