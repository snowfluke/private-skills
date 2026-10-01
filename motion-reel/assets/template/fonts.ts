import { continueRender, delayRender, staticFile } from "remotion";

// Vendored fonts; every frame waits for them so no frame renders in a fallback face.
// Fill FACES with the product's UI font and the film's display face from DIRECTION.json:
// [family, file in public/fonts/, weight range, style].
const FACES: [string, string, string, string][] = [];

export const loadFonts = (): void => {
  if (typeof document === "undefined") return;
  const handle = delayRender("fonts");
  Promise.all(
    FACES.map(([family, file, weight, style]) =>
      new FontFace(family, `url(${staticFile(`fonts/${file}`)})`, { weight, style }).load().then((f) => document.fonts.add(f)),
    ),
  )
    .then(() => continueRender(handle))
    .catch((err) => {
      console.error("font load failed", err);
      continueRender(handle);
    });
};
