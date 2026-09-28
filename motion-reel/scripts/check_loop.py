"""Check a loop reel: frames around every section hand-off, frames across the loop seam, and the audio seam.

    uv run --with numpy python tools/check_loop.py out/reel.mp4 [--out checks]

Reads src/timeline.json (bpm, fps, beats, sections, optional handoffs). Writes:
  checks/handoffs.png  3 frames per boundary (0.5 and 0.15 beat before, 0.15 after), one row each
  checks/seam.png      the last 5 frames and the first 5 frames, side by side
Prints the audio level of the last and first 50 ms and the sample jump at the seam.
"""

import argparse
import json
import os
import subprocess

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--out", default=os.path.join(ROOT, "checks"))
a = ap.parse_args()
T = json.load(open(os.path.join(ROOT, "src", "timeline.json")))
fpb = T["fps"] * 60 / T["bpm"]
total = round(T["beats"] * fpb)
os.makedirs(a.out, exist_ok=True)


def sheet(frames, cols, path, width=320):
    sel = "+".join(f"eq(n\\,{f})" for f in frames)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-vf", f"select='{sel}',scale={width}:-2,tile={cols}x{-(-len(frames) // cols)}",
                    "-fps_mode", "vfr", "-frames:v", "1", path], check=True)


# Section starts, plus any extra hand-off beats inside a section (timeline.json "handoffs": [28, 32]).
bounds = sorted({s["start"] for s in T["sections"] if s["start"] > 0} | set(T.get("handoffs", [])))
frames = [round((b + d) * fpb) for b in bounds for d in (-0.5, -0.15, 0.15)]
sheet(frames, 3, os.path.join(a.out, "handoffs.png"))
print("hand-off beats:", bounds, "->", os.path.join(a.out, "handoffs.png"))

# Seam: play the file twice in a row and look at the frames where it wraps.
concat = os.path.join(a.out, "twice.txt")
open(concat, "w").write(f"file '{os.path.abspath(a.video)}'\n" * 2)
twice = os.path.join(a.out, "twice.mp4")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", twice], check=True)
sel = "+".join(f"eq(n\\,{f})" for f in range(total - 5, total + 5))
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", twice, "-vf", f"select='{sel}',scale=240:-2,tile=10x1", "-fps_mode", "vfr", "-frames:v", "1",
                os.path.join(a.out, "seam.png")], check=True)
os.remove(concat)
os.remove(twice)
print("seam frames", total - 5, "to", total + 4, "->", os.path.join(a.out, "seam.png"))

pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.video, "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.int16).astype(float) / 32768
w = 2400
db = lambda s: 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9)
print(f"audio: last 50 ms {db(x[-w:]):.1f} dB, first 50 ms {db(x[:w]):.1f} dB, seam jump {abs(x[0] - x[-1]):.3f} "
      f"(p99 step {np.percentile(np.abs(np.diff(x)), 99):.3f}); a downbeat hit on beat 0 makes the first window louder on purpose")
