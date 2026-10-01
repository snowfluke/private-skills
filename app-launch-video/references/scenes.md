# Scene recipes

Every scene follows the film's `DIRECTION.json`: its layout, its world and its
hero motion. Nothing in this file sets the look.

## Layouts

The frame is 1920 x 1080. Keep a 90 px safe margin on every side. Inside
recreated UI, body text is at least 16 px, table text at least 17 px, and
headings 24 to 34 px.

| `layout` | Frame |
|---|---|
| `split-caption` | Caption column x 140-740 from y 250; the UI in x 800-1860, y 90-990 |
| `lower-third` | The UI or media fills x 90-1830, y 90-800; the caption sits under it, y 840-990 |
| `full-bleed-type` | The title is the picture (160-260 px); the UI appears as a small element inside the type or behind it |
| `corner-index` | A step index (`03 / 07`) and a short title in one corner; the UI fills the rest |
| `center-stack` | One object centred, up to 1100 px wide; the caption centred under it |
| `no-caption` | No text layer; the voiceover or the motion carries the meaning |

Full-frame moments (the opening, the hero motion's big beats, the finale) may
drop the caption in any layout.

## Caption copy

The copy rules hold in every layout. The styles are in `assets/theme.css`
(`.cap`, `.cap-label`, `.cap-title`, `.cap-desc`); restyle them for the layout.
The motion is in `assets/caption.js` (`capIn`, `capOut`).

| Part | Rule | Bad | Good |
|---|---|---|---|
| label | `GROUP · NAME`. Use the product's own phase words for the group. | `STEP 01 · INGESTION` then a title "Ingestion." | `Step 01 · Ingestion` |
| title | A 2 to 4 word action phrase. No period. Never repeats the label. | "Ingestion." | "Pull data from anywhere" |
| desc | One factual sentence of 25 words or fewer, from the code or the docs. | "Streamline your workflow." | "Fetch files from SFTP, email, APIs and storage." |

Write all captions into one copy table in `STORYBOARD.md` first and review it
as a set.

## Scene types by mechanic

Use the types the product has. Each shows its step in the real UI, then
visualizes what happens to the input, in the film's world.

| Type | Configure in the real UI | Then show |
|---|---|---|
| transform | the form or file picker that sets the input | raw input passes through the hero motion and lands in its new shape |
| match | the rule or key setting | items from two sides pair up; the ones that do not pair are set aside |
| route | the destination or rule list | one item travels a path that branches to several outcomes |
| inspect | the filter or query | a lens or highlight moves over the data and stops on the finding |
| schedule | the schedule setting | time passes in the film's world; runs fire on their own |
| generate | the prompt or template | the output builds piece by piece from the input |
| collaborate | a share or invite dialog | a second named cursor joins and works at the same time |

Pacing for one step scene, 3.5 to 7 s:

```
0.0       scene in (the hero motion hands over from the last scene)
0.4       the real config UI; the cursor sets one or two values that matter
~40%      the process in the film's world, with real-looking data
~85%      the result, held for reading time
DUR-0.35  out, into the next hand-off
```

- Move real objects: fields, rows, files, messages with visible text. An empty
  flying box reads as a bug.
- If an earlier scene already showed this step's config, go straight to the
  process.
- A state change ("approve", "publish") morphs into the result inside the same
  scene. Start the morph as soon as the change settles; hold the result about
  0.8 s after its last reveal.
- Show progress as real log lines or a timeline that fills. Never show a
  static spinner.

## The main screen

When the product centres on one screen (an editor, a board, a canvas), it
earns one long scene on track 1, with step scenes cutting in over it on
track 2. Build it from the app's real components and icons. Move the camera
with one eased zoom at a time (`motion.md`).

## Products without a screen

For a library, an SDK, a CLI or an API, the real screens are:
- the editor with the code a user writes, in the product's own API names;
- the terminal session;
- the artefact the product makes, shown as it forms;
- the demo or playground, when there is one.

Use the same scene types: the "config" is the call and its options, and the
"process" is the artefact forming in the film's world.

## Pages never load

A recreated page arrives with its body. Rebuild what sits under the header
(stats, cards, lists) from the real component, and bring it in with the window
within 0.1 s. A window with only a header reads as a loading state.

## Opening and mark

- Open inside the film's world, on the problem the product removes, at full
  pace from the first frame.
- Design the mark's entrance for its shape and the world. A flat mark can spin
  and snap; a mascot moves like itself. Carry a shape from the previous scene
  into the mark's entrance, so the cut connects.
- The finale comes from `arcs.md`. Hold the closing words about 1.5 s, then
  leave about 1 s before the mark lands.

## Credits and phone viewers (ask in intake)

- Credits: the company line, slogan and contact the client gives, over the
  contributor names. Lay the names out in the film's world (rows, a grid, a
  path); never size names unequally.
- Phone viewers: when the client watches on a phone, add a short corner hint
  (rotate the phone, sound on) for about 4 s, zoom dialogs to about 88% of the
  frame height (`zoom = 950 / dialog height`, at most 2.2), and burn in
  subtitles.

## Reusing and retiming scenes

- To speed up a reused scene, wrap it in a speed wrapper. Record `speed`,
  `old_start` and `old_dur` in `timeline.json` so the score can remap its cues.
- To insert content in a long scene, shift every later segment with a time
  proxy (`motion.md`), then push the later scenes back in `timeline.json`. Do
  not compress existing tweens.
