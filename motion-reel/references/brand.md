# Brand: logo, palette, fonts, rebrand

Read this when the product has no usable mark, when the client asks for a new
one, or when a rebrand changes the name.

## Designing a mark

When the product has no usable mark and the client gives no direction, decide
it yourself. Do not put a menu of logos to the client.

1. Hand-author 3 SVG candidates on a 120 x 120 viewBox, each with 6 to 9 shapes.
2. Render them on one sheet with headless Chrome: 220 px and 40 px, on the
   film's canvas colour and on white, each next to the wordmark.
3. Read the sheet. Reject what fails, and say why in one line.
   - The mark must read as the name at 40 px. A mascot needs the one feature
     that names it (a beak, a fin, a horn), not only its outline.
   - The mark must stay clean on the film's canvas. A mid-tone on a dark canvas
     turns muddy.
   - A rounded tile silhouette works as a favicon.
4. Refine the winner once or twice on a second sheet. Save it as
   `assets/brand/mark.svg`.

## Palette

The film's palette is in `DIRECTION.json`: the brand colours from the repo
plus at least three invented for the film's world. Map them to the theme
tokens (`assets/theme.css` in app-launch-video, `theme.ts` in motion-reel):

| Token | Role |
|---|---|
| `--canvas` | the film background: `palette.canvas` |
| `--accent` | labels, highlights, the tagline: the brand colour that reads best on the canvas |
| `--light` | lines, edges, the hero motion's glow: an invented colour |
| `--ink`, `--muted` | text on the canvas, and a quieter text colour that matches it |
| `--app-*` | the recreated app's own surfaces: take them from the app's theme, unchanged |

Keep semantic colours: green for ok, amber for warn, red for bad. For type
pairing and colour method, see the `hyperframes-creative` skill.

## Sweeping a palette change

Never recolour by hand. Write a map from old to new values, covering hex (3 and
6 digit) and `rgb()`/`rgba()` triples. Run it over every composition and
`index.html`, then run it again with `--check` so it lists anything left.
Then remap primary controls by context (`background:` and `border-color:` of
the old primary dark), because the same dark grey is also a text colour. Last,
snapshot every scene once. A missed colour in one dialog reads as a bug.

## Fonts

A rebrand may change the font. Vendor it: in app-launch-video, `python3
tools/vendor_fonts.py "<UI family>:400,500,600,700,800" "<mono family>:400,500,600,700"`;
in motion-reel, put the font files in `public/fonts/` and list them in `fonts.ts`.
Name the families only in `--ui` and `--mono`. After a font change,
re-snapshot every layout that depends on text width: wordmarks, dialog widths
and wide tables.

## Rebrand checklist

- Copy the project. The delivered film must stay reproducible from its own
  folder.
- Grep for the old name and the old logo files everywhere: compositions,
  `index.html` title, `meta.json`, `package.json`, the voiceover script and the
  credits.
- Redesign the mark's entrance for the new mark's shape.
- The tagline is the client's copy. When it must change, offer 3 or 4 short
  options with one recommended, and let the client pick.
