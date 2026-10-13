"""Sample-accurate 24kHz WAV assembly for authored per-shot narration.

Accepts real Kokoro-produced WAVs or explicitly synthetic CI fixtures. No
speech synthesis is claimed here. 24000 Hz / 24 FPS => 1000 samples/frame.
"""
from __future__ import annotations

import json
import re
import wave
from pathlib import Path

from studio.film import FilmError

SAMPLE_RATE = 24000
FPS = 24


def assemble_narration(timeline: dict, voices_dir: Path, output: Path) -> dict:
    if timeline.get("fps") != FPS or not isinstance(timeline.get("total_frames"), int) or timeline["total_frames"] <= 0:
        raise FilmError("Invalid fixed-fps film timeline")
    total_samples = timeline["total_frames"] * (SAMPLE_RATE // FPS)
    pcm = bytearray(total_samples * 2)
    used = bytearray(total_samples)
    manifest = []
    for event in timeline["narration"]:
        name = event["wav"]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.wav", name):
            raise FilmError("Unsafe narration WAV name")
        source = voices_dir / name
        if not source.is_file():
            raise FilmError("Missing narration WAV: " + name)
        with wave.open(str(source), "rb") as wav:
            if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != SAMPLE_RATE or wav.getcomptype() != "NONE":
                raise FilmError("Narration requires mono PCM16 24kHz WAV")
            samples = wav.getnframes()
            data = wav.readframes(samples)
        if samples == 0:
            raise FilmError("Empty narration WAV")
        start = event["absolute_frame"] * (SAMPLE_RATE // FPS)
        end = start + samples
        allowed_end = event["shot_end_frame"] * (SAMPLE_RATE // FPS)
        if start < 0 or end > allowed_end or end > total_samples:
            raise FilmError("Narration overflows its shot window")
        if any(used[start:end]):
            raise FilmError("Narration segments overlap")
        pcm[start*2:end*2] = data
        used[start:end] = b"\x01" * samples
        manifest.append({"shot_id": event["shot_id"], "wav": name,
                         "start_sample": start, "end_sample": end,
                         "start_frame": event["absolute_frame"]})
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SAMPLE_RATE)
        out.writeframes(pcm)
    return {"sample_rate": SAMPLE_RATE, "sample_count": total_samples,
            "duration_seconds": total_samples / SAMPLE_RATE, "segments": manifest}


def assemble_file(timeline_path: Path, voices_dir: Path, output: Path, manifest_path: Path) -> Path:
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    manifest = assemble_narration(timeline, voices_dir, output)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output
