# Audio: score, cues, loudness, sync

The score is synthesized offline by `audio/score.py` and `audio/music.py` (copied
from this skill's `scripts/`). It writes the music and every sound effect into one
WAV. No samples, no network. The same music block always gives the same file, and
two films with different blocks never sound alike.

```
timeline.json ──┬──> tools/build_index.py ──> index.html hosts
                └──> audio/score.py <── compositions/<id>.cues.json (one per scene)
                          │
                          ├──> assets/audio/score.wav      (music + sfx, loudnorm -15 LUFS)
                          └──> assets/audio/score-sfx.wav  (effects only, for checks)
```

## Run it

```bash
uv run --with numpy --with scipy python audio/score.py
# no uv:  python3 -m venv .venv && .venv/bin/pip install numpy scipy && .venv/bin/python audio/score.py
```

A bare `python3` often lacks scipy (`ModuleNotFoundError: scipy`). Use one of the
two lines above, and keep the venv outside the rendered folders.

The music comes from the `music` block in `timeline.json`, copied unchanged
from `DIRECTION.json`: `bpm`, `root`, `mode`, `progression`, `preset`, `swing`,
`timbre`. Without it, the score stops. The key also tunes the tonal effects
(success, chime, warn, error, pop), and the timbre colours every effect, so
the effects belong to the film's world.

Optional timing in `timeline.json`:

```json
"score": { "reveal": "s3", "groove": "build", "lockup": ["finale", 10.84], "lufs": -15 }
```

- `reveal` is the scene where the music first opens up, with a hit on the tonic chord: where the product's name or its main screen first appears.
- `groove` is where the product-at-work beat starts.
- `lockup` is the scene and the offset where the final chord lands under the
  logo lockup.

Rerun the score after every timing change. Stale audio is the most common cause
of "the sound is out of sync".

## Writing cues

`compositions/<id>.cues.json`:

```json
[
  { "t": 0.05, "sfx": "whoosh" },
  { "t": 1.65, "sfx": "click" },
  { "t": 1.90, "sfx": "tick" },
  { "t": 4.53, "sfx": "success" },
  { "t": 6.40, "sfx": "swish" }
]
```

- `t` is scene-local, in the scene's own unscaled time. The score divides by the
  scene's `speed`.
- Names: `whoosh swish drag riser pop click key tick drop thunk chime success
  warn error stamp slam impact shimmer`, plus `type:N` (N key clicks 0.05 s
  apart). An unknown name stops the build with the list.
- Derive every cue from the constants in the scene script. Do not place cues by
  ear, and do not nudge them after a measurement.

```js
// in the scene                          // in cues.json
const STREAM0 = 1.9, STAGGER = 0.06;     // ticks at 1.9 + i*0.06*2 (every other row)
const sendClick = 4.43;                  // click 4.43
toast at sendClick + 0.1                 // success 4.53
```

  One session "fixed" a cue by the measured offset in the wrong direction. The
  client heard it as delayed audio.
- One cue per visible action. For a stream of 20 rows, tick every other row. Keep
  background actions sparse. The effects sit under the music, not on top.
- Swell sounds (`whoosh swish drag riser`) are loudest mid-envelope. The score
  starts them early, so their peak lands on the cue. Put the cue where the
  motion is fastest, not where it starts.
- Click and pop sounds have an attack at 0. Put the cue on the frame where the
  ripple or the item first appears.

## Voiceover

```
audio/vo.json ──> tools/vo.py (Kokoro, local) ──> assets/audio/vo/<id>.wav ──> audio/score.py (duck + mix)
```

```json
{ "voice": "af_heart", "speed": 1.05,
  "lines": [ { "id": "05-ingest", "scene": "ingest", "t": 0.1, "text": "Pull files from SFTP, email, and APIs." } ] }
```

- Write literal lines that describe what is on screen at that moment, in the
  order it appears. Never paraphrase the caption. Never use metaphor.
- Anchor each clip to a visual beat, not to the scene start. Put the key noun
  on the beat: "Excel template" as the template editor opens, "Gantt chart" as
  the Gantt tab switches. Read the beats from the scene constants or
  `hold_probe.mjs --json`.
- When one sentence spans several beats, split it into clips, one per beat
  ("Mark the day final," on the dialog; "and it shows as final in Final
  Outputs." on the morph).
- Leave the build segments between explainers silent, so the music breathes.
- Give every finale beat a line (node rain, card wall, "and many more", name,
  tagline, credits). When a beat is shorter than its line, slow the build
  (stagger the cards over the line's length). Do not add a hold.
- Time 3 or 4 candidate lines with Kokoro before you place one. Commas add
  pauses, and a list of four nouns ran 3.95 s where 2.9 s was free.
- Speak the tagline once, at the finale lockup, and only if it is literal.
  Credits: say what the client asks ("Built by us. Innovation towards
  intelligence."), not the full legal company name.
- Plan about 3 words a second at speed 1.05. Acronyms read letter by letter
  ("SFTP", "APIs"), so they take longer. Start a line 0.1-0.3 s into its
  scene. `vo.py` flags a line that runs into the next.
- Never state a number the film does not show. Count it in the source first.
  The finale showed 53 nodes while the brief said 55, so the line lists the
  categories instead.
- `t` is scene-local wall-clock seconds, even for a speed-wrapped scene.
- `vo.py` calls Kokoro directly, not `npx hyperframes tts`. The CLI's wrapper
  does not pass espeak's data path, and the macOS `espeakng-loader` wheel
  points at its CI machine (`/Users/runner/.../phontab: No such file`). The
  script uses the system `espeak-ng` (`brew install espeak-ng`; `ESPEAK_PREFIX`
  overrides it).
- The voice is local and offline. If the client wants a cloud voice (HeyGen,
  ElevenLabs), follow `/media-use` `audio/references/tts.md`.
- Subtitles: `tools/subs.py` transcribes each clip with local whisper
  (`npx hyperframes transcribe`) and caches `<id>.words.json`. It shows the
  script's text, not whisper's spelling. One chunk is one sentence; above 12
  words it splits at a comma. At 9 words it split lists ("CSV, text" / "and
  Excel …"), which read badly.
- Mix: the music ducks about 8 dB and the effects about 4 dB while the voice
  speaks. The voice's speaking RMS is 2.2 times the bed's. Check the result:
  the mix measures 4-6 dB louder inside a line than in the gap after it.

## Loudness

`score.py` normalizes the WAV to -15 LUFS integrated with ffmpeg `loudnorm`.
`--gpu` encodes on the GPU, and Chrome captures on the GPU by default
(`--browser-gpu` is automatic). If `--gpu` fails on a machine without a usable
encoder, render again without it. The render can shift the level. Long, quiet credits pull the integrated value
down. So normalize the final mp4 again without re-encoding the video:

```bash
npx --yes hyperframes@0.8.77 render --quality delivery --fps 30 --gpu --output renders/raw.mp4
ffmpeg -y -loglevel error -i renders/raw.mp4 -c:v copy -af loudnorm=I=-15:TP=-1.5:LRA=11 \
  -ar 48000 -c:a aac -b:a 256k renders/film.mp4
ffmpeg -hide_banner -i renders/film.mp4 -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1
```

If only the audio changed, do not render again. Mux the new score onto the
existing video:

```bash
ffmpeg -y -loglevel error -i renders/film.mp4 -i assets/audio/score.wav -map 0:v -map 1:a -c:v copy \
  -af loudnorm=I=-15:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 256k -shortest renders/film-new.mp4
```

## Checking sync

Use the frames, not a meter.

```bash
python3 tools/cue_frames.py renders/film.mp4 <scene-id> --offset 0.1
```

This pulls the frame at every cue (and 0.1 s after) into
`cue-sheets/<scene-id>.jpg`. Read it:

| Cue | The frame at the cue shows |
|---|---|
| click | cursor on the target; ripple visible at +0.1 |
| pop | the item at the start of its scale-in |
| drop | the chip or node landing |
| success | the toast entering |
| whoosh / swish | the panel mid-move (fastest point) |

An automatic "audio onset versus motion peak" check on the mixed track is not
reliable. The music beat produces stronger onsets than the
effects, and a flight's motion peaks mid-flight. If you want a number, measure
onsets on `score-sfx.wav`, not on the mix. Still treat the contact sheet as the
proof.
