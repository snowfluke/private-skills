# Brand: logo, palette, fonts, rebrand

Read this when the product has no usable mark, when the client asks for a new
one, or when a rebrand changes the name.

## Designing a mark

The client said "catchy, simple, fit our platform theme" and gave no
direction. Decide it yourself. Do not put a menu of logos to the client.

1. Hand-author 3 SVG candidates on a 120 × 120 viewBox, each with 6 to 9 shapes.
2. Render them on one sheet with headless Chrome: 220 px and 40 px, on the new
   dark canvas and on white, each next to the wordmark.
3. Read the sheet. Reject what fails, and say why in one line.
   - The mark must read as the name at 40 px. A beaver needs buck teeth plus a
     light muzzle. A tail alone read as a corn dog, and a wave under the teeth
     read as a moustache.
   - The mark must stay clean on dark. Mid-brown on dark navy turned muddy.
   - A rounded app-tile silhouette with ears is catchy, and it works as a
     favicon.
4. Refine the winner once or twice on a second sheet. Save it as
   `assets/brand/mark.svg`.

Check the source assets against the name. The mascot file here was
`mascot-otter-wave.png` while the product was being renamed Beaverflow. Say so
plainly. Do not fix it silently.

## Palette from the mark

Take two brand colours from the mark, then build the rest around them:

| Token | Role | Beaverflow |
|---|---|---|
| `--canvas` | film background, deep and cool so a warm mark pops | `#0b1e26` teal-ink |
| `--accent` | brand colour from the mark: labels, highlights, the tagline | `#f6a23a` amber |
| `--flow` / `--cyan` | lines, edges, waterlines, the second collaborator | `#2dd4bf` teal |
| `--ink`, `--muted` | text on the canvas, warm white and a grey that matches the canvas | `#f6f1e7`, `#a7bab9` |
| `--app-primary` | primary buttons, switches and selected tabs inside the recreated app | `#0f2e36` |
| `--app-accent` | selection, links and focus inside the app (was blue) | `#e0661a` |
| app greys | shift the whole grey ramp one temperature: neutral to stone | `#1c1917` … `#fafaf9` |

Keep semantic colours: green for ok, amber for warn, red for bad.

## Sweeping a palette change

Never recolour by hand. Write a map from old to new values, covering hex (3 and
6 digit) and `rgb()`/`rgba()` triples. Run it over every composition and
`index.html`, then run it again with `--check` so it lists anything left.
Then remap primary controls by context (`background:` and `border-color:` of
the old primary dark), because the same dark grey is also a text colour. Last,
snapshot every scene once. A missed colour in one dialog reads as a bug.

## Fonts

A rebrand may change the font. Vendor it: `python3 tools/vendor_fonts.py
"Plus Jakarta Sans:400,500,600,700,800;300i" "JetBrains Mono:400,500,600,700"`.
Name the families only in `--ui` and `--mono`. After a font change,
re-snapshot every layout that depends on text width: wordmarks, dialog widths
and wide tables.

## Rebrand checklist

- Copy the project. The delivered film must stay reproducible from its own
  folder.
- Grep for the old name and the old logo files everywhere: compositions,
  `index.html` title, `meta.json`, `package.json`, the voiceover script and the
  credits.
- Redesign the logo intro for the new mark's shape (`scenes.md`, Logo intro).
- The tagline is the client's copy. When it must change, offer 3 or 4 short
  options with one recommended, and let the client pick.
