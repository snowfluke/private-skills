// Measure every scene's tween timing in headless Chrome and report its end hold: the idle time between
// the last on-screen action and the exit. Use it before "cut the holds" or "tighten the pacing" edits.
//
//   node tools/hold_probe.mjs            # table of scene, duration, last action, exit, hold
//   node tools/hold_probe.mjs --json     # also writes hold-probe.json with every tween
//
// Needs puppeteer-core and a headless Chrome. It finds them in the npx cache and the Playwright cache;
// PUPPETEER_CORE and CHROME_BIN override. It serves the project on 127.0.0.1:8765 while it runs.
// Speed-wrapped scenes are unwrapped, so every time is in film seconds.
import { createRequire } from "module";
import { spawn, execSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";

const ROOT = path.dirname(path.dirname(new URL(import.meta.url).pathname));
setTimeout(() => { console.error("hold_probe: timeout"); process.exit(2); }, 180000);

const find = (cmd) => { try { return execSync(`${cmd} || true`, { encoding: "utf8", shell: "/bin/sh" }).split("\n").filter(Boolean)[0]; } catch { return ""; } };
const pptr = process.env.PUPPETEER_CORE || find(`ls -d ${os.homedir()}/.npm/_npx/*/node_modules/puppeteer-core 2>/dev/null`);
const chrome = process.env.CHROME_BIN || find(`ls ${os.homedir()}/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell ${os.homedir()}/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell 2>/dev/null`);
if (!pptr || !chrome) { console.error(`hold_probe: need puppeteer-core (${pptr || "missing"}) and chrome-headless-shell (${chrome || "missing"})`); process.exit(1); }
const puppeteer = createRequire(import.meta.url)(pptr);

const scenes = JSON.parse(fs.readFileSync(path.join(ROOT, "timeline.json"))).scenes;
const heads = [...fs.readFileSync(path.join(ROOT, "index.html"), "utf8").matchAll(/<(script src|link rel="stylesheet" href)="([^"]+)"/g)]
  .map(([, kind, src]) => kind.startsWith("script") ? `<script src="/${src}"></script>` : `<link rel="stylesheet" href="/${src}">`).join("");
const harness = `<!doctype html><html><head><meta charset="utf-8">${heads}<style>*{margin:0;padding:0;box-sizing:border-box}body{width:1920px;height:1080px;overflow:hidden}.host{position:absolute;inset:0}</style></head><body><script>
window.__timelines = {};
window.probe = async (id, src) => {
  const doc = new DOMParser().parseFromString(await (await fetch("/compositions/" + src)).text(), "text/html");
  const frag = doc.querySelector("template").content.cloneNode(true);
  const scripts = [...frag.querySelectorAll("script")]; scripts.forEach((s) => s.remove());
  const host = document.createElement("div"); host.className = "host"; document.body.appendChild(host); host.appendChild(frag);
  for (const s of scripts) { const n = document.createElement("script"); n.textContent = s.textContent; host.appendChild(n); }
  let tl = window.__timelines[id], speed = 1;
  const kids = tl.getChildren(false, true, true);
  if (kids.length === 1 && kids[0].targets && kids[0].targets()[0] instanceof gsap.core.Timeline) { const inner = kids[0].targets()[0]; speed = inner.duration() / tl.duration(); tl = inner; }
  const out = [];
  const walk = (t, off) => { for (const c of t.getChildren(false, true, true)) {
    const st = off + c.startTime();
    if (c instanceof gsap.core.Timeline) { walk(c, st); continue; }
    const tg = c.targets().map((x) => x.id ? "#" + x.id : (x.nodeType ? x.tagName.toLowerCase() : "proxy")).slice(0, 2).join(",");
    out.push({ start: st / speed, end: (st + c.totalDuration()) / speed, target: tg, toOpacity: c.vars.opacity ?? c.vars.autoAlpha ?? null });
  } };
  walk(tl, 0); host.remove();
  return { id, tweens: out };
};
</script></body></html>`;
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "hold-probe-"));
fs.writeFileSync(path.join(ROOT, ".hold-probe.html"), harness);
const server = spawn("python3", ["-m", "http.server", "8765", "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
await new Promise((r) => setTimeout(r, 800));
const browser = await puppeteer.launch({ executablePath: chrome, headless: true, userDataDir: tmp, args: ["--window-size=1920,1080"] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  page.on("pageerror", (e) => console.error("pageerror", e.message));
  await page.goto("http://127.0.0.1:8765/.hold-probe.html");
  await page.evaluate(() => document.fonts.ready);
  const all = [];
  console.log("scene        dur   lastAction  exit   hold");
  for (const s of scenes) {
    const r = await page.evaluate((id, src) => window.probe(id, src), s.id, s.src);
    all.push(r);
    const tw = r.tweens.filter((t) => t.start < s.dur);
    // The exit is the first fade to 0 in the last 1.3 s that the scene does not undo.
    const exits = tw.filter((t) => t.start >= s.dur - 1.3 && t.toOpacity === 0 && !/cursor|rip/i.test(t.target));
    const exit = exits.length ? Math.min(...exits.map((t) => t.start)) : s.dur;
    const before = tw.filter((t) => t.start < exit - 1e-6 && t.end <= exit + 1e-6 && t.end - t.start < s.dur * 0.6 && !/cursor|rip/i.test(t.target));
    const last = before.length ? Math.max(...before.map((t) => t.end)) : 0;
    console.log(`${s.id.padEnd(10)} ${s.dur.toFixed(2).padStart(6)} ${last.toFixed(2).padStart(9)} ${exit.toFixed(2).padStart(6)} ${(exit - last).toFixed(2).padStart(6)}`);
  }
  if (process.argv.includes("--json")) fs.writeFileSync(path.join(ROOT, "hold-probe.json"), JSON.stringify(all, null, 1));
} finally {
  await browser.close(); server.kill(); fs.rmSync(path.join(ROOT, ".hold-probe.html"), { force: true }); fs.rmSync(tmp, { recursive: true, force: true });
}
process.exit(0);
