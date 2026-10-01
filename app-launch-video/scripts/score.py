"""Synthesize the film's score: a music bed plus every sound effect, as one stereo WAV.

Everything comes from oscillators and seeded noise, so the file is reproducible and needs
no sample library. Timing comes from timeline.json. Each scene's effects come from
compositions/<id>.cues.json as [{"t": <scene-local s>, "sfx": "<name>"}, ...].

    uv run --with numpy --with scipy python audio/score.py
    (or: python3 -m venv .venv && .venv/bin/pip install numpy scipy && .venv/bin/python audio/score.py)
    python3 audio/score.py --self-test

The music comes from the "music" block in timeline.json, copied from DIRECTION.json: bpm,
root, mode, progression, preset, swing and timbre (see music.py next to this file). There is
no default music: a film without its own block stops here.

Adds the voiceover from audio/vo.json when it exists (see tools/vo.py), ducking the bed under it.

Writes assets/audio/score.wav (loudness-normalized with ffmpeg when it is on PATH) and
assets/audio/score-sfx.wav (effects only, for sync checks).

timeline.json may also carry a "score" block; every key has a default:
    {"reveal": "<scene id>", "groove": "<scene id>",
     "lockup": ["<scene id>", <seconds into it>], "lufs": -15, "seed": 20260525}
Without it, the reveal is the 2nd scene, the groove starts at the 3rd, and the lockup
chord lands 3 s before the end.
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import music as M  # noqa: E402  (music.py sits next to this file)


def self_test():
    """Two films with different music blocks must differ; the same block twice must match."""
    import tempfile
    base = {"scenes": [{"id": "a", "start": 0, "dur": 4}, {"id": "b", "start": 4, "dur": 3},
                       {"id": "c", "start": 7, "dur": 9}],
            "score": {"lockup": ["c", 6]}}
    blocks = [{"bpm": 92, "root": "F#", "mode": "dorian", "progression": ["i", "IV", "i", "VII"],
               "preset": "broken-beat", "swing": 0.12, "timbre": "glass"},
              {"bpm": 124, "root": "Bb", "mode": "lydian", "progression": ["I", "II", "vii", "V"],
               "preset": "pulse-house", "swing": 0.0, "timbre": "wood"}]
    outs = []
    with tempfile.TemporaryDirectory() as d:
        for n, block in enumerate(blocks + blocks[:1]):
            root = os.path.join(d, str(n))
            os.makedirs(os.path.join(root, "compositions"))
            json.dump({**base, "music": block}, open(os.path.join(root, "timeline.json"), "w"))
            json.dump([{"t": 1.0, "sfx": "click"}, {"t": 2.0, "sfx": "success"}],
                      open(os.path.join(root, "compositions", "b.cues.json"), "w"))
            env = {**os.environ, "SCORE_ROOT": root, "SCORE_RAW": "1"}
            subprocess.run([sys.executable, os.path.abspath(__file__)], env=env, check=True, capture_output=True)
            outs.append(open(os.path.join(root, "assets", "audio", "score.wav"), "rb").read())
        bad = os.path.join(d, "bad")
        os.makedirs(bad)
        json.dump(base, open(os.path.join(bad, "timeline.json"), "w"))
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env={**os.environ, "SCORE_ROOT": bad},
                           capture_output=True, text=True)
        assert r.returncode != 0 and "music" in r.stderr, "a timeline without a music block must stop"
    assert outs[0] != outs[1], "two different music blocks produced the same score"
    assert outs[0] == outs[2], "the same music block produced two different scores"
    assert abs(len(outs[0]) - len(outs[1])) < 64, "both scores must last the length of the timeline"
    print("self-test OK")


if __name__ == "__main__" and sys.argv[1:] == ["--self-test"]:
    self_test()
    sys.exit(0)

import numpy as np  # noqa: E402
from scipy.io import wavfile  # noqa: E402
from scipy.signal import butter, sosfilt  # noqa: E402

SR = 48000
ROOT = os.environ.get("SCORE_ROOT") or os.path.dirname(HERE)
TL = json.load(open(os.path.join(ROOT, "timeline.json")))
SCENES = {c["id"]: c for c in TL["scenes"]}
ORDER = sorted(TL["scenes"], key=lambda c: c["start"])
CFG = TL.get("score", {})
MCFG = TL.get("music")
KEY, PRESET, BPM, SWING, TIMBRE = M.load(MCFG)
LEN = max(c["start"] + c["dur"] for c in ORDER)
N = int(SR * LEN)
BEAT = 60.0 / BPM
BAR = 4 * BEAT
STEP = BEAT / 4
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


def snare(level=1.0):
    t = t_axis(0.2)
    return (bp(rng.standard_normal(len(t)), 1200, 7000) * np.exp(-t * 22) * 0.7
            + np.sin(2 * np.pi * 185 * t) * np.exp(-t * 28) * 0.5) * level


def rim(level=1.0):
    t = t_axis(0.06)
    return (np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 120) + bp(rng.standard_normal(len(t)), 2000, 8000)
            * np.exp(-t * 300) * 0.4) * level


def lead(kind, n, dur, level=1.0):
    """The preset's lead voice, playing MIDI note n."""
    if kind == "pluck":
        return pluck(n, dur, level)
    if kind == "bell":
        return bell(midi(n), dur * 2.2, level * 0.5, 2.2)
    if kind == "keys":
        t = t_axis(dur * 1.6)
        return (bell(midi(n), dur * 1.6, 0.5, 0.9) + np.sin(2 * np.pi * midi(n) * t) * np.exp(-t * 4) * 0.3) * level
    if kind == "saw":
        t = t_axis(dur)
        x = saw(midi(n), t) + saw(midi(n) * 1.006, t)
        return lp(x * 0.4, 2600) * env(len(t), 0.01, dur, 0.6, 0.05) * level
    raise ValueError(kind)


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
        b = bell(midi(KEY.note(7 + [0, 2, 4, 6, 7, 9, 11][k % 7], 4)), 1.0, 0.25, 1.2)
        i = int(k / 14 * dur * SR)
        out[i : i + len(b)] += b
    return out * level


# name -> (maker, gain). Keep effects soft: they sit under the music, not on top.
CUE_FX = {
    "whoosh": (lambda: whoosh(0.6, 300, 3500, True), 0.35),
    "swish": (lambda: whoosh(0.3, 600, 4000, True, 0.7), 0.3),
    "drag": (lambda: whoosh(0.25, 400, 2400, True, 0.5), 0.3),
    "riser": (lambda: riser(1.2, 0.6), 0.4),
    "pop": (lambda: blip(midi(KEY.note(0, 5)), midi(KEY.note(2, 5)), 0.07, 0.8), 0.4),
    "click": (lambda: tick(1700, 0.8), 0.5),
    "key": (key, 0.4),
    "tick": (lambda: tick(2200, 0.5), 0.4),
    "drop": (lambda: blip(midi(KEY.note(0, 4)), midi(KEY.note(0, 3)), 0.2, 0.8), 0.5),
    "thunk": (lambda: thunk(0.9), 0.6),
    "chime": (lambda: bell(midi(KEY.note(7, 5)), 1.2, 0.45, 1.2) + bell(midi(KEY.note(11, 5)), 1.2, 0.2, 0.8), 0.4),
    "success": (lambda: np.concatenate([blip(midi(KEY.note(4, 5)), None, 0.07, 0.7), blip(midi(KEY.note(7, 5)), None, 0.16, 0.7)]), 0.4),
    "warn": (lambda: np.concatenate([blip(midi(KEY.note(3, 5)), None, 0.09, 0.8), blip(midi(KEY.note(2, 5)), None, 0.16, 0.8)]), 0.35),
    "error": (lambda: np.concatenate([blip(midi(KEY.note(1, 5)), None, 0.07, 0.8), blip(midi(KEY.note(0, 5)), None, 0.12, 0.8)]), 0.35),
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
# Four acts keyed to the timeline: tension until the reveal, the reveal, a groove under the
# product at work, a chord under the logo lockup, then a quiet bed under the credits. The key,
# mode, progression, groove and lead all come from the film's music block.

PROG = MCFG["progression"]
SNARE = {"clap": clap, "snare": snare, "rim": rim}[PRESET["snare_kind"]]
TONIC = KEY.chord("i", 4)


def at_step(bar_at, s):
    """Time of step s (0..15) in a bar, with swing on the off-16ths."""
    return bar_at + s * STEP + (SWING * STEP if s % 2 else 0.0)


def drums(at, density):
    """density 0.3: kick and hats only; 0.6 adds the snare; 0.9 adds the open hats."""
    for s in PRESET["kick"]:
        place(music, lp(kick(0.9), 900), at_step(at, s), 0.62)
    if density >= 0.6:
        for s in PRESET["snare"]:
            place(music, SNARE(), at_step(at, s), 0.5)
    if density >= 0.3:
        for s in PRESET["hats"]:
            place(music, lp(hat(), 11000), at_step(at, s), 0.22 if s % 4 else 0.3, pan=0.25)
    if density >= 0.9:
        for s in PRESET["open"]:
            place(music, hat(True), at_step(at, s), 0.16, pan=-0.2)


def harmony(at, numeral, bright, arp_level, bass_level=0.45):
    place(music, pad_chord(KEY.chord(numeral, 4), BAR + 0.5, bright), at, 0.32)
    root = KEY.bass_root(numeral, 2)
    for s, steps, octave in PRESET["bass"]:
        place(music, bass_note(root + 12 * octave, steps * STEP * 0.95), at_step(at, s), bass_level)
    if arp_level:
        deg = M.parse_numeral(numeral)[0]
        rate = PRESET["arp_rate"]
        for k, s in enumerate(range(0, 16, rate)):
            n = KEY.note(deg + PRESET["arp"][k % len(PRESET["arp"])], 5)
            place(music, lead(PRESET["lead"], n, rate * STEP * 1.2, arp_level), at_step(at, s), 1.0,
                  pan=float(np.sin(k * 1.3) * 0.4))


# Tension: the progression under a dark pad; the drums come in one layer at a time.
b = 0
while b * BAR < REVEAL:
    at = b * BAR
    place(music, pad_chord(KEY.chord(PROG[b % len(PROG)], 4), BAR + 0.6, PRESET["pad"] * 0.6), at, 0.5)
    for s, steps, octave in PRESET["bass"]:
        place(music, bass_note(KEY.bass_root(PROG[b % len(PROG)], 2) + 12 * octave, steps * STEP * 0.9), at_step(at, s), 0.4)
    if b >= 1:
        drums(at, 0.3 if b < 3 else 0.6)
    b += 1
if REVEAL > 2.4:
    place(music, riser(2.4, 0.9), REVEAL - 2.4, 0.8)

# Reveal: a hit on the tonic, and the lead states the tonic chord once.
place(music, chord_hit(TONIC + [KEY.note(0, 3)], 6.0), REVEAL, 0.9)
place(music, pad_chord(TONIC + [KEY.note(7, 4)], max(GROOVE - REVEAL, 0.5), PRESET["pad"] * 1.2), REVEAL, 0.55)
for k, d in enumerate([0, 2, 4, 7, 4, 2, 0, 4]):
    if REVEAL + 1.0 + k * BEAT / 2 < GROOVE:
        place(music, lead(PRESET["lead"], KEY.note(d, 5), BEAT * 0.6, 0.35), REVEAL + 1.0 + k * BEAT / 2, 1.0,
              pan=(-0.4 if k % 2 else 0.4))
place(music, bass_note(KEY.note(0, 2), max(GROOVE - REVEAL, 0.5)), REVEAL, 0.5)
if GROOVE - REVEAL > 1.5:
    place(music, riser(1.2, 0.5), GROOVE - 1.2, 0.4)

# Groove: the progression loops, one chord a bar. Every eighth bar breathes (no snare, no lead).
i = 0
while GROOVE + i * BAR < LOCKUP - 0.6:
    at = GROOVE + i * BAR
    breath = i % 8 == 7
    drums(at, 0.3 if breath else 1.0)
    harmony(at, PROG[i % len(PROG)], PRESET["pad"], 0.0 if breath else (0.3 if i < 8 else 0.38))
    i += 1

# Lockup: the tonic with an added ninth, and a rising run in the key.
NINTH = KEY.chord("i9", 3)
place(music, riser(1.6, 0.6), LOCKUP - 1.6, 0.55)
place(music, chord_hit(NINTH, 3.6), LOCKUP, 0.8)
place(music, pad_chord(NINTH, max(LEN - LOCKUP, 3.6), PRESET["pad"] * 1.4), LOCKUP, 0.4)
place(music, bass_note(KEY.note(0, 2), 3.4), LOCKUP, 0.4)
for k, d in enumerate([7, 9, 11, 14]):
    place(music, bell(midi(KEY.note(d, 5)), 2.4, 0.3), LOCKUP + k * 0.15, 1.0, pan=(-0.5 + k * 0.33))

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
sfx = np.stack([lp(reverb(M.apply_timbre(sfx[:, ch], TIMBRE, SR), 0.12), 11000) for ch in range(2)], axis=1)
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
if shutil.which("ffmpeg") and not os.environ.get("SCORE_RAW"):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11",
                    "-ar", str(SR), final], check=True)
    os.remove(raw)
else:
    os.replace(raw, final)
    print("ffmpeg not found: score.wav is not loudness-normalized")
print(f"score {LEN:.2f}s  {MCFG['bpm']} BPM {MCFG['root']} {MCFG['mode']} {MCFG['preset']} {MCFG['timbre']}  reveal {REVEAL:.2f}  groove {GROOVE:.2f}  lockup {LOCKUP:.2f}  -> {final}")
