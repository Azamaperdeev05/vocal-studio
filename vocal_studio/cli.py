import argparse
import sys
from pathlib import Path
from .config import VocalStudioConfig
from .pipeline import process_audio

def main():
    parser = argparse.ArgumentParser(
        prog="vocal-studio",
        description="YouTube/Audio Vocal Isolation, Onset Trimming & Studio Reverb Processor."
    )
    parser.add_argument(
        "source",
        type=str,
        help="YouTube URL or path to local audio/video file."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output",
        help="Directory to save processed audio files (default: ./output)"
    )
    parser.add_argument(
        "--no-trim",
        action="store_true",
        help="Do not trim the leading intro music."
    )
    parser.add_argument(
        "--start-time",
        type=float,
        default=None,
        help="Manually specify vocal start time in seconds (e.g. 14.5)"
    )
    parser.add_argument(
        "--room-size",
        type=float,
        default=0.68,
        help="Reverb room size (0.0 to 1.0, default: 0.68)"
    )
    parser.add_argument(
        "--wet-level",
        type=float,
        default=0.35,
        help="Reverb wet level (0.0 to 1.0, default: 0.35)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda", "mps"],
        help="Device for Demucs model inference (cpu, cuda, or mps)"
    )
    parser.add_argument(
        "--no-mix",
        action="store_true",
        help="Skip generating reverb vocal + instrumental mix."
    )
    
    args = parser.parse_args()
    
    config = VocalStudioConfig(
        output_dir=args.output,
        trim_to_vocal_start=not args.no_trim,
        manual_start_seconds=args.start_time,
        reverb_room_size=args.room_size,
        reverb_wet_level=args.wet_level,
        device=args.device,
        export_backing_mix=not args.no_mix
    )
    
    print(f"Starting Vocal Studio for: {args.source}")
    try:
        result = process_audio(args.source, config)
        print("\nProcessing complete!")
        print(f"Track: {result['title']}")
        print(f"Vocal onset detected at: {result['vocal_start_seconds']:.2f}s")
        print("\nGenerated files:")
        for track_name, paths in result["tracks"].items():
            print(f"  {track_name}:")
            for fmt, path in paths.items():
                print(f"    - {fmt.upper()}: {path}")
    except Exception as e:
        print(f"\nError processing track: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
