"""
Audio analysis pipeline: MP3 → timeline.json
Extracts beats, onsets, and MIDI notes for Blender animation.
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


def analyze(audio_path: str, output_path: str = None) -> dict:
    audio_path = Path(audio_path)
    if output_path is None:
        output_path = audio_path.with_suffix(".timeline.json")

    y, sr = librosa.load(audio_path, sr=None, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)

    # Tempo and beat times
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
    bpm = float(tempo[0]) if hasattr(tempo, "__len__") else float(tempo)

    # Onset detection (more precise than beats — catches individual notes)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units="frames")
    onset_times = librosa.frames_to_time(onset_frames, sr=sr).tolist()

    # MIDI note extraction via basic-pitch
    model_output, midi_data, note_events = predict(audio_path, ICASSP_2022_MODEL_PATH)

    events = []
    for note in note_events:
        start_time, end_time, pitch_midi, velocity, _ = note
        note_name = librosa.midi_to_note(int(pitch_midi))
        events.append({
            "time": round(float(start_time), 4),
            "duration": round(float(end_time) - float(start_time), 4),
            "note": note_name,
            "midi": int(pitch_midi),
            "velocity": round(float(velocity), 3),
            # Blender fields — populated by scene_builder.py
            "instrument": None,
            "position": None,
            "ball_count": 1,
        })

    # Sort by time
    events.sort(key=lambda e: e["time"])

    timeline = {
        "source": str(audio_path.name),
        "duration": round(duration, 3),
        "bpm": round(bpm, 2),
        "beats": beat_times,
        "onsets": onset_times,
        "events": events,
    }

    with open(output_path, "w") as f:
        json.dump(timeline, f, indent=2)

    print(f"Timeline saved → {output_path}")
    print(f"  Duration: {duration:.1f}s | BPM: {bpm:.1f} | Notes: {len(events)}")
    return timeline


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <audio_file> [output.timeline.json]")
        sys.exit(1)
    output = sys.argv[2] if len(sys.argv) > 2 else None
    analyze(sys.argv[1], output)
