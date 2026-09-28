"""Generate the voiceover lines in audio/vo.json with local Kokoro-82M, then check fit.

    <venv>/bin/python tools/vo.py            # generate missing or changed lines, then report fit
    <venv>/bin/python tools/vo.py --check    # report fit only

The venv needs kokoro-onnx and soundfile; the system needs espeak-ng. The model is the one `npx hyperframes tts` downloads to
~/.cache/hyperframes/tts. Kokoro is called directly because the CLI wrapper does not pass espeak's
data path, and the espeakng-loader wheel points at its build machine.

A line is regenerated when its text, voice or speed changes (the hash is kept in the wav's .txt twin).
Fit: each line must end before the next line starts and before its scene ends (a warning, not a stop:
a line may run over into the next scene on purpose).
"""

import hashlib
import json
import os
import subprocess
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = json.load(open(os.path.join(ROOT, "audio", "vo.json")))
SCENES = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "timeline.json")))["scenes"]}
OUT = os.path.join(ROOT, "assets", "audio", "vo")
os.makedirs(OUT, exist_ok=True)


def seconds(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


KOKORO = None


def synth(text, voice, speed, wav):
    global KOKORO
    if KOKORO is None:
        from kokoro_onnx import Kokoro
        from kokoro_onnx.config import EspeakConfig
        # The espeakng-loader wheel's macOS build looks for its data on the CI machine; a system
        # espeak-ng (brew install espeak-ng) works. ESPEAK_PREFIX overrides the location.
        prefix = os.environ.get("ESPEAK_PREFIX") or subprocess.run(["brew", "--prefix", "espeak-ng"], capture_output=True, text=True).stdout.strip()
        lib = os.path.join(prefix, "lib", "libespeak-ng.dylib" if sys.platform == "darwin" else "libespeak-ng.so")
        if not os.path.exists(lib):
            sys.exit(f"espeak-ng not found at {prefix}; install it (brew install espeak-ng) or set ESPEAK_PREFIX")
        cache = os.path.expanduser("~/.cache/hyperframes/tts")
        KOKORO = Kokoro(f"{cache}/models/kokoro-v1.0.onnx", f"{cache}/voices/voices-v1.0.bin",
                        espeak_config=EspeakConfig(lib_path=lib, data_path=os.path.join(prefix, "share", "espeak-ng-data")))
    import soundfile
    samples, rate = KOKORO.create(text, voice=voice, speed=speed, lang="en-us")
    soundfile.write(wav, samples, rate)


rows = []
for line in VO["lines"]:
    wav = os.path.join(OUT, f"{line['id']}.wav")
    key = hashlib.sha1(f"{VO['voice']}|{VO['speed']}|{line.get('say', line['text'])}".encode()).hexdigest()
    stamp = wav[:-4] + ".txt"
    fresh = os.path.exists(wav) and os.path.exists(stamp) and open(stamp).read() == key
    if not fresh and "--check" not in sys.argv:
        synth(line.get("say", line["text"]), VO["voice"], VO["speed"], wav)
        open(stamp, "w").write(key)
    sc = SCENES[line["scene"]]
    at = sc["start"] + line["t"]
    rows.append((at, seconds(wav), sc["start"] + sc["dur"], line))

rows.sort(key=lambda r: r[0])
for i, (at, dur, scene_end, line) in enumerate(rows):
    end = at + dur
    nxt = rows[i + 1][0] if i + 1 < len(rows) else None
    flags = []
    if nxt is not None and end > nxt - 0.15:
        flags.append(f"OVERLAPS next line by {end - nxt + 0.15:.2f}s")
    if end > scene_end:
        flags.append(f"runs {end - scene_end:.2f}s past {line['scene']}")
    words = len(line["text"].split())
    print(f"{line['id']:13s} {at:7.2f}-{end:7.2f}  {dur:4.2f}s  {words / dur:3.1f} w/s  {'  '.join(flags)}")
