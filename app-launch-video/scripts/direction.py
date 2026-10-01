#!/usr/bin/env python3
"""Check a film's DIRECTION.json: every choice traced to the product, and different from earlier films.

    direction.py check DIRECTION.json --repo <app repo> [--storyboard STORYBOARD.md]
    direction.py record DIRECTION.json          after delivery, so the next film differs from this one
    direction.py --self-test

The format is in ../references/direction.md. A copy of this file lives in the other video skill's
scripts/ folder; each skill installs on its own, so change both.

History: the bundled ../history/seed.jsonl plus the user's own file at
$VIDEO_DIRECTIONS (default ~/.local/share/video-directions/history.jsonl). A new direction may
share at most MAX_SHARED of the compared choices with any earlier film.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import music as M  # noqa: E402

MAX_SHARED = 2
ARCS = ("journey", "before-after", "scale-reveal", "build-from-nothing", "race", "day-in-the-life",
        "question-answer", "catalog")
FINALES = ("collapse-to-mark", "montage-accelerate", "zoom-out-reveal", "split-merge", "type-lockup",
           "mosaic-resolve", "trace-the-path", "loop-to-start")
LAYOUTS = ("split-caption", "lower-third", "full-bleed-type", "corner-index", "center-stack", "no-caption")
EVIDENCED = ("product", "mechanic", "audience", "tone")
REASONED = ("metaphor", "arc", "hero_motion", "finale", "layout")
# Signatures of the first film these skills made. A new film never reuses them.
FORBIDDEN = ("node rain", "and many more")
OLD_PILLARS = ("speed", "flexibility", "inspection", "iteration", "visual abstraction")
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
SEED = os.path.join(HERE, "..", "history", "seed.jsonl")
USER = os.environ.get("VIDEO_DIRECTIONS") or os.path.expanduser("~/.local/share/video-directions/history.jsonl")


def evidence_ok(ev, repo):
    if not isinstance(ev, str) or not ev.strip():
        return False
    if ev.startswith(("http://", "https://")):
        return True
    path = ev.split("#")[0].split(":")[0].strip()
    return repo is None or os.path.exists(os.path.join(repo, path))


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def shared(a, b):
    """The compared choices two directions have in common."""
    same = []
    get = lambda d, *ks: _dig(d, ks)
    for name, keys in (("arc", ("arc", "value")), ("finale", ("finale", "value")), ("hero motion", ("hero_motion", "family")),
                       ("layout", ("layout", "value")), ("groove preset", ("music", "preset")), ("sfx timbre", ("music", "timbre"))):
        if get(a, *keys) is not None and get(a, *keys) == get(b, *keys):
            same.append(name)
    if get(a, "music", "root") == get(b, "music", "root") and get(a, "music", "mode") == get(b, "music", "mode") and get(a, "music", "root"):
        same.append("key")
    ba, bb = get(a, "music", "bpm"), get(b, "music", "bpm")
    if ba and bb and abs(float(ba) - float(bb)) <= 6:
        same.append("tempo")
    ca, cb = get(a, "palette", "canvas"), get(b, "palette", "canvas")
    if ca and cb and HEX.match(ca) and HEX.match(cb) and sum((x - y) ** 2 for x, y in zip(rgb(ca), rgb(cb))) ** 0.5 < 40:
        same.append("canvas colour")
    return same


def _dig(d, ks):
    for k in ks:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def history():
    out = []
    for p in (SEED, USER):
        if os.path.exists(p):
            out += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return out


def check(d, repo=None, storyboard=None, past=None):
    errs = []
    for k in EVIDENCED:
        if not isinstance(d.get(k), dict):
            errs.append(f"{k}: missing")
        elif not evidence_ok(d[k].get("evidence"), repo):
            errs.append(f"{k}: evidence must be a file in the app repo (path or path#L12) or a URL, got {d[k].get('evidence')!r}")
    for k in REASONED:
        if not isinstance(d.get(k), dict) or len(str(d[k].get("why", "")).split()) < 6:
            errs.append(f"{k}: give a \"why\" of at least six words that ties it to the mechanic or the tone")
    if _dig(d, ("mechanic", "verb")) in (None, ""):
        errs.append("mechanic: name the physical verb the product performs, for example scan, match, route, grow")
    if len(_dig(d, ("tone", "words")) or []) < 2:
        errs.append("tone: quote at least two words from the README or the landing page")
    for k, allowed in (("arc", ARCS), ("finale", FINALES), ("layout", LAYOUTS)):
        v = _dig(d, (k, "value"))
        if v not in allowed:
            errs.append(f"{k}: {v!r} is not one of {', '.join(allowed)}")
    if not _dig(d, ("hero_motion", "family")) or not _dig(d, ("hero_motion", "value")):
        errs.append("hero_motion: needs a \"family\" (a short kebab-case name) and a \"value\" describing the motion")
    pal = d.get("palette") or {}
    if not evidence_ok(pal.get("evidence"), repo):
        errs.append("palette: evidence for the brand colours must be a file in the app repo or a URL")
    for name, need in (("brand", 1), ("invented", 3)):
        cols = pal.get(name) or []
        if len(cols) < need or not all(isinstance(c, str) and HEX.match(c) for c in cols):
            errs.append(f"palette.{name}: at least {need} colours as #rrggbb")
    if not isinstance(pal.get("canvas"), str) or not HEX.match(pal.get("canvas", "")):
        errs.append("palette.canvas: the film background as #rrggbb")
    errs += [f"music: {e}" for e in M.check(d.get("music"))]
    if isinstance(d.get("music"), dict) and len(str(d["music"].get("why", "")).split()) < 6:
        errs.append("music: give a \"why\" of at least six words that ties tempo and mode to the tone")
    text = json.dumps(d).lower() + (open(storyboard, encoding="utf-8").read().lower() if storyboard else "")
    for phrase in FORBIDDEN:
        if phrase in text:
            errs.append(f"\"{phrase}\" is the first film's signature; invent this product's own beat")
    if sum(re.search(rf"\b{w}\b", text) is not None for w in OLD_PILLARS) >= 3:
        errs.append("three or more of the first film's pillar words (speed, flexibility, inspection, iteration, visual "
                    "abstraction); take this product's own pillars from its README or landing page")
    for past_d in (history() if past is None else past):
        same = shared(d, past_d)
        if len(same) > MAX_SHARED:
            errs.append(f"too close to the earlier film {past_d.get('label', '?')!r}: shares {', '.join(same)}. "
                        f"Change all but {MAX_SHARED} of them.")
    return errs


def record(d, label):
    os.makedirs(os.path.dirname(USER), exist_ok=True)
    keep = {k: d[k] for k in ("arc", "finale", "hero_motion", "layout", "palette", "music") if k in d}
    with open(USER, "a", encoding="utf-8") as f:
        f.write(json.dumps({"label": label, **keep}) + "\n")


def example():
    return {
        "product": {"name": "Ledgerline", "evidence": "README.md#L1"},
        "mechanic": {"verb": "scan", "what": "reads text out of receipt photos", "evidence": "README.md#L5"},
        "audience": {"value": "finance teams closing the month", "evidence": "README.md#L9"},
        "tone": {"words": ["private", "instant"], "evidence": "https://example.com"},
        "metaphor": {"value": "a darkroom where text develops out of the photo", "why": "the product pulls text out of an image, like a print developing"},
        "arc": {"value": "journey", "why": "one receipt travels from a crumpled photo to a booked ledger line"},
        "hero_motion": {"family": "scan-reveal", "value": "a light bar sweeps down and leaves typed text behind it",
                        "why": "the scan is the product's mechanic, so it carries every cut"},
        "finale": {"value": "zoom-out-reveal", "why": "the one receipt becomes a month of receipts filed in a grid"},
        "layout": {"value": "lower-third", "why": "the photo needs the full frame width while it develops"},
        "palette": {"brand": ["#3b5bdb"], "invented": ["#1a1410", "#e8d5b0", "#c2410c"], "canvas": "#1a1410", "evidence": "src/theme.css#L3"},
        "music": {"bpm": 88, "root": "Eb", "mode": "dorian", "progression": ["i", "IV", "VII", "i"], "preset": "minimal-tick",
                  "swing": 0.1, "timbre": "analog", "why": "calm and precise, matching private and instant"},
    }


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as repo:
        os.makedirs(os.path.join(repo, "src"))
        for f in ("README.md", "src/theme.css"):
            open(os.path.join(repo, f), "w").close()
        good = example()
        assert check(good, repo, past=[]) == [], check(good, repo, past=[])
        twin = json.loads(json.dumps(good))
        twin["label"] = "earlier"
        assert any("too close" in e for e in check(good, repo, past=[twin])), "a copy of an earlier film must fail"
        near = json.loads(json.dumps(twin))
        near["music"].update({"bpm": 140, "root": "A", "mode": "lydian", "preset": "pulse-house", "timbre": "glass"})
        near["palette"]["canvas"] = "#f0f0f0"
        near["arc"]["value"] = "race"
        near["layout"]["value"] = "center-stack"
        assert check(good, repo, past=[near]) == [], "sharing two choices must pass"
        bad = {
            "made-up evidence file": ("product", {"name": "x", "evidence": "docs/nowhere.md"}),
            "no why": ("arc", {"value": "journey", "why": "nice"}),
            "unknown arc": ("arc", {"value": "epic", "why": "one receipt travels from a photo to a ledger"}),
            "one tone word": ("tone", {"words": ["fast"], "evidence": "README.md"}),
            "bad music": ("music", {**good["music"], "mode": "blues"}),
            "old signature": ("finale", {"value": "type-lockup", "why": "then a node rain of every feature in the product"}),
        }
        for name, (k, v) in bad.items():
            assert check({**good, k: v}, repo, past=[]), f"self-test: '{name}' was not caught"
        sb = os.path.join(repo, "STORYBOARD.md")
        open(sb, "w").write("| 0-4 | Speed |\n| 4-8 | Flexibility |\n| 8-12 | Inspection |\n")
        assert check(good, repo, storyboard=sb, past=[]), "the old pillar set in a storyboard must fail"
    seed = [json.loads(l) for l in open(SEED, encoding="utf-8") if l.strip()]
    assert seed, "history/seed.jsonl must hold the first film"
    print("self-test OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    import argparse
    ap = argparse.ArgumentParser(prog="direction.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("direction")
    c.add_argument("--repo", required=True, help="the app repository the film is about")
    c.add_argument("--storyboard")
    r = sub.add_parser("record")
    r.add_argument("direction")
    r.add_argument("--label", required=True, help="a short name for this film, for example the product and the date")
    a = ap.parse_args(argv)
    d = json.load(open(a.direction, encoding="utf-8"))
    if a.cmd == "record":
        record(d, a.label)
        print(f"recorded {a.label!r} in {USER}")
        return
    errs = check(d, a.repo, a.storyboard)
    if errs:
        print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
        sys.exit(1)
    print("direction OK")


if __name__ == "__main__":
    main(sys.argv[1:])
