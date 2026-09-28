import { continueRender, delayRender, staticFile } from "remotion";

// Vendored variable fonts; every frame waits for them so no frame renders in a fallback face.
const FACES: [string, string, string, string][] = [
  ["Plus Jakarta Sans", "PlusJakartaSans-400.woff2", "200 800", "normal"],
  ["Plus Jakarta Sans", "PlusJakartaSans-300i.woff2", "200 800", "italic"],
  ["JetBrains Mono", "JetBrainsMono-400.woff2", "100 800", "normal"],
];

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
