---
name: motion-reel
description: Build a short, looping, music-driven motion-graphics reel (15 to 45 s) that shows a product through motion, with no voiceover and no subtitles, for an exhibition screen, a booth, a lobby display, a showreel or a social loop. Reads the repository, the README and the landing page, then invents a direction for this product alone, covering its world, its pillars, a signature hand-off motion, the palette, and a score with its own tempo, key and groove. Uses Remotion with a beat-grid timeline, hand-off transitions between every section, and a seamless picture-and-sound loop, and checks that the reel differs from earlier ones. Use it for requests like "30-second reel for the exhibition", "looping motion graphics for our booth", "a brand reel at 120 BPM", "make it loop seamlessly", or revisions to a reel made this way. Use `app-launch-video` for a narrated launch film and `brag-slim` for a one-off 20 s share clip.
compatibility: Needs Node with npx, Remotion (a Remotion project, or copy the template), ffmpeg, and Python 3 with numpy and scipy (uv works). The ax CLI helps read the landing page.
---

# Motion reel

A loop that a passer-by can join at any second. Every section shows a real
part of the product. Every cut hands one object to the next section. The last
frame is the first frame, and the music wraps with it.

Two reels from this skill must never look or sound alike. Each one starts
from its own `DIRECTION.json`, checked against the product and against earlier
films. There is no default tempo, palette, pillar list or music.

Paths below are relative to this skill's folder. Find it first, then call each
script by its absolute path.

## 0. Prerequisites

| Need | Check | Fix |
|---|---|---|
| Node, npx | `node -v` | Node 20 or later |
| Remotion project | `npx remotion versions` in the project | `npx create-video@latest`, then copy `assets/template/*` into `src/` |
| ffmpeg | `ffmpeg -version` | `brew install ffmpeg` |
| numpy, scipy | `uv --version` | `uv run --with numpy --with scipy python ...` |

## 1. Discover and direct

Read the landing page, the package page, the docs site or the demo, in the
order `references/direction.md` gives, then the README, the main screen and the
theme. Fetch pages with `ax`, or `curl`. A library, SDK or CLI has no UI: its
product elements are its code, its terminal and its output (`references/direction.md`,
"Products without a screen"). Then write `DIRECTION.json`. The format and
the choices (world, hero motion, palette, music) are in
`references/direction.md`; take the arc from the reel's own shape: one idea per
section, building to the mark. Check it:

```bash
python3 <skill>/scripts/direction.py check DIRECTION.json --repo <app repo>
```

Take the section ideas from the product's own pillars, as
`references/recipes.md` describes: the landing page's section titles, the
README's feature headings, or the core loop.

## 2. Decide the grid

- BPM from `DIRECTION.json` `music.bpm`. The loop length is a whole number of
  bars: `seconds x bpm / 240` must be whole. For 30 s that holds at 96 (12
  bars), 104, 112, 120 and 128 BPM. Pick the tempo with the length in mind, so
  the stated length is the real one. A half bar never resolves musically.
- Format from the venue (1920 x 1080 at 30 fps unless told otherwise).
- The loop length in frames is a whole number. The score uses that exact
  length (`references/loop.md`).

## 3. Storyboard as a hand-off table

Write `STORYBOARD.md` before any code, as one table:

```markdown
| Beats | Section | Energy | On screen | Hand-off | Sound |
|---|---|---|---|---|---|
| 0-8 | <id> | intro | the real product element | the object that becomes the next section | the cue names |
```

`Energy` is one of intro, build, drop, break, logo, outro.

Cut any row that shows no real product element, or that has no hand-off object.
Abstract motion with no product in it says nothing about the product. Run the
direction check again with `--storyboard STORYBOARD.md`.

## 4. Build

- Copy `assets/template/*` into `src/`, and `scripts/check_loop.py` and `scripts/finalize.sh` into `tools/`.
- Fill `theme.ts` and `fonts.ts` from `DIRECTION.json`. The magenta placeholders show in the first preview when you miss one.
- Write `src/timeline.json` (shape below).
- Write one scene file per section. Each takes the section-local beat `b` and is a pure function of it. `Reel.tsx` picks the section by beat; there are no Remotion `Sequence` cuts.
- Time everything in beats: pops on beats, fast details on 8ths and 16ths.
- Exhibition rules: words at 120 px or more, one idea per bar, high contrast. Rows and log lines are texture only.
- The hero motion carries the hand-offs (`references/recipes.md`).

`src/timeline.json`:

```json
{
  "bpm": 96, "fps": 30, "beats": 48,
  "music": { "...": "copied from DIRECTION.json; its bpm equals the bpm above" },
  "sections": [ { "id": "<id>", "start": 0, "len": 8, "energy": "intro" } ],
  "handoffs": [ { "beat": 4, "label": "<what hands over>" } ],
  "gate": [44.15, 45.95],
  "cues": [ { "beat": 0, "sfx": "hit" }, { "beat": 3.5, "sfx": "type:6" } ]
}
```

- `handoffs` lists hand-offs inside a section, for the check sheet; section boundaries are covered without it.
- `gate` (optional) silences the music between two beats for a breath; the effects keep playing.
- Cue names:
  - whoosh, swish, drag, zip, sweep, suck;
  - hit, impact, slam, thud;
  - pop, popcluster, click, tick, flip, draw, zap, blips, echo;
  - glitch, boing, splash;
  - success, chime, shimmer, sparkle;
  - `type:N` for N key taps.

## 5. Score

```bash
cp <skill>/scripts/score.py <skill>/scripts/music.py audio/
uv run -q --with numpy --with scipy python audio/score.py
```

It reads `src/timeline.json`:
- the `music` block for the key, mode, progression, groove and effect timbre;
- the sections' `energy` roles for the arrangement;
- the cues (`{"beat", "sfx"}`).

It writes `public/score.wav` at -14 LUFS. Its bpm must equal the timeline's bpm.
The loop seam code is explained in `references/loop.md`.

## 6. Verify, then deliver

Render on the GPU when there is one. `--gl=angle` draws on the GPU, and
`--hardware-acceleration=if-possible` encodes on it when the codec allows, and
on the CPU otherwise:

```bash
npx tsc --noEmit -p .
npx remotion render Reel out/preview.mp4 --scale=0.5 --codec h264 --crf 23 --gl=angle
npx remotion render Reel out/render.mp4 --codec h264 --crf 18 --gl=angle --hardware-acceleration=if-possible
sh tools/finalize.sh out/render.mp4 public/score.wav out/<name>      # <name>.mp4 and <name>-x3.mp4
uv run --with numpy python tools/check_loop.py out/<name>.mp4         # hand-off and seam sheets
```

If `--gl=angle` fails, drop it. Read `checks/handoffs.png`: each boundary must
look like one object in motion. Read `checks/seam.png`: the last frames and
the first frames must be the same picture. Deliver the single loop and the 3x
file (for players that stutter on restart).

When the client accepts the reel, record its direction:

```bash
python3 <skill>/scripts/direction.py record DIRECTION.json --label "<product> reel <date>"
```

## References

| File | Read it when |
|---|---|
| `references/direction.md` | Writing DIRECTION.json: world, hero motion, palette, music |
| `references/recipes.md` | Writing a section: pillars, kinetic type, hand-offs, the mark |
| `references/loop.md` | Loop seam for picture and sound, and loudness |
| `references/arcs.md` | The arc and finale names DIRECTION.json allows |
| `references/brand.md` | A missing or new mark, palette tokens, fonts |
