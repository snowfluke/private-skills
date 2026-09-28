"""Synthesize the film's score: a music bed plus every sound effect, as one stereo WAV.

Everything comes from oscillators and seeded noise, so the file is reproducible and needs
no sample library. Timing comes from timeline.json. Each scene's effects come from
compositions/<id>.cues.json as [{"t": <scene-local s>, "sfx": "<name>"}, ...].

    uv run --with numpy --with scipy python audio/score.py
    (or: python3 -m venv .venv && .venv/bin/pip install numpy scipy && .venv/bin/python audio/score.py)

Adds the voiceover from audio/vo.json when it exists (see tools/vo.py), ducking the bed under it.

Writes assets/audio/score.wav (loudness-normalized with ffmpeg when it is on PATH) and
assets/audio/score-sfx.wav (effects only, for sync checks).

timeline.json may carry an optional "score" block; every key has a default:
    {"bpm": 100, "reveal": "<scene id>", "groove": "<scene id>",
     "lockup": ["<scene id>", <seconds into it>], "lufs": -15, "seed": 20260525}
Without it, the reveal is the 2nd scene, the groove starts at the 3rd, and the lockup
chord lands 3 s before the end.
"""

import json
import os
import shutil
import subprocess
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "timeline.json")))
SCENES = {c["id"]: c for c in TL["scenes"]}
ORDER = sorted(TL["scenes"], key=lambda c: c["start"])
CFG = TL.get("score", {})
LEN = max(c["start"] + c["dur"] for c in ORDER)
N = int(SR * LEN)
BEAT = 60.0 / CFG.get("bpm", 100)
BAR = 4 * BEAT
rng = np.random.default_rng(CFG.get("seed", 20260525))

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def scene_start(key, fallback):
    return SCENES[key]["start"] if key in SCENES else fallback


REVEAL = scene_start(CFG.get("reveal"), ORDER[min(1, len(ORDER) - 1)]["start"])
GROOVE = scene_start(CFG.get("groove"), ORDER[min(2, len(ORDER) - 1)]["start"])
if "lockup" in CFG:
    LOCKUP = SCENES[CFG["lockup"][0]]["start"] + float(CFG["lockup"][1])
else:
    LOCKUP = LEN - 3.0

# ---------------------------------------------------------------- dsp


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def env(n, a, d, s_level=0.0, r=None):
    """Attack/decay envelope in seconds; with r, holds s_level then releases over r."""
    a_n, d_n = max(1, int(a * SR)), max(1, int(d * SR))
    e = np.zeros(n)
    e[: min(a_n, n)] = np.linspace(0, 1, a_n)[: min(a_n, n)]
    if n > a_n:
        m = min(d_n, n - a_n)
        e[a_n : a_n + m] = np.linspace(1, s_level, d_n)[:m]
        e[a_n + m :] = s_level
    if r:
        r_n = min(int(r * SR), n)
        e[n - r_n :] *= np.linspace(1, 0, r_n)
    return e


def place(bus, x, at, gain=1.0, pan=0.0):
    i = int(round(at * SR))
    if i >= N or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    x = x[: N - i]
    left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[i : i + len(x), 0] += x * gain * left * 1.4142
    bus[i : i + len(x), 1] += x * gain * right * 1.4142


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def saw(f, t):
    return 2 * ((t * f) % 1.0) - 1


# ---------------------------------------------------------------- instruments


def kick(level=1.0):
    t = t_axis(0.45)
    f = 45 + 95 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * level


def clap():
    t = t_axis(0.25)
    noise = rng.standard_normal(len(t))
    e = np.zeros(len(t))
    for k, off in enumerate([0, 0.011, 0.022]):
        e += np.exp(-np.clip(t - off, 0, None) * (60 if k < 2 else 16)) * (t >= off)
    return bp(noise * e, 900, 2600) * 0.9


def hat(open_=False):
    t = t_axis(0.18 if open_ else 0.05)
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * (20 if open_ else 80)) * 0.5


def bass_note(n, dur):
    t = t_axis(dur)
    f = midi(n)
    x = 0.6 * saw(f, t) + 0.4 * np.sin(2 * np.pi * f * t)
    return lp(x, 380) * env(len(t), 0.005, dur * 0.9, 0.5, 0.05)


def pad_chord(notes, dur, bright=900):
    t = t_axis(dur)
    x = np.zeros(len(t))
    for n in notes:
        for det in (-0.12, 0.0, 0.11):
            x += saw(midi(n + det), t + rng.random() * 0.01)
    return lp(x / (3 * len(notes)), bright) * env(len(t), 0.6, 0.4, 0.8, 0.8)


def pluck(n, dur=0.35, level=1.0):
    t = t_axis(dur)
    x = (2 * np.abs(2 * ((t * midi(n)) % 1) - 1) - 1) * np.exp(-t * 11)
    return lp(x, 3200) * level


def bell(f, dur=1.6, level=1.0, idx=3.0):
    t = t_axis(dur)
    mod = np.sin(2 * np.pi * f * 3.5 * t) * idx * np.exp(-t * 5)
    return np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 3.2) * level


def chord_hit(notes, dur=4.0, level=1.0):
    t = t_axis(dur)
    x = sum(saw(midi(n), t) + saw(midi(n) * 1.004, t) for n in notes) / (2 * len(notes))
    return lp(x, 2200) * np.exp(-t * 0.9) * level


# ---------------------------------------------------------------- sound effects


def tick(f=2200, level=1.0):
    t = t_axis(0.03)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + 0.3 * rng.standard_normal(len(t)) * np.exp(-t * 400)) * level


def key():
    t = t_axis(0.035)
    x = bp(rng.standard_normal(len(t)), 1800 + rng.random() * 1400, 6500) * np.exp(-t * 140)
    return x * 0.8 + np.sin(2 * np.pi * (180 + rng.random() * 40) * t) * np.exp(-t * 90) * 0.5


def blip(f1, f2=None, dur=0.09, level=1.0):
    t = t_axis(dur)
    f = np.linspace(f1, f2 or f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.003, dur - 0.003) * level


def whoosh(dur=0.6, lo=300, hi=3500, rising=True, level=1.0):
    t = t_axis(dur)
    noise = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    seg = 480
    for s in range(0, len(t), seg):
        p = s / len(t)
        c = lo * (hi / lo) ** (p if rising else 1 - p)
        out[s : s + seg] = bp(noise[max(0, s - 2000) : s + seg], c * 0.7, min(c * 1.4, 20000))[-len(out[s : s + seg]) :]
    return out * np.sin(np.pi * np.linspace(0, 1, len(t))) ** (1.5 if rising else 0.8) * level


def slam(level=1.0):
    t = t_axis(0.7)
    body = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-t * 18)) / SR) * np.exp(-t * 5)
    return (body + hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 45) * 0.5) * level


def impact():
    t = t_axis(3.0)
    boom = np.sin(2 * np.pi * np.cumsum(32 + 60 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.6)
    return boom + lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 2.5) * 0.35


def riser(dur=2.4, level=1.0):
    t = t_axis(dur)
    tone = np.sin(2 * np.pi * np.cumsum(np.linspace(220, 880, len(t))) / SR) * 0.25
    return (whoosh(dur, 200, 9000, True) + tone) * np.linspace(0.05, 1, len(t)) ** 2 * level


def thunk(level=1.0):
    t = t_axis(0.35)
    body = np.sin(2 * np.pi * np.cumsum(70 + 60 * np.exp(-t * 30)) / SR) * np.exp(-t * 14)
    return (body + bp(rng.standard_normal(len(t)), 600, 4000) * np.exp(-t * 35) * 0.6) * level


def shimmer(dur=1.4, level=1.0):
    out = np.zeros(int(dur * SR) + SR)
    for k in range(14):
        b = bell(midi(84 + [0, 4, 7, 11, 12, 16, 19][k % 7]), 1.0, 0.25, 1.2)
        i = int(k / 14 * dur * SR)
        out[i : i + len(b)] += b
    return out * level


# name -> (maker, gain). Keep effects soft: they sit under the music, not on top.
CUE_FX = {
    "whoosh": (lambda: whoosh(0.6, 300, 3500, True), 0.35),
    "swish": (lambda: whoosh(0.3, 600, 4000, True, 0.7), 0.3),
    "drag": (lambda: whoosh(0.25, 400, 2400, True, 0.5), 0.3),
    "riser": (lambda: riser(1.2, 0.6), 0.4),
    "pop": (lambda: blip(700, 1100, 0.07, 0.8), 0.4),
    "click": (lambda: tick(1700, 0.8), 0.5),
    "key": (key, 0.4),
    "tick": (lambda: tick(2200, 0.5), 0.4),
    "drop": (lambda: blip(260, 140, 0.2, 0.8), 0.5),
    "thunk": (lambda: thunk(0.9), 0.6),
    "chime": (lambda: bell(1760, 1.2, 0.45, 1.2) + bell(2637, 1.2, 0.2, 0.8), 0.4),
    "success": (lambda: np.concatenate([blip(1047, 1047, 0.07, 0.7), blip(1568, 1568, 0.16, 0.7)]), 0.4),
    "warn": (lambda: np.concatenate([blip(587, 587, 0.09, 0.8), blip(494, 494, 0.16, 0.8)]), 0.35),
    "error": (lambda: np.concatenate([blip(520, 520, 0.07, 0.8), blip(390, 380, 0.12, 0.8)]), 0.35),
    "stamp": (lambda: thunk(1.6) + np.pad(tick(900, 0.6), (0, int(0.32 * SR)))[: int(0.35 * SR)], 0.7),
    "slam": (lambda: slam(0.8), 0.6),
    "impact": (impact, 0.8),
    "shimmer": (lambda: shimmer(1.3, 0.9), 0.45),
}
# A swell is loudest mid-envelope; it starts early so that peak lands on the cue.
# Transient sounds (attack at 0) play on the cue as they are.
SWELLS = {"whoosh", "swish", "drag", "riser"}


def peak_offset(x):
    a = np.convolve(np.abs(x), np.ones(480) / 480, "same")
    return int(np.argmax(a)) / SR


# ---------------------------------------------------------------- music
# Four acts keyed to the timeline: tension until the reveal, the reveal, a groove under
# the product at work, a chord under the logo lockup, then a quiet bed under the credits.

chords = {"Am": [57, 60, 64], "F": [53, 57, 60], "E": [52, 56, 59], "C": [48, 55, 60, 64],
          "G": [55, 59, 62], "Cadd9": [48, 55, 62, 64, 67]}
roots = {"Am": 33, "F": 29, "E": 28, "C": 36, "G": 31, "Cadd9": 36}

for b, name in enumerate(["Am", "Am", "F", "F", "E", "E"] * 4):
    at = b * BAR
    if at >= REVEAL:
        break
    place(music, pad_chord(chords[name], BAR + 0.6, 700), at, 0.5)
    for k in range(8):
        place(music, bass_note(roots[name], BEAT * 0.47), at + k * BEAT / 2, 0.55 if k % 2 == 0 else 0.35)
    if b >= 2:
        place(music, kick(0.8), at, 1.0)
        place(music, kick(0.6), at + 2 * BEAT, 1.0)
    if b >= 3:
        for k in range(16):
            place(music, hat(), at + k * BEAT / 4, 0.25 if k % 2 else 0.4, pan=0.3)
if REVEAL > 2.4:
    place(music, riser(2.4, 0.9), REVEAL - 2.4, 0.8)

place(music, chord_hit(chords["C"], 6.0), REVEAL, 0.9)
place(music, pad_chord(chords["C"] + [67], max(GROOVE - REVEAL, 0.5), 1400), REVEAL, 0.55)
for k, n in enumerate([72, 76, 79, 84, 79, 76, 72, 79]):
    if REVEAL + 1.0 + k * BEAT / 2 < GROOVE:
        place(music, bell(midi(n), 1.4, 0.35), REVEAL + 1.0 + k * BEAT / 2, 1.0, pan=(-0.4 if k % 2 else 0.4))
place(music, bass_note(36, max(GROOVE - REVEAL, 0.5)), REVEAL, 0.5)
if GROOVE - REVEAL > 1.5:
    place(music, riser(1.2, 0.5), GROOVE - 1.2, 0.4)

prog = ["C", "Am", "F", "G"]
arp = [0, 7, 12, 16, 12, 7, 0, 7]
i = 0
while GROOVE + i * BAR < LOCKUP - 0.6:
    at = GROOVE + i * BAR
    name = prog[i % 4] if (i // 8) % 3 != 2 else ["Am", "F", "C", "G"][i % 4]
    place(music, pad_chord(chords[name], BAR + 0.5, 1100), at, 0.32)
    root = roots[name] + 12
    for k in range(4):
        place(music, lp(kick(0.9), 900), at + k * BEAT, 0.62)
        place(music, lp(hat(), 11000), at + k * BEAT + BEAT / 2, 0.22, pan=0.25)
        place(music, bass_note(root - 12, BEAT * 0.8), at + k * BEAT + BEAT / 2, 0.45)
    place(music, clap(), at + BEAT, 0.5)
    place(music, clap(), at + 3 * BEAT, 0.5)
    for k, off in enumerate(arp * 2):
        place(music, pluck(root + 12 + off, 0.3, 0.3 if i < 10 else 0.38), at + k * BEAT / 4, 1.0, pan=np.sin(k) * 0.4)
    i += 1

place(music, riser(1.6, 0.6), LOCKUP - 1.6, 0.55)
place(music, chord_hit(chords["Cadd9"], 3.6), LOCKUP, 0.8)
place(music, pad_chord(chords["Cadd9"], max(LEN - LOCKUP, 3.6), 1600), LOCKUP, 0.4)
place(music, bass_note(36, 3.4), LOCKUP, 0.4)
for k, n in enumerate([84, 88, 91, 96]):
    place(music, bell(midi(n), 2.4, 0.3), LOCKUP + k * 0.15, 1.0, pan=(-0.5 + k * 0.33))

# ---------------------------------------------------------------- cues
# Cue t is scene-local in the scene's own (unscaled) time; a speed-wrapped scene
# ("speed" in timeline.json) plays it at t / speed.

for c in ORDER:
    path = os.path.join(ROOT, "compositions", f"{c['id']}.cues.json")
    if not os.path.exists(path):
        continue
    speed = float(c.get("speed", 1.0))
    for cue in json.load(open(path)):
        at, name = c["start"] + float(cue["t"]) / speed, str(cue["sfx"])
        pan = float(np.sin(at * 1.7) * 0.35)
        if name.startswith("type:"):
            for k in range(int(name.split(":")[1])):
                place(sfx, key(), at + k * 0.05, 0.4, pan)
            continue
        if name not in CUE_FX:
            sys.exit(f"{c['id']}.cues.json: unknown sfx {name!r}; known: {', '.join(sorted(CUE_FX))}, type:N")
        make, gain = CUE_FX[name]
        x = make()
        place(sfx, x, at - (peak_offset(x) if name in SWELLS else 0.0), gain, pan)

# ---------------------------------------------------------------- voiceover
# Lines from audio/vo.json, generated by tools/vo.py into assets/audio/vo/<id>.wav. Music ducks
# about 8 dB and effects about 4 dB under the voice; the bed breathes back between lines.

vo = np.zeros(N)
VO_JSON = os.path.join(ROOT, "audio", "vo.json")
if os.path.exists(VO_JSON):
    from math import gcd
    from scipy.signal import resample_poly
    for line in json.load(open(VO_JSON))["lines"]:
        rate, x = wavfile.read(os.path.join(ROOT, "assets", "audio", "vo", f"{line['id']}.wav"))
        x = x.astype(np.float64) / (32768.0 if x.dtype == np.int16 else 1.0)
        if x.ndim > 1:
            x = x.mean(axis=1)
        if rate != SR:
            g = gcd(SR, rate)
            x = resample_poly(x, SR // g, rate // g)
        x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9)
        i = int((SCENES[line["scene"]]["start"] + float(line["t"])) * SR)
        vo[i : i + len(x)] += x[: max(0, N - i)]


def presence(x, attack=0.06, release=0.4, step=240):
    """0..1 envelope that follows the voice: rises in `attack` seconds, falls in `release` seconds."""
    frames = np.abs(x[: len(x) // step * step]).reshape(-1, step).max(axis=1)
    k = max(1, int(0.12 * SR / step))
    on = np.convolve((frames > 0.05).astype(float), np.ones(k), "same") > 0  # bridge gaps between words
    up, down = step / (attack * SR), step / (release * SR)
    out, v = np.zeros(len(on)), 0.0
    for i, target in enumerate(on):
        v = min(v + up, 1.0) if target else max(v - down, 0.0)
        out[i] = v
    env = np.repeat(out, step)
    return np.pad(env, (0, len(x) - len(env)))


pres = presence(vo)
music *= (1 - 0.6 * pres)[:, None]
sfx *= (1 - 0.35 * pres)[:, None]

# ---------------------------------------------------------------- mix


def reverb(x, mix=0.25):
    out = x.copy()
    for d, g in ((0.037, 0.5), (0.053, 0.45), (0.079, 0.4), (0.113, 0.35), (0.167, 0.3), (0.241, 0.25), (0.347, 0.18)):
        n = int(d * SR)
        tail = np.zeros_like(x)
        tail[n:] = x[:-n] * g
        out += lp(tail, 5000) * mix
    return out


music = np.stack([hp(reverb(music[:, ch], 0.22 + 0.02 * ch), 30) for ch in range(2)], axis=1)
sfx = np.stack([lp(reverb(sfx[:, ch], 0.12), 11000) for ch in range(2)], axis=1)
bed = music * 0.42 + sfx
# The voice sits clearly above the bed: its speaking RMS is 2.2x the bed's average.
spoken = np.abs(vo) > 0.05
vo_rms = np.sqrt(np.mean(vo[spoken] ** 2)) if np.any(spoken) else 1.0
mix = bed + (vo / vo_rms * np.sqrt(np.mean(bed ** 2)) * 2.2)[:, None]
fade_in, fade_out = int(0.4 * SR), int(2.0 * SR)
for bus in (mix, sfx):
    bus[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    bus[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.1) / np.tanh(1.1) * 0.89

out_dir = os.path.join(ROOT, "assets", "audio")
os.makedirs(out_dir, exist_ok=True)
raw, final = os.path.join(out_dir, "score-raw.wav"), os.path.join(out_dir, "score.wav")
wavfile.write(raw, SR, (mix * 32767).astype(np.int16))
wavfile.write(os.path.join(out_dir, "score-sfx.wav"), SR, (sfx / max(np.max(np.abs(sfx)), 1e-9) * 0.89 * 32767).astype(np.int16))
lufs = CFG.get("lufs", -15)
if shutil.which("ffmpeg"):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11",
                    "-ar", str(SR), final], check=True)
    os.remove(raw)
else:
    os.replace(raw, final)
    print("ffmpeg not found: score.wav is not loudness-normalized")
print(f"score {LEN:.2f}s  reveal {REVEAL:.2f}  groove {GROOVE:.2f}  lockup {LOCKUP:.2f}  -> {final}")
