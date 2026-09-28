# Motion recipes

Every snippet assumes one paused GSAP timeline `tl` per scene, registered on
`window.__timelines["<id>"]`. The renderer seeks to arbitrary times. So every
value on screen must be a pure function of the timeline position.

## Seek-safety rules

| Do | Do not | Why |
|---|---|---|
| `fromTo(..., { immediateRender: false })` for a second tween on the same property | a bare `to()` after an earlier tween on that property | When the renderer seeks backwards, the `to()` start value is wrong. |
| `tl.set(el, {...}, t)` for instant changes | `tl.call(...)` | A callback does not rerun on a seek. |
| a proxy object tween with `onUpdate` for text, counters and wiggles | `setInterval`, CSS animation, CSS transitions | Only the timeline is seeked. |
| a seeded `xorshift32` or a hash of the index | `Math.random()`, `Date` | Every frame must render the same on every run. |
| swap between two elements with opacity | a GSAP `className` tween | GSAP 3 does not tween class names. |
| hidden initial states in CSS (`opacity: 0`) | a tween at t=0 that hides | The first frame would show a flash of the visible state. |
| bound every continuous motion to end before the next tween on the element | a wiggle that overlaps a fall | Its `onUpdate` pins the element and the fall does nothing. |

## Element position for flight paths

This helper finds an element's position in scene coordinates for a flight
start or target. It reads the layout once, at build time.

```js
const at = (el) => { let x = 0, y = 0;
  for (let n = el; n && n !== root; n = n.offsetParent) { x += n.offsetLeft; y += n.offsetTop; }
  return { x, y }; };
```

Give the containers along the chain `position: relative` or `absolute`.
Otherwise `offsetParent` skips them. Append flying chips to the scene root.

## Camera (Screen Studio style)

Wrap the whole editor in `#<id>-cam`. Make one eased move at a time and clamp
it so the frame never shows past the edges.

```js
let view = { z: 1, x: 0, y: 0 };
const clampView = (z, fx, fy) => ({ z,
  x: Math.min(0, Math.max(1920 - 1920 * z, 960 - fx * z)),
  y: Math.min(0, Math.max(1080 - 1080 * z, 540 - fy * z)) });
tl.set(CAM, { x: 0, y: 0, scale: 1, transformOrigin: "0 0" }, 0);
const camTo = (t, dur, z, fx, fy, ease = "power3.inOut") => {
  const v = clampView(z, fx, fy);
  tl.fromTo(CAM, { x: view.x, y: view.y, scale: view.z },
    { x: v.x, y: v.y, scale: v.z, duration: dur, ease, immediateRender: false }, t);
  view = v; };
const camSet = (t, z, fx, fy) => { const v = clampView(z, fx, fy); tl.set(CAM, { x: v.x, y: v.y, scale: v.z }, t); view = v; };
```

Zoom to 1.3 to 1.6 on the working area for a drag or a dialog. Return to 1 before
you cut away. Author the calls in time order, because `view` carries state.

## Cursor, click, ripple

```js
let cprev = { x: 420, y: 520 };
tl.set(cursor, cprev, 0);                               // no cursor at 0,0 on frame one
const moveTo = (t, dur, p, ease = "power2.inOut") => {
  tl.fromTo(cursor, { x: cprev.x, y: cprev.y }, { x: p.x - 4, y: p.y - 4, duration: dur, ease, immediateRender: false }, t);
  cprev = { x: p.x - 4, y: p.y - 4 }; };
const click = (t, p) => {
  tl.set(RIPPLE, { x: p.x - 40, y: p.y - 40 }, t);
  tl.fromTo(RIPPLE, { opacity: 0.85, scale: 0.3 }, { opacity: 0, scale: 1.4, duration: 0.35, ease: "power2.out", immediateRender: false }, t); };
```

Put the cursor last in the scene root, with `z-index` above the dialogs.

## Drag from a palette

The drag has two tempos. The main cursor is snappy. A collaborator's cursor is
human-paced. The client rejected a fast second cursor as "way too fast and
not smooth".

| Phase | Main cursor | Collaborator cursor |
|---|---|---|
| reach the palette item | 0.16 s `power2.out` | 0.35 s `power2.inOut` |
| grab (ghost appears) | at +0.15 | at +0.40 |
| carry to the drop point | 0.28 s `expo.out` | 0.55 s `power2.inOut` |
| drop (ghost fades, node pops `scale 0.85→1`) | at +0.44 | at +1.00 |

Give the collaborator its own cursor color, a name pill and its own ripple. Put
its ghost to the side of the cursor, so the name pill does not collide with the
ghost (the layout check flags it). Add a presence count and an avatar to the
editor header.

## Rotating an SVG part

Use GSAP's `svgOrigin` in both halves of the tween:
`{ rotate: -90, svgOrigin: "12 12" }` rotates about the viewBox point (12, 12).
A CSS `transform-origin` on a `<g>` rotated the icon about the wrong point.

## Dialogs

Build dialogs from the app's real dialog markup: header, sub-line, body fields,
and footer buttons. Mark only true overlays with `data-layout-ignore`.

```js
const dialogIn = (t, id) => {
  tl.fromTo(OVERLAY, { opacity: 0 }, { opacity: 1, duration: 0.18, immediateRender: false }, t);
  tl.fromTo(id, { opacity: 0, scale: 0.95 }, { opacity: 1, scale: 1, duration: 0.22, ease: "power2.out", immediateRender: false }, t); };
const dialogOut = (t, id) => {
  tl.to(id, { opacity: 0, scale: 0.97, duration: 0.14, ease: "power2.in" }, t);
  tl.to(OVERLAY, { opacity: 0, duration: 0.16 }, t); };
```

To toggle a switch or change a value, stack two versions of the element and
cross-fade them. Class tweens do not work.

## Edges with arrowheads

Draw an edge with `strokeDashoffset` from its length to 0. Keep the arrowhead
as a separate path that fades in when the stroke lands. An SVG marker would
show the arrowhead before the line is drawn.

## Typing and counters

```js
const p = { k: 0 };
tl.fromTo(p, { k: 0 }, { k: TEXT.length, duration: TEXT.length * 0.035, ease: "none", immediateRender: false,
  onUpdate: () => { el.textContent = TEXT.slice(0, Math.round(p.k)); } }, t);
```

## Pop in place, then a bounded wiggle

```js
const hash = (n) => ((n * 2654435761) % 1000) / 1000;           // deterministic 0..1
tl.fromTo(el, { x, y, opacity: 0, scale: 0.4 }, { x, y, opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.2)", immediateRender: false }, t0);
const ph = hash(i + 31) * 6.28, ph2 = hash(i + 41) * 6.28, wspan = fall - t0 - 0.22;
const wig = (s) => ({ x: x + 8 * Math.sin(s * 9 + ph) + 3 * Math.sin(s * 23 + ph2),
                      y: y + 6 * Math.cos(s * 8 + ph2) + 3 * Math.sin(s * 19 + ph),
                      rotate: 2.5 * Math.sin(s * 7 + ph), scale: 1 + 0.03 * Math.sin(s * 11 + ph2) });
let end = { x, y };
if (wspan > 0.03) {
  const w = { q: 0 };
  tl.fromTo(w, { q: 0 }, { q: 1, duration: wspan, ease: "none", immediateRender: false,
    onUpdate: () => gsap.set(el, wig(w.q * wspan)) }, t0 + 0.22);
  end = wig(wspan); }
tl.fromTo(el, end, { ...end, y: end.y + 1250, duration: 0.55, ease: "power2.in", immediateRender: false }, Math.max(fall, t0 + 0.22));
```

Place the items on one or two tight ellipses around the title (inner ring up to
7 items). The client rejected items scattered to the frame edges.

## Seeded shuffle and a fair round-robin deal

```js
let seed = 2463534242;
const xorshift32 = () => { seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5; seed >>>= 0; return seed / 4294967296; };
const order = NAMES.slice();
for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(xorshift32() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
const rows = Array.from({ length: ROWS }, () => []);
order.forEach((name, i) => rows[i % ROWS].push(name));   // each name in exactly one row
```

Repeat each row's text enough times to cover its travel. Alternate the direction
per row. Use a constant speed (`ease: "none"`).

## A streaming list that scrolls

Follow the newest row. Read the row bottoms at render time, so a late font swap
cannot leave the scroll short.

```js
const bottom = (i) => rows[i].offsetTop + rows[i].offsetHeight;   // offsetParent is the table
const follow = { k: 0 };
const scrollToFollow = () => {
  const i = Math.min(Math.floor(follow.k), rows.length - 1), j = Math.min(i + 1, rows.length - 1);
  wrap.scrollTop = Math.max(0, bottom(i) + (bottom(j) - bottom(i)) * (follow.k - i) - wrap.clientHeight); };
tl.fromTo(follow, { k: 0 }, { k: rows.length - 1, duration: (rows.length - 1) * STAGGER, ease: "none",
  immediateRender: false, onUpdate: scrollToFollow }, STREAM0 + ROWDUR / 2);
```

Do not tween `scrollTop` to a huge sentinel value. The browser clamps it to the
bottom on the first frame, so the early rows appear off-screen while their
ticks play.

## Morph inside a scene

To show cause and effect, keep the scene and swap the view. The acted-on
element stays put. The old panel fades and scales down, the new panel scales up
from the same anchor, and then the changed item highlights (a ring or a badge
pops). Give every cell of a repeated grid the same inner slots. A cell that
gains an extra child during the morph shifts its siblings.

## Retiming

A speed wrapper for a reused scene (record `speed` in `timeline.json`):

```js
const SPEED = 1.6;
window.__timelines[ID] = gsap.timeline({ paused: true })
  .to(tl, { time: tl.duration(), duration: tl.duration() / SPEED, ease: "none" }, 0);
```

A time proxy to shift whole segments of a long scene without rewriting each time:

```js
const master = gsap.timeline({ paused: true });
let SHIFT = 0;
const at_ = (t) => { if (typeof t !== "number") throw new Error("numeric positions only"); return t + SHIFT; };
const tl = { set: (e, v, t) => master.set(e, v, at_(t)),
             to: (e, v, t) => master.to(e, v, at_(t)),
             fromTo: (e, a, b, t) => master.fromTo(e, a, b, at_(t)) };
// ... segment A at authored times ...
SHIFT = 3.2;   // everything after this line plays 3.2 s later
```

A negative SHIFT is a trap. A call at "0 + SHIFT" lands before the scene
starts, and GSAP answers a negative insertion by pushing every child later. The
flow scene started 0.99 s late, blank, until a probe showed its first tween at
0.99. Make `at_` throw when `t + SHIFT < 0`. Put setup calls at absolute 0 on
the master timeline, not through the proxy.

After you raise a SHIFT, push the matching explainer scenes and every later scene
back by the same amount in `timeline.json`. Then rerun `build_index.py` and the
score.
