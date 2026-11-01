import os
import subprocess
import numpy as np
import soundfile as sf
from pedalboard import Pedalboard, Reverb, HighpassFilter, Compressor
from pedalboard.io import AudioFile

INPUT_SONG = "Kyle Ruh— «Күзгі бақ» ⧸ COVER SHOW ⧸ КАВЕР ШОУ.wav"
VOCALS_FILE = "separated/htdemucs/input_song/vocals.wav"
NO_VOCALS_FILE = "separated/htdemucs/input_song/no_vocals.wav"

START_SEC = 14.45  # Vocal starts cleanly with natural breath onset

def export_audio(np_data, sr, base_name):
    wav_out = f"{base_name}.wav"
    mp3_out = f"{base_name}.mp3"
    
    # Save WAV
    with AudioFile(wav_out, 'w', sr, np_data.shape[0]) as f:
        f.write(np_data)
        
    # Convert to 320k MP3 using ffmpeg
    subprocess.run([
        "/opt/homebrew/bin/ffmpeg", "-y", "-i", wav_out,
        "-b:a", "320k", mp3_out
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"Exported: {mp3_out} and {wav_out}")
    return mp3_out, wav_out

def main():
    print(f"Loading vocals from {VOCALS_FILE}...")
    with AudioFile(VOCALS_FILE) as f:
        vocal_data = f.read(f.frames)
        sr = f.samplerate
        
    start_sample = int(START_SEC * sr)
    vocal_trimmed = vocal_data[:, start_sample:]
    
    # 1. Dry Vocal Trimmed
    print("1. Creating Dry Vocal Trimmed...")
    # Peak normalize
    dry_peak = np.max(np.abs(vocal_trimmed))
    if dry_peak > 0:
        dry_normalized = vocal_trimmed * (10 ** (-1.0 / 20.0) / dry_peak)
    else:
        dry_normalized = vocal_trimmed
    export_audio(dry_normalized, sr, "Kyle_Ruh_Kuzgi_Baq_Vocal_Dry")
    
    # 2. Vocal with Lush Studio Reverb
    print("2. Creating Vocal with Lush Studio Reverb...")
    reverb_board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=80.0),
        Compressor(threshold_db=-16, ratio=2.5, attack_ms=10, release_ms=120),
        Reverb(
            room_size=0.68,
            damping=0.45,
            wet_level=0.35,
            dry_level=0.85,
            width=1.0,
            freeze_mode=0.0
        )
    ])
    vocal_reverb = reverb_board(vocal_trimmed, sr)
    rev_peak = np.max(np.abs(vocal_reverb))
    if rev_peak > 0:
        vocal_reverb = vocal_reverb * (10 ** (-1.0 / 20.0) / rev_peak)
    export_audio(vocal_reverb, sr, "Kyle_Ruh_Kuzgi_Baq_Vocal_Reverb")
    
    # 3. Full original song trimmed from 14.45s
    print("3. Creating Full original song trimmed...")
    with AudioFile(INPUT_SONG) as f:
        full_data = f.read(f.frames)
        full_sr = f.samplerate
    full_start_sample = int(START_SEC * full_sr)
    full_trimmed = full_data[:, full_start_sample:]
    f_peak = np.max(np.abs(full_trimmed))
    if f_peak > 0:
        full_trimmed = full_trimmed * (10 ** (-1.0 / 20.0) / f_peak)
    export_audio(full_trimmed, full_sr, "Kyle_Ruh_Kuzgi_Baq_FullSong_Trimmed")

    # 4. Mix Reverb Vocal with Instrumental trimmed
    print("4. Creating Mix: Reverb Vocal + Instrumental...")
    with AudioFile(NO_VOCALS_FILE) as f:
        inst_data = f.read(f.frames)
    inst_trimmed = inst_data[:, start_sample:]
    # Match length
    min_len = min(vocal_reverb.shape[1], inst_trimmed.shape[1])
    mix = vocal_reverb[:, :min_len] * 0.95 + inst_trimmed[:, :min_len] * 0.85
    mix_peak = np.max(np.abs(mix))
    if mix_peak > 0:
        mix = mix * (10 ** (-1.0 / 20.0) / mix_peak)
    export_audio(mix, sr, "Kyle_Ruh_Kuzgi_Baq_ReverbVocal_With_Music")

    print("All tracks successfully generated!")

if __name__ == "__main__":
    main()

