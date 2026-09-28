"""Pull the rendered frame at every sound cue of a scene into one contact sheet.

    python3 tools/cue_frames.py renders/film.mp4 <scene-id> [--offset 0.1] [--out cue-sheets]

This is the sync check that works. A frame at a "click" cue must show the cursor on its target,
and a frame at a "pop" must show the item appearing. Motion-versus-audio measurements on the mixed
track are swamped by the music beat, so read the sheet instead. --offset also grabs a second frame
that many seconds after each cue (for example a ripple or a toast that follows the click).

Needs ffmpeg. Labels are drawn when Pillow is installed; otherwise the legend is printed.
"""

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("scene")
ap.add_argument("--offset", type=float, default=0.0)
ap.add_argument("--out", default=os.path.join(ROOT, "cue-sheets"))
ap.add_argument("--cols", type=int, default=6)
args = ap.parse_args()

scenes = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "timeline.json")))["scenes"]}
if args.scene not in scenes:
    sys.exit(f"unknown scene {args.scene!r}; known: {', '.join(scenes)}")
sc = scenes[args.scene]
cues_path = os.path.join(ROOT, "compositions", f"{args.scene}.cues.json")
if not os.path.exists(cues_path):
    sys.exit(f"no cue file at {cues_path}")
speed = float(sc.get("speed", 1.0))
shots = []
for c in json.load(open(cues_path)):
    at = sc["start"] + float(c["t"]) / speed
    shots.append((at, c["sfx"]))
    if args.offset:
        shots.append((at + args.offset, f'{c["sfx"]} +{args.offset}'))

work = os.path.join(args.out, args.scene)
os.makedirs(work, exist_ok=True)
for name in os.listdir(work):
    if name.startswith("f") and name.endswith(".png"):
        os.remove(os.path.join(work, name))

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None

for k, (at, label) in enumerate(shots):
    png = os.path.join(work, f"f{k:03d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{at:.3f}", "-i", args.video,
                    "-frames:v", "1", "-vf", "scale=640:-2", png], check=True)
    if Image:
        im = Image.open(png).convert("RGB")
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 640, 26], fill=(0, 0, 0))
        d.text((8, 6), f"#{k} {at:.2f}s {label}", fill=(255, 255, 0))
        im.save(png)
    print(f"#{k:<3} {at:8.2f}s  {label}")

rows = -(-len(shots) // args.cols)
sheet = os.path.join(args.out, f"{args.scene}.jpg")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "1", "-i", os.path.join(work, "f%03d.png"),
                "-vf", f"tile={args.cols}x{rows}:padding=6:color=black", "-frames:v", "1", sheet], check=True)
print(f"sheet -> {sheet}")
