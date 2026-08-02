import { JSDOM } from "jsdom";
import fs from "fs";
const html = fs.readFileSync(new URL("./docs/index.html", import.meta.url), "utf8");
const code = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)[1];

function boot({ reduced = false } = {}) {
  const dom = new JSDOM(html, { runScripts: "outside-only", pretendToBeVisual: true });
  const { window } = dom;
  window.SVGElement.prototype.getTotalLength = () => 120;
  window.HTMLCanvasElement.prototype.getContext = () => null;
  window.matchMedia = q => ({ matches: reduced && /reduced-motion/.test(q), addListener(){}, removeListener(){} });
  const ios = [];
  window.IntersectionObserver = class {
    constructor(cb){ this.cb=cb; this.els=[]; ios.push(this); }
    observe(el){ this.els.push(el); } unobserve(){} disconnect(){}
    fire(v=true){ this.cb(this.els.map(t=>({isIntersecting:v,target:t})), this); }
  };
  let now=0,q=[],timers=[],id=1;
  window.requestAnimationFrame = cb => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => { q=[]; };
  window.setTimeout = (cb,ms=0)=>{ const h=id++; timers.push({id:h,cb,due:now+ms}); return h; };
  window.setInterval = (cb,ms=1)=>{ const h=id++; timers.push({id:h,cb,due:now+ms,every:ms}); return h; };
  window.clearTimeout = window.clearInterval = i => { timers = timers.filter(t=>t.id!==i); };
  window.eval(code);
  const pump = n => { for(let i=0;i<n;i++){ const c=q;q=[];c.forEach(cb=>cb(now)); now+=16;
    timers.filter(t=>t.due<=now).forEach(t=>{ if(t.every)t.due=now+t.every; else timers=timers.filter(o=>o!==t);
      try{t.cb();}catch(e){} }); } };
  return { window, d: window.document, ios, pump };
}
const fail=[]; const ok=(c,m)=>{ if(!c) fail.push(m); };

// ─────────── confidentiality: nothing identifying may survive ───────────
{
  const banned = ["MUIS","ACRA","halal","Halal","HIVA","ComplAI","SecWiz","LighTool",
                  "Corporate Service Provider"];
  banned.forEach(w => ok(!html.includes(w), `confidentiality: "${w}" still in the page`));
  // and no product name should reach a screen reader through an aria-label either
  const { d } = boot();
  const labels = [...d.querySelectorAll("[aria-label]")].map(e => e.getAttribute("aria-label")).join(" ");
  banned.forEach(w => ok(!labels.includes(w), `confidentiality: "${w}" in an aria-label`));
}

// ─────────── hero illustration ───────────
{
  const { d } = boot();
  const fig = d.querySelector(".hero-art");
  ok(fig, "hero art: not present");
  const img = fig && fig.querySelector("img");
  ok(img, "hero art: no <img>");
  ok(d.querySelector('.hero-art source[type="image/webp"]'), "hero art: no webp source");
  ok(img && img.getAttribute("width") && img.getAttribute("height"),
     "hero art: no intrinsic size — the page will shift as it loads");
  const alt = img ? img.getAttribute("alt") || "" : "";
  ok(alt.length > 60, "hero art: alt text is missing or too thin");
  ok(/Prasanna/.test(alt), "hero art: alt does not name the subject");
  ok(!/\bimage of\b|\bpicture of\b/i.test(alt), "hero art: alt starts with a redundant phrase");
  ok(img && /srcset/.test(img.outerHTML), "hero art: no srcset — 2x screens get a soft image");
  // it must sit beside the words, not below them
  const grid = d.querySelector(".hero .hero-grid");
  ok(grid, "hero art: hero is not a two-column grid");
  ok(grid && grid.querySelector(".hero-words") && grid.querySelector(".hero-art"),
     "hero art: words and art are not siblings in the grid");
  ok(!d.querySelector(".portrait"), "hero art: the old traced portrait is still in the page");
  ok(!d.querySelector(".wrap.split"), "hero art: leftover split wrapper");
}

// ─────────── the top nav must actually be visible ───────────
{
  const { d } = boot();
  const mast = d.querySelector(".masthead");
  const nav = d.querySelector("nav.nav");
  ok(nav, "nav: missing");
  ok(mast && mast.contains(nav),
     "nav: sits outside the masthead — the masthead gradient will paint over it");
  const css = html.match(/<style>([\s\S]*?)<\/style>/)[1];
  const navRule = css.match(/\n  \.nav\{([^}]*)\}/);
  ok(navRule && !/position:\s*fixed/.test(navRule[1]),
     "nav: still position:fixed at desktop — that is what hid it");
  const links = [...nav.querySelectorAll("a")].map(a => a.getAttribute("href"));
  ok(links.length >= 5, `nav: only ${links.length} links`);
  const ids = [...d.querySelectorAll("[id]")].map(e => e.id);
  links.forEach(h => ok(!h.startsWith("#") || ids.includes(h.slice(1)),
                        `nav: ${h} points at nothing`));
  ok(links.includes("#learning"), "nav: no link to the learning section");
  ok(nav.querySelector("a.nav-cta"), "nav: no call to action");
  ok(d.querySelector('.nav-toggle[aria-controls="site-nav"]'), "nav: toggle not wired to the nav");
}

// ─────────── email ───────────
{
  ok(html.includes("prasanna18101994@gmail.com"), "email: new address missing");
  ok(!html.includes("prasanna.brabourame1@ncs.co"), "email: the work address is still in the page");
  const { d } = boot();
  const mailtos = [...d.querySelectorAll('a[href^="mailto:"]')].map(a => a.getAttribute("href"));
  ok(mailtos.length >= 2, "email: expected the contact block and the footer to link it");
  ok(mailtos.every(m => m.includes("prasanna18101994@gmail.com")),
     "email: a mailto still points somewhere else");
}

// ─────────── certifications & continuous learning ───────────
{
  const { d } = boot();
  const sec = d.getElementById("learning");
  ok(sec, "learning: section missing");
  ok(sec && /continuous learning/i.test(sec.textContent), "learning: no eyebrow");
  ok(sec && sec.querySelector("svg"), "learning: no cadence chart");
  const links = [...sec.querySelectorAll("a")].map(a => a.getAttribute("href"));
  ok(links.some(h => h.includes("skills.google")), "learning: no Google Skills link");
  ok(links.some(h => h.includes("credly.com")), "learning: no Credly link");
  // the numbers must match what the profiles actually say
  const txt = sec.textContent.replace(/\s+/g, " ");
  ok(/13,895 points/.test(txt), "learning: points figure wrong or missing");
  ok(/Diamond League/.test(txt), "learning: league missing");
  ok(/38 skill badges/.test(txt), "learning: badge count wrong or missing");
  ok(/15 on Credly/.test(txt), "learning: Credly count wrong or missing");
  // and must NOT claim certifications that are only 'recommended next' on Credly
  ["Professional Cloud Architect", "Associate Cloud Engineer", "Cloud Digital Leader",
   "Professional Cloud Developer", "Professional Cloud DevOps"].forEach(c =>
    ok(!txt.includes(c), `learning: claims "${c}", which is not actually held`));
}

// ─────────── the scenario explorer ───────────
{
  const { d, window } = boot();
  const fig = d.getElementById("reality");
  ok(fig, "explorer: figure missing");
  const btns = [...fig.querySelectorAll(".sw")];
  const notes = [...fig.querySelectorAll(".sc-note")];
  const groups = [...fig.querySelectorAll("svg .sc")];
  const KEYS = ["demo","scale","malformed","injection","context","memory","leakage","cost","audit"];

  ok(btns.length === 9, `explorer: expected 9 chips, got ${btns.length}`);
  ok(groups.length === 9, `explorer: expected 9 svg overlays, got ${groups.length}`);
  ok(notes.length === 9, `explorer: expected 9 notes, got ${notes.length}`);
  ok(fig.querySelector('[role="group"]'), "explorer: chips not grouped");
  ok(fig.querySelector('[aria-live="polite"]'), "explorer: notes not announced");

  // every chip must have a matching overlay AND a matching note
  KEYS.forEach(k => {
    ok(btns.some(b => b.getAttribute("data-state") === k), `explorer: no chip for "${k}"`);
    ok(groups.some(g => g.classList.contains(k)), `explorer: no svg overlay for "${k}"`);
    ok(notes.some(n => n.getAttribute("data-for") === k), `explorer: no note for "${k}"`);
  });
  // notes must be substantial and name the mitigation, not just the failure
  notes.forEach(n => {
    const k = n.getAttribute("data-for");
    ok(n.textContent.trim().length > 90, `explorer: note "${k}" is too thin`);
  });
  ["backoff","schema","provenance","budget","TTL","redaction","cache","decision trace"]
    .forEach(w => ok(fig.textContent.includes(w), `explorer: never mentions "${w}"`));
  // the current-trend vocabulary the section is meant to cover
  ["orchestrat","serverless","guardrail","vector","memory","injection","residency",
   "audit","token budget","allow-list"].forEach(w =>
    ok(fig.textContent.toLowerCase().includes(w.toLowerCase()),
       `explorer: does not cover "${w}"`));

  // it starts on the demo, with exactly one overlay and one note showing
  ok(groups.filter(g => g.classList.contains("on")).length === 1, "explorer: not exactly one overlay on");
  ok(notes.filter(n => n.classList.contains("on")).length === 1, "explorer: not exactly one note on");
  ok(groups.find(g => g.classList.contains("demo")).classList.contains("on"),
     "explorer: does not start on the demo");

  // switching
  const inj = btns.find(b => b.getAttribute("data-state") === "injection");
  inj.dispatchEvent(new window.Event("click"));
  ok(groups.find(g => g.classList.contains("injection")).classList.contains("on"),
     "explorer: overlay did not switch");
  ok(notes.find(n => n.getAttribute("data-for") === "injection").classList.contains("on"),
     "explorer: note did not switch");
  ok(groups.filter(g => g.classList.contains("on")).length === 1,
     "explorer: more than one overlay showing after a switch");
  ok(notes.filter(n => n.classList.contains("on")).length === 1,
     "explorer: more than one note showing after a switch");
  ok(inj.getAttribute("aria-pressed") === "true" &&
     btns.filter(b => b.getAttribute("aria-pressed") === "true").length === 1,
     "explorer: aria-pressed out of step");
}

// ─────────── the two-line section divider is gone ───────────
{
  const css = html.match(/<style>([\s\S]*?)<\/style>/)[1];
  const band = css.match(/\n  \.band\{([^}]*)\}/);
  ok(band, "divider: .band rule missing");
  ok(band && !/background-image/.test(band[1]),
     "divider: .band still paints the doubled sketched rule");
  ok(band && /border-top:\s*1px/.test(band[1]), "divider: no hairline replacement");
}

// ─────────── the explorable stack ───────────
{
  const { d } = boot();
  const fig = d.querySelector(".stack-fig");
  ok(fig, "stack: figure wrapper missing");
  const layers = d.querySelectorAll(".stack-fig svg.sk .lyr");
  ok(layers.length === 6, `stack: expected 6 layers, got ${layers.length}`);
  const note = d.getElementById("layerNote");
  ok(note, "stack: no note element");
  ok(note && note.getAttribute("aria-live") === "polite", "stack: note is not announced");
  [...layers].forEach((g, i) => {
    ok(g.getAttribute("tabindex") === "0", `stack: layer ${i} not focusable`);
    ok((g.getAttribute("data-note") || "").length > 20, `stack: layer ${i} has no note`);
    ok((g.getAttribute("aria-label") || "").length > 20, `stack: layer ${i} has no label`);
  });
  // no product names — the whole point of the rewrite
  const txt = [...layers].map(g => g.textContent + " " + g.getAttribute("aria-label")).join(" ");
  ["React", "Next.js", "Firestore", "PostgreSQL", "BigQuery", "Cloud Run", "Terraform",
   "Docker"].forEach(p => ok(!txt.includes(p), `stack: still names the product "${p}"`));
  // and it should carry the current concerns
  ["governance", "guardrails", "observability", "evaluation", "harness"].forEach(w =>
    ok(txt.toLowerCase().includes(w), `stack: does not mention "${w}"`));
  // focusing a layer must fill the note
  const before = note.textContent;
  layers[3].dispatchEvent(new (d.defaultView.Event)("focus"));
  ok(note.textContent !== before, "stack: focusing a layer did not update the note");
  ok(note.querySelector("b"), "stack: note has no heading");
  ok(layers[3].classList.contains("on"), "stack: focused layer not marked");
}

// ─────────── little actors ───────────
{
  const { d, ios, pump } = boot();
  const cells = d.querySelectorAll(".case-actor");
  ok(cells.length === 6, `actors: expected 6 workers (4 cases + how + learning), got ${cells.length}`);
  ["certify","comply","remediate","insight","how","learn"].forEach(k =>
    ok(d.querySelector(`[data-actor="${k}"] pre.actor`), `actors: no figure for "${k}"`));
  [...cells].forEach(c => {
    ok(c.getAttribute("aria-hidden") === "true", "actors: a case worker is not aria-hidden");
    ok(c.querySelector("pre.actor"), "actors: a case worker has no figure");
    ok(c.querySelector(".note"), "actors: a case worker has no note");
  });
  const pacer = d.querySelector(".track-stage .pacer");
  ok(pacer, "pacer: not added to the timeline");
  ok(pacer && pacer.parentElement.classList.contains("sk-scroll"),
     "pacer: attached to the figure, so it overlaps the caption");
  const cap = d.querySelector(".track-stage figcaption");
  ok(cap && !cap.contains(pacer), "pacer: sits inside the caption");

  // bring everything on screen, then run
  ios.forEach(o => o.fire(true));
  const first = [...cells].map(c => c.querySelector("pre.actor").textContent);
  pump(400);
  const later = [...cells].map(c => c.querySelector("pre.actor").textContent);
  ok(first.some((f, i) => f !== later[i]), "actors: no case worker ever animated");
  [...cells].forEach((c, i) => {
    const rows = c.querySelector("pre.actor").textContent.split("\n").length;
    ok(rows === 4, `actors: worker ${i} rendered ${rows} rows, expected 4`);
  });

  // the pacer must visit every station and stay within 0-100%
  const seen = new Set(); let bad = 0;
  for (let i = 0; i < 6000; i++) {
    pump(1);
    const l = parseFloat(pacer.style.left);
    if (!(l >= 0 && l <= 100)) bad++;
    seen.add(pacer.style.left);
  }
  ok(bad === 0, `pacer: left went out of range on ${bad} frames`);
  ok(seen.size >= 6, `pacer: only visited ${seen.size} positions, expected 6`);
  ok(pacer.querySelector(".say").textContent.length > 0, "pacer: never said anything");

  // one ticker only, and it must stop when the tab is hidden
  const before = pacer.style.left;
  Object.defineProperty(d, "hidden", { value: true, configurable: true });
  d.dispatchEvent(new (d.defaultView.Event)("visibilitychange"));
  pump(500);
  ok(pacer.style.left === before, "actors: still ticking with the tab hidden");
}

// ─────────── reduced motion ───────────
{
  const { d, ios, pump } = boot({ reduced: true });
  ios.forEach(o => o.fire(true));
  pump(400);
  ok(!d.querySelector("pre.actor"), "reduced motion: actors were created anyway");
  ok(!d.querySelector(".pacer"), "reduced motion: the pacer was created anyway");
  ok(d.querySelector(".hero-art img"), "reduced motion: the hero illustration should still be there");
}

console.log(fail.length ? "FAIL\n - " + fail.join("\n - ")
                        : "confidentiality / nav / email / learning / stack / actors clean (" + (9+9+11+20+13+4+13+37+62) + " checks)");
process.exit(fail.length ? 1 : 0);
