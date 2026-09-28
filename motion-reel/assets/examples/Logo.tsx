import { AbsoluteFill } from "remotion";
import { Mark } from "../Mark";
import { C, UI } from "../theme";
import { inn, lerp, out, ramp } from "../timeline";
import { DOT, TILE } from "./Montage";

// Beats 56-72 (local 0-16). The mark builds from the calendar's tile, locks up with the wordmark and the
// tagline, returns to the centre, and squashes into the teal line that opens the reel at beat 0.
const SIZE = 330;
const back = (t: number) => 1 + 2.7 * (t - 1) ** 3 + 1.7 * (t - 1) ** 2;

export const Logo: React.FC<{ b: number }> = ({ b }) => {
  const parts = {
    tile: lerp(DOT / TILE.w, 1, ramp(b, 0, 0.42, back)),
    ears: ramp(b, 0.4, 0.72, back),
    muzzle: ramp(b, 0.8, 1.05, back),
    eyes: ramp(b, 1.05, 1.25, out),
    nose: ramp(b, 1.35, 1.6, back),
    teeth: ramp(b, 1.8, 2.05, back),
    blink: Math.max(0, 1 - Math.abs(b - 8.6) * 12),
  };
  const toLock = ramp(b, 2.9, 3.7, (t) => 0.5 - Math.cos(t * Math.PI) / 2);
  const toCentre = ramp(b, 10.2, 11.0, (t) => 0.5 - Math.cos(t * Math.PI) / 2);
  const lock = toLock * (1 - toCentre);
  const hit = Math.max(0, 1 - Math.abs(b - 2.05) * 8);
  const bob = b > 2.2 && b < 10 ? Math.sin((b - 2.2) * Math.PI) * 6 : 0;
  // Mark: centred (960, 540) when lock = 0; left of the wordmark when lock = 1.
  const scale = lerp(1, 0.78, lock) * (1 + hit * 0.07);
  const mx = lerp(960, 452, lock), my = lerp(540, 470, lock) + bob;
  // The squash: the face goes, then the tile stretches into the loop line.
  const faceOut = ramp(b, 11.8, 12.4, inn);
  const squash = ramp(b, 12.3, 15.4, (t) => 1 - (1 - t) ** 3);
  const line = squash > 0;
  const words = ramp(b, 3.1, 3.7, out) * (1 - ramp(b, 9.8, 10.3, inn));
  const tag1 = ramp(b, 4.9, 5.3, out) * (1 - ramp(b, 9.6, 10.1, inn));
  const tag2 = ramp(b, 5.9, 6.3, out) * (1 - ramp(b, 9.6, 10.1, inn));
  const off = { tile: line ? 0 : parts.tile, ears: parts.ears * (1 - faceOut), muzzle: parts.muzzle * (1 - faceOut), eyes: parts.eyes * (1 - faceOut),
    nose: parts.nose * (1 - faceOut), teeth: parts.teeth * (1 - faceOut), blink: parts.blink };
  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden", fontFamily: UI }}>
      <div style={{ position: "absolute", left: 960, top: 540, width: 1400, height: 1400, marginLeft: -700, marginTop: -700, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(246,162,58,0.20) 0%, rgba(246,162,58,0) 60%)", opacity: ramp(b, 1.8, 2.6) * (1 - faceOut) }} />
      <div style={{ position: "absolute", left: mx - SIZE / 2, top: my - SIZE / 2, transform: `scale(${scale})`, transformOrigin: "50% 50%" }}>
        <Mark size={SIZE} parts={off} id="logo" />
      </div>
      {line && (
        <div style={{ position: "absolute", left: lerp(TILE.cx - TILE.w / 2, 0, squash), width: lerp(TILE.w, 1920, squash),
          top: lerp(TILE.cy - TILE.h / 2, 538, squash), height: lerp(TILE.h, 4, squash), borderRadius: lerp(TILE.r, 2, squash),
          background: `color-mix(in srgb, #e8842a ${(1 - ramp(squash, 0.55, 0.9)) * 100}%, ${C.flow})`,
          boxShadow: `0 0 ${lerp(0, 24, squash)}px ${lerp(0, 6, squash)}px rgba(45,212,191,${0.55 * squash})` }} />
      )}
      <div style={{ position: "absolute", left: 640, top: 360, display: "flex", overflow: "hidden", paddingBottom: 30 }}>
        {"Beaverflow".split("").map((ch, i) => (
          <span key={i} style={{ display: "inline-block", fontSize: 200, fontWeight: 800, letterSpacing: "-0.045em", lineHeight: 1,
            color: i >= 6 ? C.amber : C.paper, transform: `translateY(${(1 - ramp(b, 3.1 + i * 0.04, 3.6 + i * 0.04, out)) * 110}%)`, opacity: words }}>{ch}</span>
        ))}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 690, display: "flex", justifyContent: "center", gap: 28, fontSize: 72, fontWeight: 600, letterSpacing: "-0.015em" }}>
        <span style={{ color: C.paper, opacity: tag1, transform: `translateY(${(1 - tag1) * 30}px)` }}>Build the flow.</span>
        <span style={{ color: C.amber, opacity: tag2, transform: `translateY(${(1 - tag2) * 30}px)` }}>Close the books.</span>
      </div>
    </AbsoluteFill>
  );
};
