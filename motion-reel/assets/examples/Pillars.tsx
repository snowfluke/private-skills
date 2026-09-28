import { AbsoluteFill } from "remotion";
import { C, MONO, UI } from "../theme";
import { inn, lerp, out, ramp } from "../timeline";

// Beats 24-44 (local 0-20): the five pillars, four beats each. Each one hands its last shape to the next.
const word: React.CSSProperties = { position: "absolute", left: 0, right: 0, textAlign: "center", fontFamily: UI, lineHeight: 1, whiteSpace: "nowrap" };
const smooth = (t: number) => 0.5 - Math.cos(t * Math.PI) / 2;

const GANTT: [string, number, number][] = [["SFTP Server", 0.05, 0.14], ["Table Converter", 0.12, 0.26], ["Key Matcher", 0.24, 0.62], ["Flag Rows", 0.6, 0.74], ["Write File", 0.72, 1]];

const Speed: React.FC<{ b: number }> = ({ b }) => {
  const p = ramp(b, 0, 0.45, out);
  const run = ramp(b, 0.7, 3.0, (t) => t);
  const wipe = ramp(b, 3.25, 4, inn);
  return (
    <AbsoluteFill style={{ background: C.amber, overflow: "hidden" }}>
      {Array.from({ length: 14 }, (_, i) => {
        const y = 110 + ((i * 97) % 860);
        const len = 300 + ((i * 173) % 700);
        const x = lerp(-900, 2600, ramp(b, i * 0.05, 0.6 + i * 0.05, (t) => t));
        return <div key={i} style={{ position: "absolute", left: x - len, top: y, width: len, height: 7, borderRadius: 4, background: C.ink, opacity: 0.28 }} />;
      })}
      <div style={{ ...word, top: 170, fontSize: 250, fontWeight: 800, letterSpacing: "-0.03em", color: C.ink,
        transform: `translateX(${(1 - p) * -1500}px) skewX(${(1 - p) * -30 - 8 * (1 - ramp(b, 0.4, 1.4))}deg) scaleX(${lerp(1.5, 1, ramp(b, 0.2, 1.2, out))})`,
        filter: `blur(${(1 - p) * 22}px)` }}>SPEED</div>
      <div style={{ position: "absolute", left: 360, top: 520, width: 1200 }}>
        {GANTT.map(([label, a, z], i) => {
          const g = ramp(run, a, z, (t) => t);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", height: 70, opacity: ramp(b, 0.5 + i * 0.08, 0.8 + i * 0.08) }}>
              <span style={{ width: 330, fontFamily: MONO, fontSize: 30, color: C.ink }}>{label}</span>
              <div style={{ position: "relative", flex: 1, height: 30 }}>
                <div style={{ position: "absolute", left: `${a * 100}%`, width: `${(z - a) * g * 100}%`, height: 30, borderRadius: 8, background: C.deep }} />
              </div>
            </div>
          );
        })}
        <div style={{ textAlign: "right", fontFamily: MONO, fontSize: 64, fontWeight: 700, color: C.ink, marginTop: 14 }}>
          {Math.floor((run * 84) / 60)}m {String(Math.round(run * 84) % 60).padStart(2, "0")}s
        </div>
      </div>
      {/* Hand-off: the last streak widens into the FLEXIBILITY background. */}
      <div style={{ position: "absolute", top: 0, bottom: 0, left: -200, width: wipe * 2400, background: C.deep, transform: "skewX(-14deg)", transformOrigin: "0 0" }} />
    </AbsoluteFill>
  );
};

const Flexibility: React.FC<{ b: number }> = ({ b }) => {
  const drag = Math.sin(Math.max(0, b - 0.6) * Math.PI) * Math.min(1, Math.max(0, b - 0.6) * 2) * (1 - ramp(b, 3.3, 3.5));
  const A = { x: 560, y: 860 }, Z = { x: 1360, y: 860 };
  const mid = { x: 960, y: 860 + drag * -170 };
  const cursorIn = ramp(b, 0.3, 0.6, out);
  const click = ramp(b, 3.5, 4.0, inn);
  return (
    <AbsoluteFill style={{ background: C.deep, overflow: "hidden" }}>
      <div style={{ ...word, top: 280, fontSize: 210, color: C.paper }}>
        {"FLEXIBILITY".split("").map((ch, i) => {
          const w = Math.sin(b * Math.PI * 2 - i * 0.55) * Math.min(1, b * 3) * (1 - ramp(b, 3.4, 3.9));
          return (
            <span key={i} style={{ display: "inline-block", transformOrigin: "50% 100%", fontWeight: Math.round(lerp(300, 800, (w + 1) / 2)),
              transform: `translateY(${-Math.max(0, w) * 70}px) scale(${1 - w * 0.2}, ${1 + w * 0.28})` }}>{ch}</span>
          );
        })}
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0 }}>
        <path d={`M${A.x},${A.y} Q${mid.x},${mid.y * 2 - A.y} ${Z.x},${Z.y}`} fill="none" stroke={C.flow} strokeWidth={7} strokeLinecap="round" />
      </svg>
      {[A, Z].map((n, k) => (
        <div key={k} style={{ position: "absolute", left: n.x - (k ? 0 : 260), top: n.y - 44, width: 260, height: 88, borderRadius: 16, background: "#fff",
          border: `3px solid ${k ? "#db2777" : "#e0661a"}`, display: "grid", placeItems: "center", fontFamily: UI, fontSize: 30, fontWeight: 700, color: C.text }}>
          {k ? "Key Matcher" : "IT Table"}
        </div>
      ))}
      <svg width={56} height={56} viewBox="0 0 24 24" style={{ position: "absolute", left: mid.x - 6, top: mid.y - 6, opacity: cursorIn, transform: `scale(${1 - ramp(b, 3.45, 3.55) * 0.15})` }}>
        <path d="M4 2l15 11-6.5 1.2L9 21z" fill="#fff" stroke={C.ink} strokeWidth={1.5} strokeLinejoin="round" />
      </svg>
      {/* Hand-off: the click ring grows into the INSPECTION background. */}
      <div style={{ position: "absolute", left: mid.x - 1, top: mid.y - 1, width: 2, height: 2, borderRadius: "50%", background: C.cream,
        transform: `scale(${click * 2400})`, opacity: click > 0 ? 1 : 0 }} />
    </AbsoluteFill>
  );
};

const Inspection: React.FC<{ b: number }> = ({ b }) => {
  const lx = lerp(330, 1590, ramp(b, 0.1, 2.9, smooth));
  const ly = 470;
  const grow = ramp(b, 3.0, 4.0, inn);
  const r = lerp(180, 2300, grow);
  const lens = `circle(${r}px at ${lx}px ${ly}px)`;
  const inside = lerp(0, 1, grow);
  return (
    <AbsoluteFill style={{ background: C.cream }}>
      <div style={{ ...word, top: 370, fontSize: 200, fontWeight: 200, color: C.deep }}>INSPECTION</div>
      <AbsoluteFill style={{ clipPath: lens, background: inside < 1 ? `color-mix(in srgb, ${C.deep} ${(1 - inside) * 100}%, ${C.teal})` : C.teal }}>
        <div style={{ ...word, top: 370, fontSize: 200, fontWeight: 800, color: C.flow, transform: "scale(1.25)", transformOrigin: `${lx}px 100px`, opacity: 1 - grow }}>INSPECTION</div>
        <div style={{ ...word, top: 590, fontFamily: MONO, fontSize: 40, color: C.paper, opacity: 1 - grow }}>[Key Matcher] Matched 21,984 · Unmatched 20</div>
      </AbsoluteFill>
      <div style={{ position: "absolute", left: lx - r - 12, top: ly - r - 12, width: (r + 12) * 2, height: (r + 12) * 2, borderRadius: "50%",
        border: `14px solid ${C.deep}`, opacity: 1 - grow }} />
      <div style={{ position: "absolute", left: lx + 128, top: ly + 128, width: 170, height: 38, borderRadius: 19, background: C.deep, transform: "rotate(45deg)",
        transformOrigin: "0 50%", opacity: 1 - grow }} />
    </AbsoluteFill>
  );
};

const Iteration: React.FC<{ b: number }> = ({ b }) => {
  const collapse = ramp(b, 3.0, 3.6, inn);
  const dusk = ramp(b, 3.3, 4.0);
  // The final word falls out of frame; VISUAL falls in from above, so the motion runs straight down.
  const fall = ramp(b, 3.55, 4.0, inn);
  return (
    <AbsoluteFill style={{ background: `color-mix(in srgb, ${C.teal} ${(1 - dusk) * 100}%, ${C.ink})` }}>
      {Array.from({ length: 8 }, (_, k) => {
        const on = ramp(b, k * 0.12, k * 0.12 + 0.22, out);
        const last = k === 7;
        const top = lerp(400 + (7 - k) * -40, 400, collapse);
        return (
          <div key={k} style={{ position: "absolute", left: 0, right: 0, top: top + (last ? fall * 760 : 0), opacity: last ? on : on * (1 - collapse),
            filter: last && fall > 0 ? `blur(${fall * 10}px)` : undefined }}>
            <div style={{ ...word, position: "relative", fontSize: 200, fontWeight: 800, color: last ? "#fff" : "transparent",
              WebkitTextStroke: last ? undefined : `3px rgba(255,255,255,${0.3 + k * 0.08})`, transform: `scale(${lerp(0.7, 1, k / 7)})` }}>ITERATION</div>
            <div style={{ position: "absolute", left: 150, top: 70, fontFamily: MONO, fontSize: 30, color: last ? C.amber : "rgba(255,255,255,0.55)" }}>v{k + 1}</div>
          </div>
        );
      })}
      <svg width={110} height={110} viewBox="0 0 24 24" fill="none" stroke={C.amber} strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round"
        style={{ position: "absolute", left: 1640, top: 450, transform: `rotate(${b * 180}deg)`, opacity: ramp(b, 0.6, 1) * (1 - dusk) }}>
        <path d="M21 12a9 9 0 1 1-2.64-6.36" /><path d="M21 3v6h-6" />
      </svg>
    </AbsoluteFill>
  );
};

const BOX = 104;
const Line: React.FC<{ text: string; top: number; b: number; from: number }> = ({ text, top, b, from }) => {
  const x0 = 960 - (text.length * BOX) / 2;
  const morph = ramp(b, 1.6, 2.2);
  const link = ramp(b, 1.9, 2.5, out);
  const flow = 0;
  return (
    <>
      {text.split("").map((ch, i) => {
        const p = ramp(b, i * 0.03, i * 0.03 + 0.3, out);
        const bx = x0 + i * BOX, by = top, bw = BOX, bh = 170;
        return (
          <div key={i} style={{ position: "absolute", left: bx, top: by, width: bw, height: bh, transform: `translateY(${(1 - p) * from}px)`, opacity: p }}>
            <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", fontFamily: UI, fontSize: 170, fontWeight: 800, color: C.paper,
              opacity: 1 - morph, transform: `scale(${1 - morph * 0.6})` }}>{ch}</div>
            <div style={{ position: "absolute", left: lerp(10, 0, flow), right: lerp(10, 0, flow), top: lerp(lerp(20, 50, morph), 0, flow), bottom: lerp(lerp(20, 50, morph), 0, flow),
              borderRadius: 14, border: `${lerp(5, 2, flow)}px solid ${C.flow}`, background: `rgba(45,212,191,${lerp(0.12, 0.08, flow)})`, opacity: morph,
              transform: `scale(${lerp(1.4, 1, morph)})` }} />
            {i < text.length - 1 && (
              <div style={{ position: "absolute", left: BOX - 10, top: 83, width: 20 * link, height: 5, background: C.flow, opacity: 1 - flow }} />
            )}
          </div>
        );
      })}
    </>
  );
};

// The camera dives into the centre box of ABSTRACTION (at 960, 555); its fill becomes the first montage card.
const Abstraction: React.FC<{ b: number }> = ({ b }) => {
  const dive = ramp(b, 2.9, 4.0, inn);
  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden" }}>
      <AbsoluteFill style={{ transformOrigin: "960px 555px", transform: `scale(${lerp(1, 30, dive)})` }}>
        <Line text="VISUAL" top={250} b={b} from={-700} />
        <Line text="ABSTRACTION" top={470} b={b - 0.25} from={700} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Pillars: React.FC<{ b: number }> = ({ b }) => {
  if (b < 4) return <Speed b={b} />;
  if (b < 8) return <Flexibility b={b - 4} />;
  if (b < 12) return <Inspection b={b - 8} />;
  if (b < 16) return <Iteration b={b - 12} />;
  return <Abstraction b={b - 16} />;
};
