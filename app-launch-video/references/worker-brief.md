# Worker brief template

Copy this into the video project as `WORKERS.md`. Fill every `{{...}}` from
`PRODUCT.md` and `STORYBOARD.md`. Give each worker one or two scenes and this
file. Workers run in parallel, so each one owns only its own files.

After a worker reports back, snapshot its scene yourself before you accept it.
Workers have passed their own checks with empty flying boxes, missing toasts,
serif fallback text, and ghost cells that overlap.

---

# Worker brief: {{PRODUCT}} launch film scenes

You build one or two HyperFrames scene files for a launch film of
{{PRODUCT}}, {{ONE-LINE WHAT IT DOES}}. The audience is {{AUDIENCE}}. The tone is
{{TONE}}. You recreate the real app UI in HTML with the exact labels given
below. Never invent product claims, slogans, numbers about the product, or UI
labels that are not in this brief or in the app's source. Illustrative data
(file names, amounts, ids) is fine.

- Project: `{{ABSOLUTE PROJECT PATH}}`.
- App source for reference: `{{ABSOLUTE REPO PATH}}`. The components are in
  `{{PATHS}}`.
- Work only in your assigned files. Do not edit `index.html`, `timeline.json`,
  `assets/theme.css`, or other scenes.
- Use absolute paths in every command.

## Composition contract

- File: `compositions/<id>.html`. It holds a `<template>` with a `<style>`, one
  root `<div id="<id>-root" data-composition-id="<id>" data-width="1920" data-height="1080">`,
  and a `<script>` IIFE.
- Scope every CSS rule under `#<id>-root`. Prefix every element id with `<id>-`.
- Use one paused GSAP timeline, registered as `window.__timelines["<id>"] = tl`.
- Seek-safe only. No `Math.random`, `Date`, `tl.call`, CSS animations or
  transitions, and no `repeat: -1`. A second tween on the same property uses
  `fromTo` with `immediateRender: false`. Set initial hidden states in CSS.
- The background is transparent. `index.html` draws it.
- Enter in the first 0.5 s. Exit in the last 0.4 s. The last frame is empty.
- Readability: a line meant to be read stays settled for about 0.3 s per word.
- No idle hold over 0.8 s.
- Give every app window the `app` class. Without it, the text falls back to
  serif and dark-on-dark.

## Look

- Tokens and classes are in `assets/theme.css`: `.app`, `.badge`, `.btn`,
  `.cursor`, `.ripple`, and the caption classes.
- Icons: use `window.{{ICON GLOBAL}}[label]`, the real icon paths extracted
  from `{{ICON PACKAGE}}`.
- Layout: {{LAYOUT}} as `references/scenes.md` sets it out ({{LAYOUT FRAME}}).
  Window body text is at least 16 px, table text at least 17 px.
- The film's world: {{METAPHOR}}. Its hand-off between scenes is the hero
  motion: {{HERO MOTION}}. Enter and exit with it; do not invent another.

## Caption standard (mandatory)

```html
<div class="cap" id="<id>-cap">
  <div class="cap-label">{{LABEL}}</div>
  <div class="cap-title">{{TITLE}}</div>
  <div class="cap-desc">{{DESCRIPTION}}</div>
</div>
```
`window.capIn(tl, "<id>-cap", 0.05)` to enter.
`window.capOut(tl, "<id>-cap", <exit time>)` to exit.
Use exactly this copy:

| scene id | label | title | description |
|---|---|---|---|
| {{id}} | {{Step 01 · Stage}} | {{Action phrase}} | {{One factual sentence.}} |

## Scene recipe

Scene type: {{SCENE TYPE}} (`references/scenes.md`, "Scene types by mechanic").
Show config in the real UI first, then the process in the film's world with
real-looking data, then the result. Details: `references/scenes.md` and
`references/motion.md` in the app-launch-video skill folder.

## Sound cues

Write `compositions/<id>.cues.json` as `[{ "t": <scene-local s>, "sfx": "<name>" }]`.
Derive each `t` from your tween constants.
Names: `whoosh swish drag riser pop click key tick drop thunk chime success warn error stamp slam impact shimmer type:N`.
Put one cue on each visible action.

## Verify

1. `cd {{PROJECT}} && npx --yes hyperframes@0.8.77 check` must pass, with no `✗`
   line that names your elements. Use `data-layout-ignore` only on true
   overlays (dialogs, toasts, popovers).
2. `npx --yes hyperframes@0.8.77 snapshot --describe false --no-end -o snaps-<id> --at <t1>,...`
   at 6-10 global times: the first 0.3 s, the middle, mid-flight of anything
   that moves, and the last 0.4 s. Always pass `--describe false`. Read the
   images and fix what you see. Then delete the snaps folder.
3. Global time = the scene's `start` in `timeline.json` + the scene-local time.

Report back:
- The file names.
- One line of choreography with the scene-local times.
- Anything from this brief that you could not follow.
