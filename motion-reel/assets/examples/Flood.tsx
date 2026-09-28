import { AbsoluteFill } from "remotion";
import { C, MONO, UI } from "../theme";
import { hash, inn, lerp, out, ramp } from "../timeline";

// Beats 0-8. Opens from the loop line; ends as two orbs where the source nodes will pop.
// Where the source nodes first appear on screen (Build starts at zoom 1.25 around the frame centre).
export const ORB_A = { x: 960 + (385 - 960) * 1.25, y: 540 + (358 - 540) * 1.25 };
export const ORB_B = { x: 960 + (385 - 960) * 1.25, y: 540 + (718 - 540) * 1.25 };

const ROW_H = 46;
const ROWS = 30;
const row = (side: number, i: number) => {
  const amt = Math.round(40000 + hash(side * 97 + i) * 9_000_000);
  const diff = hash(side * 31 + i * 7) < 0.16;
  return { ref: `TRX-0522-${String(401 + i).padStart(5, "0")}`, amt: amt.toLocaleString("en-US"), diff, dv: diff ? `-${Math.round(hash(i + side) * 90000).toLocaleString("en-US")}` : "0" };
};

const Column: React.FC<{ side: 0 | 1; b: number; x: number; label: string }> = ({ side, b, x, label }) => {
  const speed = 210 * (side === 0 ? -1 : 1);
  const offset = (((b * speed) % (ROWS * ROW_H)) + ROWS * ROW_H) % (ROWS * ROW_H);
  const blink = 0.35 + 0.65 * Math.abs(Math.sin(b * Math.PI * 2));
  return (
    <div style={{ position: "absolute", left: x, top: 0, width: 780, height: 1080, overflow: "hidden" }}>
      {Array.from({ length: ROWS }, (_, i) => {
        const r = row(side, i);
        const y = ((i * ROW_H + offset) % (ROWS * ROW_H)) - ROW_H;
        return (
          <div key={i} style={{ position: "absolute", left: 0, right: 0, top: y, height: ROW_H - 6, display: "flex", alignItems: "center", gap: 28,
            padding: "0 18px", borderRadius: 8, background: "rgba(167,186,185,0.07)", fontFamily: MONO, fontSize: 22, color: "rgba(246,241,231,0.55)" }}>
            <span style={{ width: 250 }}>{r.ref}</span>
            <span style={{ width: 200, textAlign: "right" }}>{r.amt}</span>
            <span style={{ marginLeft: "auto", color: r.diff ? C.bad : "rgba(246,241,231,0.35)", opacity: r.diff ? blink : 1 }}>{r.dv}</span>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 18, top: 24, fontFamily: MONO, fontSize: 22, letterSpacing: "0.18em", color: C.flow }}>{label}</div>
    </div>
  );
};

export const Flood: React.FC<{ b: number }> = ({ b }) => {
  const open = ramp(b, 0.05, 0.7, out);
  const suck = ramp(b, 5.9, 7.1, inn);
  const fly = ramp(b, 7.0, 8.0, out);
  const line = 1 - ramp(b, 0, 0.45, out);
  const t1 = ramp(b, 1.4, 1.9, out), t2 = ramp(b, 2.9, 3.35, out), tOut = ramp(b, 5.4, 5.9, inn);
  const colL = { cx: 510, cy: 540 }, colR = { cx: 1410, cy: 540 };
  const orb = (from: { cx: number; cy: number }, to: { x: number; y: number }) => ({ x: lerp(from.cx, to.x, fly), y: lerp(from.cy, to.y, fly) });
  const oA = orb(colL, ORB_A), oB = orb(colR, ORB_B);
  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, clipPath: `inset(${(1 - open) * 50}% 0 ${(1 - open) * 50}% 0)`, opacity: 1 - suck }}>
        <div style={{ position: "absolute", inset: 0, transformOrigin: `${colL.cx}px ${colL.cy}px`, transform: `scale(${1 - suck * 0.98})` }}>
          <Column side={0} b={b} x={120} label="INTERNAL DATA" />
        </div>
        <div style={{ position: "absolute", inset: 0, transformOrigin: `${colR.cx}px ${colR.cy}px`, transform: `scale(${1 - suck * 0.98})` }}>
          <Column side={1} b={b} x={1020} label="REKENING KORAN" />
        </div>
      </div>
      {/* The loop line: it opens into the two streams. */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 538, height: 4, background: C.flow, boxShadow: `0 0 24px 6px rgba(45,212,191,0.55)`,
        opacity: line, transform: `scaleY(${1 + (1 - line) * 30})` }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 370, height: 340, background: "rgba(11,30,38,0.86)", opacity: Math.max(t1 - tOut, 0),
        backdropFilter: "blur(2px)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 392, textAlign: "center", fontFamily: UI, fontWeight: 800, fontSize: 176, letterSpacing: "-0.04em",
        color: C.paper, lineHeight: 1, opacity: t1 * (1 - tOut), transform: `scale(${lerp(1.35, 1, t1)}) translateY(${tOut * -40}px)`, filter: `blur(${(1 - t1) * 14}px)` }}>
        1,000,000 rows
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 580, textAlign: "center", fontFamily: UI, fontStyle: "italic", fontWeight: 300, fontSize: 112,
        color: C.amber, lineHeight: 1, opacity: t2 * (1 - tOut), transform: `translateY(${(1 - t2) * 40 - tOut * 40}px)` }}>
        every single day.
      </div>
      {[oA, oB].map((o, k) => (
        <div key={k} style={{ position: "absolute", left: o.x - 26, top: o.y - 26, width: 52, height: 52, borderRadius: "50%", background: C.flow,
          boxShadow: "0 0 40px 14px rgba(45,212,191,0.6)", opacity: suck, transform: `scale(${lerp(0.4, 1, suck) + fly * 0.4})` }} />
      ))}
    </AbsoluteFill>
  );
};
