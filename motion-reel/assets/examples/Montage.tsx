import { AbsoluteFill } from "remotion";
import FEATURES from "../features.json";
import { C, MONO, UI } from "../theme";
import { inn, lerp, out, ramp } from "../timeline";

// Beats 44-56 (local 0-12). Every feature, cut faster and faster (1, 1/2, 1/4, 1/8 beat), then the last
// card collapses into the orange dot that the logo grows from.
export const TILE = { cx: 960, cy: 559.25, w: 275, h: 247.5, r: 82.5 };
export const DOT = 30;

const NAMES = Object.keys(FEATURES as Record<string, string>);
const DURS = [1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, ...Array(8).fill(0.25), ...Array(8).fill(0.125)];
const STARTS = DURS.reduce<number[]>((acc, d, i) => [...acc, i === 0 ? 0 : acc[i - 1] + DURS[i - 1]], []);
export const MONTAGE_CUTS = STARTS; // local beats of every cut, for the cue list
const END = STARTS[STARTS.length - 1] + DURS[DURS.length - 1];
// The first card is the colour of the box the Abstraction section zooms into.
const BGS = ["#0f3438", C.amber, C.deep, C.cream, C.teal, C.ink, "#e8842a", C.paper];
const light = (bg: string) => bg === C.amber || bg === C.cream || bg === C.paper || bg === "#e8842a";

export const Montage: React.FC<{ b: number }> = ({ b }) => {
  const k = Math.min(NAMES.length - 1, Math.max(0, STARTS.findIndex((s, i) => b >= s && b < s + DURS[i])));
  const idx = b >= END ? NAMES.length - 1 : k;
  const name = NAMES[idx];
  const bg = BGS[idx % BGS.length];
  const local = (b - STARTS[idx]) / DURS[idx];
  const punch = lerp(1.1, 1, ramp(local, 0, 0.6, out));
  const collapse = ramp(b, END, END + 0.9, inn);
  const dotPulse = b > END + 0.9 ? 1 + 0.25 * Math.exp(-((b - (END + 1.2)) ** 2) * 30) : 1;
  const ink = light(bg) ? C.ink : C.paper;
  const icon = (FEATURES as Record<string, string>)[name];
  // The collapsing card: a full-frame rectangle that shrinks into the dot and turns orange.
  const w = lerp(1920, DOT, collapse), h = lerp(1080, DOT, collapse);
  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden", fontFamily: UI }}>
      <div style={{ position: "absolute", left: lerp(0, TILE.cx - DOT / 2, collapse), top: lerp(0, TILE.cy - DOT / 2, collapse), width: w, height: h,
        borderRadius: lerp(0, DOT / 2, collapse), background: collapse > 0.6 ? `color-mix(in srgb, ${bg} ${(1 - ramp(collapse, 0.6, 1)) * 100}%, #e8842a)` : bg,
        transform: `scale(${dotPulse})`, boxShadow: collapse > 0.8 ? "0 0 40px 10px rgba(246,162,58,0.45)" : undefined, overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 960 - 900, top: 0, width: 1800, height: 1080, display: "flex", flexDirection: "column", alignItems: "center",
          justifyContent: "center", gap: 40, transform: `scale(${punch * (1 - collapse)})`, opacity: 1 - ramp(collapse, 0, 0.4), color: ink }}>
          <svg width={220} height={220} viewBox="0 0 24 24" fill="none" stroke={light(bg) ? C.deep : C.amber} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round"
            dangerouslySetInnerHTML={{ __html: icon }} />
          <div style={{ fontSize: 150, fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1, whiteSpace: "nowrap" }}>{name}</div>
        </div>
        <div style={{ position: "absolute", left: 60, top: 50, fontFamily: MONO, fontSize: 28, letterSpacing: "0.12em", color: ink, opacity: 0.55 * (1 - collapse) }}>
          {String(idx + 1).padStart(2, "0")} / {NAMES.length}
        </div>
      </div>
    </AbsoluteFill>
  );
};
