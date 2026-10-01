---
name: app-launch-video
description: Build a long-form product launch video (90 s to 3 min) for an app whose source code you have. Reads the repository, the README and the landing page, then invents a direction for this product alone, covering the visual world, the story arc, a signature motion, the palette, and a score with its own tempo, key, groove and sound effects. It recreates the real UI in HTML with HyperFrames, syncs every effect to the motion, and checks that the film differs from earlier ones. Use it when someone wants a launch video, feature showcase, commercial or product film for their own app or codebase, including phrases like "make a launch video for our platform", "commercial for the app", "showcase every feature", "rework the launch video", or revisions to a video made this way. Use `brag-slim` for a 15 to 25 s brag clip, `product-launch-video` when the only input is a public URL, and `motion-reel` for a looping, music-only exhibition reel.
compatibility: Needs the HyperFrames skills (hyperframes, hyperframes-core, hyperframes-cli), Node with npx, ffmpeg, and Python 3 with numpy and scipy (uv works). Pillow is optional. The ax CLI helps read the landing page.
---

# App launch video

Make a commercial-grade launch film for an app you can read the code of. The
film shows the product doing its job, in its own UI, inside a world invented
for this product, with a score that hits every action.

Two films from this skill must never look or sound alike. Each one starts
from its own `DIRECTION.json`. A script checks that file against the product and
against earlier films. The skill has no default look, story or music.

Paths below are relative to this skill's folder (the folder that holds this
`SKILL.md`). Find it first, then call each script by its absolute path.

## 0. Prerequisites

Check these before anything else. Stop and report what is missing.

| Need | Check | Fix |
|---|---|---|
| HyperFrames skills: `hyperframes`, `hyperframes-core`, `hyperframes-cli` (and `hyperframes-animation`, `hyperframes-keyframes` for motion) | `npx --yes hyperframes skills check` | `npx --yes hyperframes skills update hyperframes-core hyperframes-cli hyperframes-animation hyperframes-keyframes`. Without the CLI: `npx skills add heygen-com/hyperframes --all`. |
| Node and npx | `node -v` | Install Node 20 or later. |
| ffmpeg and ffprobe | `ffmpeg -version` | `brew install ffmpeg`, or the platform's package manager. |
| Python 3 with numpy and scipy | `uv --version` or `python3 -c "import numpy, scipy"` | `uv run --with numpy --with scipy ...`, or a venv. |
| Pillow (optional, labels on cue sheets) | `python3 -c "import PIL"` | `pip install pillow`. |
| Voiceover (when the film has one): a venv with `kokoro-onnx` and `soundfile`, plus system `espeak-ng` | `<venv>/bin/python -c "import kokoro_onnx"` and `brew --prefix espeak-ng` | `uv venv .tts && uv pip install --python .tts/bin/python kokoro-onnx soundfile`; `brew install espeak-ng`. |
| Tween probe: `puppeteer-core` and `chrome-headless-shell` | `node tools/hold_probe.mjs` reports what it cannot find | `npx @puppeteer/browsers install chrome-headless-shell@stable`, or set `PUPPETEER_CORE` / `CHROME_BIN`. |

Then load `/hyperframes-core` (the composition contract) and `/hyperframes-cli`
(check, snapshot, render). Load `/hyperframes-keyframes` for motion that is not
in `references/motion.md`.

## 1. Discover the product

Every fact in the film comes from the repository and its public pages. Write
what you find to `PRODUCT.md` in the video project, each item "found" (with the
file path or URL) or "missing".

| Find | Where to look |
|---|---|
| What it does, for whom, in the team's own words | README, docs index |
| Tone and pillars | The landing page: headline, section titles, the adjectives it uses. Find its URL in `package.json` `homepage`, the README, or the repo's website field. Fetch it with `ax`, or `curl`. |
| The mechanic: the physical verb | The main screen, the core loop (3 to 6 stages), what happens to the input |
| Feature catalog | Registries, settings pages, docs sidebar |
| Brand | Logo files, slogan and tagline strings, principle pages |
| Look | Theme tokens, the font the UI really renders, the icon package |
| Real labels and data | Button text, dialog titles, toasts, fixtures, seeds |

Never fill a missing brand item with an invented one. The brand is real; the
film's world around it is invented.

## 2. Direction

Write `DIRECTION.json` by `references/direction.md`:
- the mechanic;
- the tone, quoted from the landing page or the README;
- a world (the metaphor) where the mechanic lives;
- an arc and a finale from `references/arcs.md`;
- the hero motion: the mechanic made visible, carrying every transition;
- the layout;
- the palette: the brand colours plus three invented ones;
- the music: tempo, key, mode, progression, groove preset, swing, effect timbre.

Check it:

```bash
python3 <skill>/scripts/direction.py check DIRECTION.json --repo <app repo>
```

Fix every error before you plan. A direction too close to an earlier film
fails with the choices it shares.

## 3. Intake (one message, then work)

Ask only what the repository cannot tell you, in one message:

- Length target, audience, and where it plays (a phone, a screen, a site).
- The missing brand items from `PRODUCT.md`.
- The step the client sees as the product's signature. Weight it most.
- Anything to exclude (a customer name, a feature).
- Credits, if any: company line, slogan, contact, contributor names.
- Voiceover or not.

Show the direction in five lines (world, arc, hero motion, palette, music) in
the same message, so the client can redirect it before you build.

## 4. Plan

Write `STORYBOARD.md` and `timeline.json` before any scene HTML. Map the
product's own steps onto the chosen arc. Each row names the scene, its scene
type (`references/scenes.md`), the hand-off object into the next scene, and
the sound. Write all captions in one copy table.

Plan scenes as `{id, src, track, start, dur}` rows in `timeline.json`, with the
`music` block copied from `DIRECTION.json`. That file is the single source of
timing. The index hosts and the score both read it. Run the direction check
again with `--storyboard STORYBOARD.md`.

## 5. Build

Create the video project outside the app repository, as a sibling folder
(for example `../<product>-launch`). HyperFrames 0.8.77 was validated on
2026-09-26. On a new project, run
`npx hyperframes@latest upgrade --project . --check` first. Copy the kit:

```bash
P=<project>; K=<skill>
mkdir -p $P/tools $P/audio $P/assets/vendor $P/compositions
cp $K/scripts/build_index.py $K/scripts/cue_frames.py $K/scripts/hold_probe.mjs $K/scripts/vo.py $K/scripts/subs.py $K/scripts/vendor_fonts.py $P/tools/
cp $K/scripts/score.py $K/scripts/music.py $P/audio/
cp $K/assets/caption.js $K/assets/theme.css $P/assets/
cp $K/assets/index.html $K/assets/hyperframes.json $K/assets/package.json $P/
curl -sL https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js -o $P/assets/vendor/gsap.min.js
```

Then:
- Fill `assets/theme.css`: the `FROM-DIRECTION` tokens come from the palette, and the `FROM-REPO` tokens from the app. Its magenta placeholders show in the first snapshot when one is missed.
- Set the title in `index.html` and the name in `package.json`.
- Copy the logo into `assets/brand/`.
- Extract the icons the film uses from the app's icon package into `assets/icons.js`, as a global map from label to SVG inner markup.

Per scene:

1. Recreate the real screen from the source code: the same labels, dialogs,
   icons and data vocabulary.
2. Place it in the film's world and layout (`references/scenes.md`).
3. Hand over to the next scene with the hero motion.
4. Write `compositions/<id>.cues.json` from the tween constants in the scene's
   script, never by ear (`references/audio.md`).
5. Run `python3 tools/build_index.py` after any change to `timeline.json`.

`references/motion.md` holds the infrastructure: seek safety, camera, cursor,
drag, dialogs, typing, retiming. Copy it. Invent the hero motion and the
world's own entrances; do not reuse another film's.

Voiceover, when the client wants one: write `audio/vo.json`, then run
`<venv>/bin/python tools/vo.py`, then `python3 tools/subs.py`. Rules are in
`references/audio.md`.

For more than three scenes, build in parallel. Give each worker
`references/worker-brief.md` with every field filled, including the world and
the hero motion. Snapshot each worker's scene yourself.

## 6. Verify, then render

Run this set of checks after every round of edits:

```bash
npx --yes hyperframes@0.8.77 check
npx --yes hyperframes@0.8.77 snapshot --describe false --no-end -o snaps-<id> --at <t1>,<t2>,...
```

- Snapshot every changed scene at its first 0.3 s, mid-action, mid-flight of
  anything that moves, and its last 0.4 s. Read the images. Look for overlaps,
  clipped text, empty boxes, serif fallback text, dark-on-dark, and magenta.
- Build the score: `uv run --with numpy --with scipy python audio/score.py`.
- Render on the GPU when there is one:
  `npx --yes hyperframes@0.8.77 render --quality delivery --fps 30 --gpu --output renders/raw.mp4`.
  If `--gpu` fails, render again without it. Then normalize loudness
  (`references/audio.md`).
- Check sync with `tools/cue_frames.py`. The frame at a click cue must show
  the cursor on the target and the ripple.
- Tighten pacing with `node tools/hold_probe.mjs`. Cut holds from its table.

## 7. Deliver

Report the mp4 path, the runtime, the loudness, and one line per change. Never
overwrite a render the client already has. For a platform with a length limit,
cut at a scene boundary at or before the limit, and re-encode H.264 High,
yuv420p, AAC, `-movflags +faststart`. Answer each numbered revision item in
order.

When the client accepts the film, record its direction, so the next film
differs from it:

```bash
python3 <skill>/scripts/direction.py record DIRECTION.json --label "<product> <date>"
```

## Hard rules

- Never delete an earlier variant when told to "clean up". Clean processes and
  scratch files only.
- Keep real names exact.
- Every frame is a pure function of time. Do not use `Math.random`, `Date`,
  `tl.call`, CSS transitions or infinite repeats. Use a seeded xorshift32.
- The last frame of every scene is empty, or the first frame of the hand-off.
- No idle holds over 0.8 s, except reading time: about 0.3 s per word.
- When a revision adds content, shift later scenes in `timeline.json`. Do not
  squeeze tweens until they overlap.

## References

| File | Read it when |
|---|---|
| `references/direction.md` | Writing DIRECTION.json: the world, hero motion, palette, music |
| `references/arcs.md` | Choosing the story shape and the finale |
| `references/rules.md` | Before planning, and before each revision round |
| `references/scenes.md` | Writing any scene: layouts, caption copy, scene types, the mark |
| `references/motion.md` | Writing tweens: camera, cursor, drag, dialog, wiggle, retiming |
| `references/audio.md` | Score, cues, voiceover, loudness, sync checks |
| `references/worker-brief.md` | Handing scenes to parallel workers |
| `references/brand.md` | A missing or new logo, mapping the palette to tokens, fonts, a rebrand |
