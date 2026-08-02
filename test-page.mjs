import { JSDOM } from "jsdom";
import fs from "fs";

const html = fs.readFileSync(new URL("./docs/index.html", import.meta.url), "utf8");

// jsdom has no SVG geometry; stub getTotalLength so the animator can run
const dom = new JSDOM(html, { runScripts: "outside-only", pretendToBeVisual: true });
const { window } = dom;
window.SVGPathElement && (window.SVGPathElement.prototype.getTotalLength = function () { return 120; });
window.SVGElement.prototype.getTotalLength = function () { return 120; };
 window.HTMLCanvasElement.prototype.getContext = () => null;
window.IntersectionObserver = class {
  constructor(cb) { this.cb = cb; this.seen = []; }
  observe(el) { this.seen.push(el); }
  unobserve() {}
  trigger() { this.cb(this.seen.map(t => ({ isIntersecting: true, target: t })), this); }
};
const observers = [];
const RealIO = window.IntersectionObserver;
window.IntersectionObserver = class extends RealIO {
  constructor(cb, o) { super(cb, o); observers.push(this); }
};
window.matchMedia = q => ({ matches: false, addListener(){}, removeListener(){} });

// run the page's inline script
const code = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)[1];
window.eval(code);

const d = window.document;
const fail = [];
const ok = (c, m) => { if (!c) fail.push(m); };

// ---- readiness check ----
const convo = d.getElementById("convo");
ok(convo.querySelectorAll(".q").length === 1, "quiz: first question not rendered");
ok(convo.querySelector(".qt").textContent.includes("Where does your AI"), "quiz: wrong first question");
ok(convo.querySelectorAll(".qb").length === 3, "quiz: expected 3 options");

// answer all five, always the strongest option, then check the closing text
let steps = 0;
for (let i = 0; i < 5; i++) {
  const blocks = convo.querySelectorAll(".q:not(.done):not(.final)");
  ok(blocks.length === 1, `quiz: ${blocks.length} open blocks at step ${i}`);
  const btns = blocks[0].querySelectorAll(".qb");
  btns[2].dispatchEvent(new window.Event("click"));
  ok(blocks[0].classList.contains("done"), `quiz: block ${i} not marked done`);
  ok(blocks[0].querySelector(".qe"), `quiz: block ${i} has no reflection`);
  ok([...btns].every(b => b.disabled), `quiz: block ${i} buttons still enabled`);
  await new Promise(r => setTimeout(r, 400));
  steps++;
}
const fin = convo.querySelector(".q.final");
ok(fin, "quiz: no closing block");
ok(fin && fin.querySelector(".qe").textContent.includes("further along than most"),
   "quiz: wrong closing for a perfect score");
ok(fin && fin.querySelector(".q-again"), "quiz: no start-over button");
ok(convo.querySelectorAll(".q").length === 6, "quiz: expected 5 questions + close");

// double-click guard
const first = convo.querySelector(".q");
const before = convo.querySelectorAll(".q").length;
first.querySelectorAll(".qb")[0].dispatchEvent(new window.Event("click"));
ok(convo.querySelectorAll(".q").length === before, "quiz: re-answering a done block added a block");

// start over
fin.querySelector(".q-again").dispatchEvent(new window.Event("click"));
ok(convo.querySelectorAll(".q").length === 1, "quiz: start over did not reset");

// ---- lowest score path ----
for (let i = 0; i < 5; i++) {
  convo.querySelector(".q:not(.done):not(.final)").querySelectorAll(".qb")[0]
       .dispatchEvent(new window.Event("click"));
  await new Promise(r => setTimeout(r, 400));
}
ok(convo.querySelector(".q.final .qe").textContent.includes("earlier than you might like"),
   "quiz: wrong closing for a low score");

// ---- draw animation ----
ok(d.documentElement.classList.contains("anim"), "anim: .anim class not applied");
const sk = d.querySelectorAll("svg.sk");
ok(sk.length === 10, `anim: expected 10 animated diagrams, got ${sk.length}`);
  // the three small glyphs are decorative marks, not diagrams — they must NOT
  // be class="sk", or they would sit invisible until scrolled into view
  ok(d.querySelectorAll(".principle .glyph svg").length === 3, "glyphs: expected 3");
  ok([...d.querySelectorAll(".principle .glyph svg")].every(g => !g.classList.contains("sk")),
     "glyphs: a glyph is marked as an animated diagram");
const prepared = [...d.querySelectorAll("svg.sk path.st")]
  .filter(p => !(p.parentNode.classList && p.parentNode.classList.contains("hh")));
const withDash = prepared.filter(p => p.style.strokeDasharray);
ok(withDash.length === prepared.length,
   `anim: ${prepared.length - withDash.length} of ${prepared.length} strokes not prepared`);
const inHachure = [...d.querySelectorAll("svg.sk g.hh path.st")];
ok(inHachure.every(p => !p.style.strokeDasharray),
   "anim: hachure strokes were prepared for drawing (should fade instead)");
ok(prepared.every(p => p.style.strokeDashoffset && p.style.strokeDashoffset !== "0"),
   "anim: strokes not hidden before scroll");

observers.forEach(o => o.trigger());
await new Promise(r => setTimeout(r, 1600));
ok(prepared.every(p => p.style.strokeDashoffset === "0"), "anim: strokes never drew");
ok([...sk].every(s => s.classList.contains("drawn")), "anim: .drawn never applied");

// ---- scroll spy / nav ----
ok(d.querySelector('.nav a[href="#ready"]'), "nav: no self-check link");
ok(d.getElementById("yr").textContent.length === 4, "footer: year not set");

console.log(fail.length ? "FAIL\n - " + fail.join("\n - ") : "all " + (8 + steps) + "+ checks passed");
process.exit(fail.length ? 1 : 0);
