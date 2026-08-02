import { JSDOM } from "jsdom";
import fs from "fs";
const html = fs.readFileSync(new URL("./docs/index.html", import.meta.url), "utf8");
const dom = new JSDOM(html, { runScripts: "outside-only", pretendToBeVisual: true });
const { window } = dom;
window.SVGElement.prototype.getTotalLength = () => 120;
window.IntersectionObserver = class { constructor(cb){this.cb=cb;} observe(){} unobserve(){} };
// ← the whole point of this run: the user prefers reduced motion
window.matchMedia = q => ({ matches: /reduced-motion/.test(q), addListener(){}, removeListener(){} });

const code = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)[1];
window.eval(code);
const d = window.document, fail = [];
const ok = (c,m) => { if(!c) fail.push(m); };

ok(!d.documentElement.classList.contains("anim"),
   "reduced motion: .anim was applied — diagrams would start hidden");
ok([...d.querySelectorAll("svg.sk path.st")].every(p => !p.style.strokeDasharray),
   "reduced motion: strokes were prepared for animation");
ok(d.querySelectorAll(".reveal.in").length === d.querySelectorAll(".reveal").length,
   "reduced motion: reveals not shown immediately");
const q = d.querySelector("#convo .q");
ok(q && q.classList.contains("in"), "reduced motion: first question not immediately visible");
// quiz must still advance, with no transition delay
q.querySelectorAll(".qb")[1].dispatchEvent(new window.Event("click"));
await new Promise(r => setTimeout(r, 20));
ok(d.querySelectorAll("#convo .q").length === 2, "reduced motion: quiz did not advance");
ok(d.querySelector("#convo .q:nth-child(2)").classList.contains("in"),
   "reduced motion: next question not immediately visible");
// orbiting mark must not animate
ok(!d.querySelector(".brand .orbit").style.transition,
   "reduced motion: brand mark still animating");

console.log(fail.length ? "FAIL\n - "+fail.join("\n - ") : "reduced-motion path clean (7 checks)");
process.exit(fail.length?1:0);
