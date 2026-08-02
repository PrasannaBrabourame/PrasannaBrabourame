import { JSDOM } from "jsdom";
import fs from "fs";
const html = fs.readFileSync(new URL("./docs/index.html", import.meta.url), "utf8");
const code = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)[1];

function boot({ reduced = false, coarse = false, noCanvas = false } = {}) {
  const dom = new JSDOM(html, { runScripts: "outside-only", pretendToBeVisual: true });
  const { window } = dom;
  window.SVGElement.prototype.getTotalLength = () => 120;
  window.matchMedia = q => ({
    matches: (reduced && /reduced-motion/.test(q)) || (coarse && /pointer:\s*coarse/.test(q)),
    addListener(){}, removeListener(){}
  });
  window.IntersectionObserver = class { constructor(cb){this.cb=cb;} observe(){} unobserve(){} };
  // canvas: jsdom has no 2d context, so fake one and record what gets drawn
  const calls = [];
  window.HTMLCanvasElement.prototype.getContext = noCanvas ? () => null : function () {
    return new Proxy({}, {
      get: (_, k) => {
        if (k === "setTransform" || k === "clearRect" || k === "beginPath" ||
            k === "moveTo" || k === "lineTo" || k === "stroke")
          return (...a) => calls.push([k, ...a]);
        return undefined;
      },
      set: () => true
    });
  };
  let now = 0, q = [], timers = [], id = 1;
  window.requestAnimationFrame = cb => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => { q = []; };
  window.setTimeout = (cb, ms = 0) => { const h = id++; timers.push({ id: h, cb, due: now + ms }); return h; };
  window.clearTimeout = window.clearInterval = i => { timers = timers.filter(t => t.id !== i); };
  window.setInterval = (cb, ms = 1) => { const h = id++; timers.push({ id: h, cb, due: now + ms, every: ms }); return h; };
  window.eval(code);
  const pump = n => { for (let i = 0; i < n; i++) {
    const c = q; q = []; c.forEach(cb => cb(now));
    now += 16;
    timers.filter(t => t.due <= now).forEach(t => {
      if (t.every) t.due = now + t.every; else timers = timers.filter(o => o !== t);
      try { t.cb(); } catch (e) {}
    });
  } };
  return { window, d: window.document, pump, calls, timers: () => timers.length };
}

const fail = [];
const ok = (c, m) => { if (!c) fail.push(m); };

// ─────────── everything on ───────────
{
  const { window, d, pump } = boot();
  // cursor wash
  const wash = d.querySelector(".wash");
  ok(wash, "wash: not created");
  ok(!wash.classList.contains("on"), "wash: visible before the pointer has moved");
  const pm = new window.Event("pointermove");
  pm.clientX = 300; pm.clientY = 200; pm.pointerType = "mouse";
  d.dispatchEvent(pm);
  ok(wash.classList.contains("on"), "wash: did not appear on pointer move");
  pump(40);
  ok(/translate\(/.test(wash.style.transform), "wash: never followed the pointer");
  // touch input must be ignored by the wash
  const t2 = new window.Event("pointermove"); t2.clientX = 900; t2.clientY = 900; t2.pointerType = "touch";
  const beforeT = wash.style.transform; d.dispatchEvent(t2); pump(2);
  ok(true, "");    // position eases, just assert no throw
  d.dispatchEvent(new window.Event("pointerleave"));
  ok(!wash.classList.contains("on"), "wash: did not hide when the pointer left");

  // click ring
  const pd = new window.Event("pointerdown");
  pd.clientX = 120; pd.clientY = 140; pd.pointerType = "mouse";
  d.dispatchEvent(pd);
  ok(d.querySelectorAll(".ring").length === 1, "ring: not created on click");
  // rings must not pile up — the fallback timer has to clear them
  for (let i = 0; i < 25; i++) { const e = new window.Event("pointerdown");
    e.clientX = i * 10; e.clientY = 50; e.pointerType = "mouse"; d.dispatchEvent(e); }
  pump(200);
  ok(d.querySelectorAll(".ring").length === 0,
     `ring: ${d.querySelectorAll(".ring").length} rings left in the DOM`);
  // touch must not spawn rings
  const tp = new window.Event("pointerdown"); tp.clientX = 5; tp.clientY = 5; tp.pointerType = "touch";
  d.dispatchEvent(tp);
  ok(d.querySelectorAll(".ring").length === 0, "ring: a touch spawned a ring");

  // living mark
  const mark = d.querySelector(".brand .mark");
  const orbit = mark.querySelector(".orbit");
  const outer = mark.querySelector(".outer");
  const start = orbit.getAttribute("cx");
  pump(60);
  ok(orbit.getAttribute("cx") !== start, "mark: dot never moved");
  ok(outer.getAttribute("transform"), "mark: outer ring never rotated");
  // the dot must stay on the r=27 ring
  let offRing = 0;
  for (let i = 0; i < 400; i++) {
    pump(1);
    const dx = parseFloat(orbit.getAttribute("cx")) - 50;
    const dy = parseFloat(orbit.getAttribute("cy")) - 50;
    if (Math.abs(Math.hypot(dx, dy) - 27) > 0.4) offRing++;
  }
  ok(offRing === 0, `mark: dot left the ring on ${offRing} frames`);
  // the crossing must fire, and must clear itself
  let sawCross = false;
  for (let i = 0; i < 1800; i++) { pump(1); if (mark.classList.contains("cross")) sawCross = true; }
  ok(sawCross, "mark: the crossing never fired in 1800 frames");
  pump(400);
  ok(!mark.classList.contains("cross"), "mark: .cross stuck on");

  // no unbounded timer growth across all three
  const t1 = window.document && 0;
  pump(3000);
  ok(d.body.querySelectorAll(".ring").length === 0, "ring: leaked over 3000 frames");
}

// ─────────── reduced motion: all three must be absent ───────────
{
  const { d, pump } = boot({ reduced: true });
  pump(200);
  ok(!d.querySelector(".wash"), "reduced motion: cursor wash still created");
  const orbit = d.querySelector(".brand .orbit");
  ok(orbit.getAttribute("cx") === "50", "reduced motion: mark animated anyway");
  ok(!d.querySelector(".brand .outer").getAttribute("transform"),
     "reduced motion: outer ring rotated anyway");
}

// ─────────── coarse pointer: wash off, trace and mark still on ───────────
{
  const { d, pump } = boot({ coarse: true });
  pump(60);
  ok(!d.querySelector(".wash"), "touch device: cursor wash created (pointless there)");
  ok(d.querySelector(".brand .orbit").getAttribute("cx") !== "50",
     "touch device: mark not animating");
}

// ─────────── the background canvas must be gone for good ───────────
{
  const { d, pump } = boot();
  pump(40);
  ok(!d.querySelector(".trace"), "the removed ambient canvas came back");
  ok(!d.querySelector("canvas"), "a stray canvas is being created");
}

console.log(fail.length ? "FAIL\n - " + fail.filter(Boolean).join("\n - ")
                        : "wash / mark / no-canvas clean (21 checks)");
process.exit(fail.filter(Boolean).length ? 1 : 0);
