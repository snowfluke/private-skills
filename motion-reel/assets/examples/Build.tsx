import { AbsoluteFill } from "remotion";
import ICONS from "../icons.json";
import { C, MONO, UI } from "../theme";
import { bez, inn, lerp, out, ramp } from "../timeline";

// Beats 8-16 (local 0-8). Nodes pop where the flood's orbs landed; the camera then dives into Key Matcher.
type Group = { tint: string; fg: string };
const INPUT: Group = { tint: "#d1fae5", fg: "#059669" };
const TABLE: Group = { tint: "#ffe8d2", fg: "#e0661a" };
const MATCH: Group = { tint: "#fce7f3", fg: "#db2777" };
const OUTPUT: Group = { tint: "#ccfbf1", fg: "#0d9488" };

export const NW = 330, NH = 116;
type N = { label: string; sub: string; g: Group; x: number; y: number; at: number };
const NODES: N[] = [
  { label: "SFTP Server", sub: "sftp.partner.co.id", g: INPUT, x: 220, y: 300, at: 0 },
  { label: "Email Inbox", sub: "imap.partner.co.id", g: INPUT, x: 220, y: 660, at: 0.1 },
  { label: "Table Converter", sub: "IT Table", g: TABLE, x: 700, y: 300, at: 1.5 },
  { label: "Table Converter", sub: "RK Table", g: TABLE, x: 700, y: 660, at: 1.6 },
  { label: "Key Matcher", sub: "IT ⇄ RK", g: MATCH, x: 1180, y: 480, at: 3 },
  { label: "Flag Rows", sub: "first rule wins", g: TABLE, x: 1660, y: 480, at: 4 },
  { label: "Write File", sub: "Rekon Cash In BCA.xlsx", g: OUTPUT, x: 2140, y: 480, at: 5 },
];
const EDGES: [number, number, number][] = [[0, 2, 1.2], [1, 3, 1.3], [2, 4, 2.6], [3, 4, 2.7], [4, 5, 3.7], [5, 6, 4.7]];
export const KM = { x: NODES[4].x + NW / 2, y: NODES[4].y + NH / 2 };

const icon = (label: string) => (ICONS as Record<string, string>)[label] ?? "";

export const Build: React.FC<{ b: number }> = ({ b }) => {
  const pan = ramp(b, 2, 5.2, (t) => 0.5 - Math.cos(t * Math.PI) / 2);
  const dive = ramp(b, 6, 8, inn);
  const cx = lerp(lerp(960, 1345, pan), KM.x, ramp(b, 5.6, 6.6));
  const cy = lerp(540, KM.y, ramp(b, 5.6, 6.6));
  const z = lerp(1.25, 0.8, pan) * lerp(1, 14, dive);
  const labelOut = 1 - ramp(b, 6.2, 7.0);
  return (
    <AbsoluteFill style={{ background: C.ink, overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 960, top: 540, width: 0, height: 0, transform: `scale(${z}) translate(${-cx}px, ${-cy}px)` }}>
        <div style={{ position: "absolute", left: -1400, top: -1200, width: 5200, height: 3400,
          backgroundImage: "radial-gradient(rgba(167,186,185,0.22) 2px, transparent 2px)", backgroundSize: "36px 36px" }} />
        <svg width={2600} height={1200} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
          {EDGES.map(([a, zI, at], i) => {
            const A = NODES[a], Z = NODES[zI];
            const x0 = A.x + NW, y0 = A.y + NH / 2, x1 = Z.x, y1 = Z.y + NH / 2;
            const d = `M${x0},${y0} C${(x0 + x1) / 2},${y0} ${(x0 + x1) / 2},${y1} ${x1},${y1}`;
            const draw = ramp(b, at, at + 0.5, out);
            const pk = b > at + 0.5 ? (b - at - 0.5) % 1 : -1;
            const p = pk >= 0 ? bez(x0, y0, x1, y1, pk) : null;
            return (
              <g key={i}>
                <path d={d} fill="none" stroke={C.flow} strokeWidth={5} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} strokeLinecap="round" />
                {p && <circle cx={p.x} cy={p.y} r={9} fill={C.amber} style={{ filter: "drop-shadow(0 0 8px rgba(246,162,58,0.9))" }} />}
              </g>
            );
          })}
        </svg>
        {NODES.map((n, i) => {
          const s = ramp(b, n.at, n.at + 0.45, (t) => 1 + 2.7 * (t - 1) ** 3 + 1.7 * (t - 1) ** 2);
          const live = b > 5.5 + i * 0.15;
          return (
            <div key={i} style={{ position: "absolute", left: n.x, top: n.y, width: NW, height: NH, borderRadius: 18, background: "#fff",
              border: `3px solid ${live ? C.ok : n.g.fg}`, boxShadow: "0 16px 40px rgba(0,0,0,0.35)", transform: `scale(${Math.max(0, s)})`,
              display: "flex", alignItems: "center", gap: 18, padding: "0 22px", fontFamily: UI }}>
              <div style={{ width: 62, height: 62, borderRadius: 14, background: n.g.tint, display: "grid", placeItems: "center", flex: "0 0 auto", opacity: i === 4 ? labelOut : 1 }}>
                <svg width={34} height={34} viewBox="0 0 24 24" fill="none" stroke={n.g.fg} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"
                  dangerouslySetInnerHTML={{ __html: icon(n.label) }} />
              </div>
              <div style={{ opacity: i === 4 ? labelOut : 1, minWidth: 0 }}>
                <div style={{ fontSize: 28, fontWeight: 700, color: C.text, whiteSpace: "nowrap" }}>{n.label}</div>
                <div style={{ fontFamily: MONO, fontSize: 17, color: "#6b635c", whiteSpace: "nowrap" }}>{n.sub}</div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
