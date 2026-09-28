---
name: app-launch-video
description: Build a long-form product launch video (90 s to 3 min) for an app whose source code you have. It recreates the real UI in HTML with HyperFrames and adds an offline-synthesized score whose sound effects sync to the motion. Use it when someone wants a launch video, feature showcase, commercial or product film for their own app or codebase. That includes phrases like "make a launch video for our platform", "commercial for the app", "showcase every feature", "video for the finance team", "rework the launch video", or revisions to a video made this way (captions, sync, scenes, credits). Use `brag-slim` instead for a 15 to 25 s brag clip. Use `product-launch-video` when the only input is a public URL. Use the `hyperframes` entry skill for other video kinds (captions on footage, decks, explainers without an app).
compatibility: Needs the HyperFrames skills (hyperframes, hyperframes-core, hyperframes-cli), Node with npx, ffmpeg, and Python 3 with numpy and scipy (uv works). Pillow is optional.
---

<!-- Private repo: the absolute ~/.claude/skills/ paths below are intentional. This skill and its sibling media skill are installed only on the maintainer's machine. -->

# App launch video

Make a commercial-grade launch film for an app you can read the code of. The film
shows the product doing its job, in its own UI, at a fast pace, with a score that
hits every click.

This skill sits on top of HyperFrames. Section 0 lists the HyperFrames skills and
tools it needs. This file covers the parts that
HyperFrames does not: the story shape, the scene recipes, the audio pipeline, and
the corrections one client made over 40 prompts in three sessions. Those
corrections are in `references/lessons.md`. Read it before you plan. Most first
drafts fail in the ways it lists.

## 0. Prerequisites

Check these before anything else. Stop and report what is missing. Do not work
from a remembered HyperFrames contract.

| Need | Check | Fix |
|---|---|---|
| HyperFrames skills: `hyperframes`, `hyperframes-core`, `hyperframes-cli` (and `hyperframes-animation`, `hyperframes-keyframes` for motion) | `npx --yes hyperframes skills check` | `npx --yes hyperframes skills update hyperframes-core hyperframes-cli hyperframes-animation hyperframes-keyframes`. Without the CLI: `npx skills add heygen-com/hyperframes --all`. |
| Node and npx | `node -v` | Install Node 20 or later. |
| ffmpeg and ffprobe | `ffmpeg -version` | `brew install ffmpeg`, or the platform's package manager. |
| Python 3 with numpy and scipy | `uv --version` or `python3 -c "import numpy, scipy"` | `uv run --with numpy --with scipy ...`, or a venv (`references/audio.md`). |
| Pillow (optional, labels on cue sheets) | `python3 -c "import PIL"` | `pip install pillow`. Without it, the sheets have no labels. |
| Voiceover (when the film has one): a venv with `kokoro-onnx` and `soundfile`, plus system `espeak-ng` | `<venv>/bin/python -c "import kokoro_onnx"` and `brew --prefix espeak-ng` | `uv venv .tts && uv pip install --python .tts/bin/python kokoro-onnx soundfile`; `brew install espeak-ng`. The first `npx hyperframes tts "test"` downloads the model to `~/.cache/hyperframes/tts`, even when its synthesis step fails. |
| Tween probe: `puppeteer-core` and `chrome-headless-shell` | `node tools/hold_probe.mjs` reports what it cannot find | Any `npx hyperframes` run caches puppeteer-core; `npx @puppeteer/browsers install chrome-headless-shell@stable`, or set `PUPPETEER_CORE` / `CHROME_BIN`. |

Then load `/hyperframes-core` (the composition contract) and `/hyperframes-cli`
(check, snapshot, render). Load `/hyperframes-keyframes` before you write
motion that is not in `references/motion.md`. This skill adds to those skills.
It does not repeat them.

## 1. Discover the product from the repository

The skill works on any app. Every fact in the film comes from the repository you
are invoked in, not from this skill. Read these before you ask anything. Write
what you find to `PRODUCT.md` in the video project.

| Find | Where to look |
|---|---|
| What the product does, for whom | README, docs index, landing or login page copy |
| Core loop (the 3 to 6 stages a user moves through) | Router and page list, main nav, domain docs, the editor or wizard the app centers on |
| Feature catalog for the finale | Palette or registry lists, feature flags, settings pages, docs sidebar |
| Brand | Logo files (`docs/brand`, `public/`, `assets/`), slogan and tagline strings in the frontend, philosophy or principle pages in docs |
| Look | Theme tokens (CSS variables, Tailwind config), the font stack the UI really renders, the icon package and its version |
| Real labels | Button text, dialog titles, empty states, toasts, table headers in the components |
| Real data shapes | Fixtures, seeds, test data, API specs. Use a read-only database or MCP tool when one is connected. |

Mark each item "found" (with the file path) or "missing". Never fill a missing
brand item with an invented one.

## 2. Intake (one message, then work)

Ask only for what the repository cannot tell you, in one message:

- Length target and audience.
- The missing brand items from `PRODUCT.md`.
- The step the client thinks is the product's signature. Weight it most.
- Anything to exclude (a customer name, a mascot, a feature).
- The credits: company line, company slogan, contact, and contributor names.

## 3. Plan

Write `STORYBOARD.md` and `timeline.json` before any scene HTML. Map the
product's own core loop onto this arc:

| Act | Content | Share of runtime |
|---|---|---|
| Hook | The pain the product removes, shown fast, all at once | 10% |
| Reveal | Logo and real slogan. Speed it up once everything is visible. | 5% |
| Build and explain | Do the product's main action in its main screen. After each segment, cut to a "Step NN" explainer for that stage, then come back. | 40 to 50% |
| Operate | How it runs without the user (schedule, automation), then on demand with live progress | 10 to 15% |
| Review and result | Handle the exceptions. Morph into the result view inside the same scene. Then the report or outcome. | 15% |
| Finale | Feature catalog rain, a card wall, "and many more...", the logo with pillar tags, then credits over a contributor marquee | 10 to 15% |

Keep acts the product does not have out of the film. A product with no editor
still has a main action. Build that action on screen instead.

Plan scenes as `{id, src, track, start, dur}` rows in `timeline.json`. That file is
the single source of timing. The index hosts and the score both read it.
Explainer scenes that interleave with a long "build" scene go on track 2 over it.

## 4. Build

Create the video project outside the app repository, as a sibling folder
(for example `../<product>-launch`). Nothing from the video goes into the app
repository. The kit below is a complete HyperFrames project. HyperFrames 0.8.77
was validated on 2026-09-26. On a new project, run
`npx hyperframes@latest upgrade --project . --check` first (see `/hyperframes`).
Copy the kit:

```bash
P=<project>; K=~/.claude/skills/app-launch-video
mkdir -p $P/tools $P/audio $P/assets/vendor $P/compositions
cp $K/scripts/build_index.py $K/scripts/cue_frames.py $K/scripts/hold_probe.mjs $K/scripts/vo.py $K/scripts/subs.py $K/scripts/vendor_fonts.py $P/tools/
cp $K/scripts/score.py $P/audio/
cp $K/assets/caption.js $K/assets/theme.css $P/assets/
cp $K/assets/index.html $K/assets/hyperframes.json $K/assets/package.json $P/
curl -sL https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js -o $P/assets/vendor/gsap.min.js
```

Then fill the `FROM-REPO` tokens in `assets/theme.css` and the title in
`index.html` and the name in `package.json`. Copy the logo into `assets/brand/`. Extract the icons the film
uses from the app's icon package into `assets/icons.js`, as a global map from
label to SVG inner markup. Write a `timeline.json` with a `scenes` array.

Then, per scene:

1. Recreate the real screen from the source code: the same labels, dialogs,
   icons, and data vocabulary.
2. Use the caption standard for every explainer scene. See
   `references/scenes.md`.
3. Show config in the real UI first, then visualize the process. Do not use
   a config panel as the explanation.
4. Write `compositions/<id>.cues.json` from the tween constants in the scene's
   script, never by ear. See `references/audio.md`.
5. Run `python3 tools/build_index.py` after any change to `timeline.json`.

Voiceover, when the client wants one: write `audio/vo.json` (voice, speed, and
lines of `{id, scene, t, text}`), then run `<venv>/bin/python tools/vo.py`. It
generates each changed line with local Kokoro and reports any line that runs
into the next. `score.py` places the lines and ducks the bed under them. Rules
for the lines are in `references/audio.md`. Then run `python3 tools/subs.py`.
It transcribes each line for word timings and writes the subtitle composition
on its own track.

Phones: the client watches on WhatsApp. So open with a small corner hint
("Rotate your phone · Sound on") for about 4 s, placed where the first scene is
empty. Zoom a config dialog until it fills about 88% of the frame height
(measure the dialog, then zoom = 950 / its height, at most 2.2). Burn in the
subtitles.

Motion code (camera zoom, cursors, drags, dialogs, pop and wiggle, marquee) is in
`references/motion.md`. Copy it, do not reinvent it.

For more than three scenes, build in parallel. Give each worker
`references/worker-brief.md` with the copy table filled in. Verify each worker's
scene yourself with snapshots. Workers have shipped empty flying boxes and a
missing toast that their own checks passed.

## 5. Verify, then render

Run this set of checks after every round of edits:

```bash
npx --yes hyperframes@0.8.77 check                       # lint, layout, contrast
npx --yes hyperframes@0.8.77 snapshot --describe false --no-end -o snaps-<id> --at <t1>,<t2>,...
```

- Snapshot every changed scene at its first 0.3 s, at mid-action, at mid-flight
  of anything that moves, and at its last 0.4 s. Read the images. Look for
  overlaps, clipped text, empty boxes, serif fallback text, and dark-on-dark.
- Always pass `--describe false`.
- Build the score, normalize it, render, and normalize the mp4 again. The
  commands are in `references/audio.md`.
- Check sync with `tools/cue_frames.py`. It pulls the frame at every cue of a
  scene into one contact sheet. The frame at a click cue must show the cursor on
  the target and the ripple.

To tighten pacing, run `node tools/hold_probe.mjs`. It prints each scene's end
hold, the idle time between its last action and its exit. Cut holds from that
table, not by eye.

## 6. Deliver

Report the mp4 path, the runtime, the loudness, and one line per change. Never
overwrite a render the client already has. Write the new one under a new name.
For a platform with a length limit (WhatsApp, for example), cut at a scene
boundary at or before the limit, and re-encode H.264 High, yuv420p, AAC,
`-movflags +faststart`. After a
revision round, answer each numbered item the client raised, in their order.

## Hard rules

- Never delete an earlier variant when told to "clean up". Clean processes and
  scratch files only. The client asked for the older compositions back.
- Keep real names exact. Spell out data names in full in explainers. Short
  names may stay short only where the real UI shows them short.
- Every frame is a pure function of time. Do not use `Math.random`, `Date`, `tl.call`,
  CSS transitions or infinite repeats. Use a seeded xorshift32 for "random".
- The last frame of every scene is empty.
- No idle holds over 0.8 s, except reading time: about 0.3 s per word from
  the moment the whole line is visible.
- When a revision adds content, shift later scenes in `timeline.json`. Do not
  squeeze tweens until they overlap.

## References

| File | Read it when |
|---|---|
| `references/lessons.md` | Before planning, and before each revision round |
| `references/scenes.md` | Writing any scene: caption standard, scene recipes, finale |
| `references/motion.md` | Writing tweens: camera, cursor, drag, dialog, wiggle, marquee, retiming |
| `references/audio.md` | Score, cues, loudness, sync checks |
| `references/worker-brief.md` | Handing scenes to parallel workers |
| `references/brand.md` | A missing or new logo, a palette from the mark, fonts, a rebrand |
