"""
Main orchestrator: MP3 → final MP4
Usage: python scripts/run.py input/mp3/song.mp3 "Song Title"
"""
import subprocess
import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"


def run(audio_path: str, title: str):
    audio_path = Path(audio_path).resolve()
    stem = audio_path.stem
    output_dir = ROOT / "output"
    render_dir = output_dir / "renders" / stem
    render_dir.mkdir(parents=True, exist_ok=True)

    timeline_path = ROOT / "input" / "audio_stems" / f"{stem}.timeline.json"
    timeline_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[1/3] Audio analysis: {audio_path.name}")
    subprocess.run([
        sys.executable,
        str(ROOT / "pipeline" / "audio" / "analyze.py"),
        str(audio_path),
        str(timeline_path),
    ], check=True)

    print(f"\n[2/3] Blender render: {stem}")
    subprocess.run([
        BLENDER, "--background",
        "--python", str(ROOT / "pipeline" / "blender" / "scene_builder.py"),
        "--",
        str(timeline_path),
        str(render_dir),
        title,
    ], check=True)

    print(f"\n[3/3] Export MP4")
    video_path = output_dir / "videos" / f"{stem}.mp4"
    video_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", str(render_dir / "frame_%04d.png"),
        "-i", str(audio_path),
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(video_path),
    ], check=True)

    print(f"\nDone → {video_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/run.py <audio.mp3> <title>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
