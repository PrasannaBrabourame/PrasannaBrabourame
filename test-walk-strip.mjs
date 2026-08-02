import { JSDOM } from "jsdom";
import fs from "fs";
const html = fs.readFileSync(new URL("./docs/index.html", import.meta.url), "utf8");
const code = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)[1];

function boot({ reduced = false } = {}) {
  const dom = new JSDOM(html, { runScripts: "outside-only", pretendToBeVisual: true });
  const { window } = dom;
  window.SVGElement.prototype.getTotalLength = () => 120;
  window.HTMLCanvasElement.prototype.getContext = () => null;  // no ambient canvas in this test
  window.matchMedia = q => ({ matches: reduced && /reduced-motion/.test(q),
                              addListener(){}, removeListener(){} });
  const ios = [];
  window.IntersectionObserver = class {
    constructor(cb, o) { this.cb = cb; this.o = o; this.els = []; ios.push(this); }
    observe(el) { this.els.push(el); }
    unobserve() {} disconnect() {}
    fire(v = true) { this.cb(this.els.map(t => ({ isIntersecting: v, target: t })), this); }
  };
  // virtual clock: frames AND timers advance together, so cleanup is really tested
  let now = 0, q = [], timers = [], nextId = 1;
  window.requestAnimationFrame = cb => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => { q = []; };
  window.setTimeout = (cb, ms = 0) => {
    const t = { id: nextId++, cb, due: now + ms, every: null }; timers.push(t); return t.id;
  };
  window.setInterval = (cb, ms = 1) => {
    const t = { id: nextId++, cb, due: now + ms, every: ms }; timers.push(t); return t.id;
  };
  window.clearTimeout = window.clearInterval = id => {
    timers = timers.filter(t => t.id !== id);
  };
  window.eval(code);
  const tick = () => {
    now += 16;
    const due = timers.filter(t => t.due <= now);
    due.forEach(t => {
      if (t.every) t.due = now + t.every; else timers = timers.filter(o => o !== t);
      try { t.cb(); } catch (e) {}
    });
  };
  const pump = n => {
    for (let i = 0; i < n; i++) { const c = q; q = []; c.forEach(cb => cb(now)); tick(); }
  };
  return { window, d: window.document, ios, pump, qlen: () => q.length,
           timers: () => timers.length,
           intervals: () => timers.filter(t => t.every).length };
}

const fail = [];
const ok = (c, m) => { if (!c) fail.push(m); };

// ─────────── normal motion ───────────
{
  const { d, ios, pump, qlen, timers, intervals } = boot();
  const fig = d.getElementById("figure");
  const stage = d.getElementById("stage");
  ok(stage && fig, "strip: stage/figure missing");
  ok(d.querySelector('.strip[aria-hidden="true"]'), "strip: not aria-hidden (it is decorative)");
  ok(fig.textContent.split("\n").length === 5, "strip: standing figure is not 5 rows");
  ok(fig.textContent.includes("\\O>"), "strip: figure not facing right at rest");

  // find the observer watching the stage and make sure nothing runs before it fires
  const stageIO = ios.find(o => o.els.includes(stage));
  ok(stageIO, "strip: stage is not observed");
  const before = qlen();
  pump(5);
  const x0 = fig.style.left;
  ok(x0 === "90px", `strip: figure moved before being on screen (${x0})`);

  stageIO.fire(true);
  pump(400);
  ok(fig.style.left !== "90px", "strip: figure never moved after coming on screen");
  ok(d.querySelectorAll(".step").length > 0, "strip: no footprints laid down");

  // run long enough for several actions to complete
  pump(4000);
  const marks = [...d.querySelectorAll("#stage .gm")].map(m => m.className.replace("gm ", ""));
  ok(marks.length > 0, "strip: no actions ever performed");
  const kinds = new Set(marks);
  ok(kinds.size >= 2, `strip: only one kind of action in 4400 frames (${[...kinds]})`);
  ok(d.querySelectorAll(".bubble").length === 1, "strip: bubble missing");

  // the walker must stay inside the stage
  const xs = [];
  for (let i = 0; i < 3000; i++) { pump(1); xs.push(parseFloat(fig.style.left)); }
  ok(Math.min(...xs) >= 45, `strip: walked off the left edge (${Math.min(...xs)})`);
  ok(Math.max(...xs) <= 575, `strip: walked off the right edge (${Math.max(...xs)})`);

  // pausing: off-screen must stop the loop
  stageIO.fire(false);
  pump(2);
  const parked = fig.style.left;
  pump(600);
  ok(fig.style.left === parked, "strip: still animating while off screen");
  stageIO.fire(true);
  // he may resume mid-idle (up to ~210 frames), so give him room to start walking
  let resumed = false;
  for (let i = 0; i < 60 && !resumed; i++) { pump(25); if (fig.style.left !== parked) resumed = true; }
  ok(resumed, "strip: did not resume when scrolled back");

  // DOM must not grow without bound
  pump(6000);
  const nodes = d.getElementById("stage").childElementCount;
  ok(nodes < 80, `strip: ${nodes} nodes left in the stage — DOM cleanup is leaking`);
  // Timers legitimately rise and fall — footprints live 5s, ground marks up to 70s.
  // The property that matters is that they stay BOUNDED, and that repeating
  // intervals get cleared. Measured over 576 virtual seconds: 9-23 pending, 0-4
  // intervals. Anything drifting past these means something stopped cleaning up.
  let peak = 0, peakIv = 0;
  for (let k = 0; k < 8; k++) {
    pump(3000);
    peak = Math.max(peak, timers());
    peakIv = Math.max(peakIv, intervals());
  }
  ok(peak < 60, `strip: pending timers peaked at ${peak} — cleanup is leaking`);
  ok(peakIv < 12, `strip: ${peakIv} repeating intervals alive — clearInterval is not firing`);
}

// ─────────── reduced motion ───────────
{
  const { d, pump } = boot({ reduced: true });
  const fig = d.getElementById("figure");
  ok(fig.textContent === "", "reduced motion: walker rendered anyway");
  pump(500);
  ok(fig.textContent === "", "reduced motion: walker started animating");
  ok(d.querySelectorAll("#stage .step, #stage .gm, #stage .spark").length === 0,
     "reduced motion: walker produced artefacts");
}

console.log(fail.length ? "FAIL\n - " + fail.join("\n - ") : "walk strip clean (19 checks)");
process.exit(fail.length ? 1 : 0);
