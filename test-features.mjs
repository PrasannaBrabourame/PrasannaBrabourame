import { JSDOM } from "jsdom";
import fs from "fs";

const here = p => new URL(p, import.meta.url);
const html = fs.readFileSync(here("./docs/index.html"), "utf8");
const code = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)[1];
const css = html.match(/<style>([\s\S]*?)<\/style>/)[1];

const fail = [];
const ok = (c, m) => { if (!c) fail.push(m); };
let checks = 0;
const check = (c, m) => { checks++; ok(c, m); };

function boot({ prefersDark = false, stored = null } = {}) {
  // a real origin, so jsdom gives us a real localStorage instead of an opaque one
  const dom = new JSDOM(html, {
    runScripts: "outside-only", pretendToBeVisual: true, url: "https://example.test/"
  });
  const { window } = dom;
  window.localStorage.clear();
  if (stored !== null) window.localStorage.setItem("theme", stored);
  const store = window.localStorage;
  window.matchMedia = q => ({
    matches: prefersDark && /prefers-color-scheme:\s*dark/.test(q),
    addEventListener() {}, removeEventListener() {},
    addListener() {}, removeListener() {}
  });
  window.SVGElement.prototype.getTotalLength = () => 120;
  window.IntersectionObserver = class { constructor(cb) { this.cb = cb; } observe() {} unobserve() {} };
  window.requestAnimationFrame = () => 1;
  window.cancelAnimationFrame = () => {};
  // the boot script in <head> is not run by runScripts:"outside-only"
  const bootSrc = html.match(/<script data-theme-boot>([\s\S]*?)<\/script>/)[1];
  window.eval(bootSrc);
  window.eval(code);
  return { window, d: window.document, store };
}

/* ─────────── the invariant that makes the other suites work ─────────── */
{
  const opens = html.match(/<script(\s[^>]*)?>/g) || [];
  const bare = opens.filter(t => t === "<script>");
  check(bare.length === 1,
    `script tags: ${bare.length} bare <script> tags — every suite extracts the page ` +
    `script with a regex anchored on one, so extras silently widen the match`);
  check(/<script data-theme-boot>/.test(html), "theme: boot script missing from <head>");
  const bootAt = html.indexOf("<script data-theme-boot>");
  check(bootAt > -1 && bootAt < html.indexOf("<body"),
    "theme: boot script must run before <body> or the wrong theme flashes");
}

/* ─────────── dark theme ─────────── */
{
  check(/@media \(prefers-color-scheme:dark\)/.test(css), "theme: no system-preference block");
  check(/:root:not\(\[data-theme="light"\]\)/.test(css),
    "theme: system block must yield to an explicit light choice");
  check(/:root\[data-theme="dark"\]\{/.test(css), "theme: no explicit dark block");

  // every token the dark palettes touch must also have a light default on :root,
  // or the light theme inherits a hole
  const rootBlock = css.match(/\n  :root\{([\s\S]*?)\n  \}/)[1];
  const lightTokens = new Set([...rootBlock.matchAll(/(--[a-z0-9-]+):/g)].map(m => m[1]));
  const darkBlock = css.match(/:root\[data-theme="dark"\]\{([\s\S]*?)\n  \}/)[1];
  const darkTokens = [...darkBlock.matchAll(/(--[a-z0-9-]+):/g)].map(m => m[1]);
  const orphans = darkTokens.filter(t => !lightTokens.has(t));
  check(orphans.length === 0, `theme: dark-only tokens with no light default: ${orphans.join(", ")}`);

  // the two dark palettes must agree, or the toggle changes more than the theme
  const sysBlock = css.match(/:root:not\(\[data-theme="light"\]\)\{([\s\S]*?)\n    \}/)[1];
  const pairs = b => Object.fromEntries(
    [...b.matchAll(/(--[a-z0-9-]+):([^;]+);/g)].map(m => [m[1], m[2].trim()]));
  const sys = pairs(sysBlock), exp = pairs(darkBlock);
  const drift = Object.keys(exp).filter(k => sys[k] !== exp[k]);
  check(drift.length === 0, `theme: the two dark palettes disagree on: ${drift.join(", ")}`);

  // the diagrams only ever draw with these three
  for (const t of ["--ink", "--teal", "--amber"])
    check(t in exp, `theme: dark palette does not redefine ${t} — the 13 diagrams would not follow`);

  // the paper grain multiplies; on a dark ground that has to invert
  check(/mix-blend-mode:var\(--grain-blend\)/.test(css), "theme: paper grain blend not tokenised");
  check(exp["--grain-blend"] === "screen", "theme: grain still multiplying in dark");
  check(exp["--art-blend"] === "normal", "theme: hero illustration still multiplying in dark");
}

/* ─────────── nothing hardcoded that the theme needs to move ─────────── */
{
  const panel = css.match(/\.contact\{([\s\S]*?)\n  \}/)[1];
  check(!/#fff|#ffffff/i.test(panel), "theme: .contact still has a hardcoded white");
  // print deliberately forces white paper and black ink, so exclude it
  const themed = css.replace(/@media print\{[\s\S]*?\n  \}/, "");
  const stray = [...themed.matchAll(/\n +([^\s@{}][^{}\n]*)\{([^}]*)\}/g)]
    .filter(([, sel]) => !/^:root|^@|theme-toggle/.test(sel))
    .filter(([, , body]) => /(?:background|color):\s*#fff\b/i.test(body))
    .map(([, sel]) => sel.trim());
  check(stray.length === 0, `theme: rules still painting a literal #fff: ${stray.join(" / ")}`);
}

/* ─────────── the toggle ─────────── */
{
  const { d } = boot();
  const btn = d.querySelector(".theme-toggle");
  check(btn, "theme: no toggle button");
  check(btn && btn.getAttribute("aria-pressed") === "false",
    "theme: toggle should read not-pressed on a light default");
  check(btn && /dark/i.test(btn.getAttribute("aria-label")),
    "theme: toggle label should say what it switches to");
  check(btn && btn.querySelector(".t-sun") && btn.querySelector(".t-moon"),
    "theme: toggle needs both icons");
  check(!d.querySelector("nav.nav .theme-toggle"),
    "theme: toggle must sit outside nav.nav — it would count as a nav item");
}
{
  // click flips the attribute, records the choice, and repaints the browser chrome
  const { window, d, store } = boot();
  const btn = d.querySelector(".theme-toggle");
  btn.dispatchEvent(new window.Event("click"));
  check(d.documentElement.getAttribute("data-theme") === "dark", "theme: click did not go dark");
  check(store.getItem("theme") === "dark", "theme: choice not persisted");
  check(btn.getAttribute("aria-pressed") === "true", "theme: aria-pressed not updated");
  check(/light/i.test(btn.getAttribute("aria-label")), "theme: label not updated after switching");
  const bars = [...d.querySelectorAll('meta[name="theme-color"]')];
  check(bars.length >= 1 && bars.every(m => m.getAttribute("content") === "#16191d"),
    "theme: theme-color meta not repainted");
  btn.dispatchEvent(new window.Event("click"));
  check(d.documentElement.getAttribute("data-theme") === "light", "theme: does not toggle back");
  check(store.getItem("theme") === "light", "theme: light choice not persisted");
}
{
  // a stored choice must win over the system preference, and be applied pre-paint
  const { d } = boot({ prefersDark: true, stored: "light" });
  check(d.documentElement.getAttribute("data-theme") === "light",
    "theme: stored light choice lost to the system preference");
  check(d.querySelector(".theme-toggle").getAttribute("aria-pressed") === "false",
    "theme: toggle state wrong for a stored light choice");
}
{
  // no stored choice: follow the machine, and leave data-theme unset so it keeps following
  const { d } = boot({ prefersDark: true });
  check(!d.documentElement.hasAttribute("data-theme"),
    "theme: pinned data-theme without the reader ever choosing");
  check(d.querySelector(".theme-toggle").getAttribute("aria-pressed") === "true",
    "theme: toggle should reflect the system preference when unset");
}

/* ─────────── print stays on paper ─────────── */
{
  const print = css.match(/@media print\{([\s\S]*?)\n  \}/)[1];
  check(/:root\[data-theme="dark"\]/.test(print), "print: dark theme not overridden for print");
  check(/--grain-opacity:0/.test(print), "print: paper grain not switched off");
  check(/\.theme-toggle\{display:none\}/.test(print), "print: toggle still printing");
}

/* ─────────── structured data ─────────── */
{
  const raw = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
  check(raw, "jsonld: no block in <head>");
  let data = null;
  try { data = JSON.parse(raw[1]); } catch (e) { ok(false, "jsonld: does not parse — " + e.message); }
  checks++;
  if (data) {
    check(data["@type"] === "Person", "jsonld: not a Person");
    check(data.name === "Prasanna Brabourame", "jsonld: wrong name");
    check(/^https:\/\//.test(data.url), "jsonld: url placeholder not resolved");
    check(!/\{\{/.test(JSON.stringify(data)), "jsonld: unresolved template placeholder");
    check(Array.isArray(data.sameAs) && data.sameAs.length >= 4, "jsonld: too few sameAs profiles");
    check(!JSON.stringify(data).includes("@ncs.co"), "jsonld: leaks the work email address");
  }
}

/* ─────────── self-hosted fonts ─────────── */
{
  check(!/fonts\.googleapis\.com|fonts\.gstatic\.com/.test(html),
    "fonts: still calling Google");
  const faces = [...css.matchAll(/url\(fonts\/([^)]+)\)/g)].map(m => m[1]);
  check(faces.length >= 4, `fonts: only ${faces.length} @font-face sources inlined`);
  const gone = faces.filter(f => !fs.existsSync(here("./docs/fonts/" + f)));
  check(gone.length === 0, `fonts: referenced but not on disk: ${gone.join(", ")}`);
  check(/font-display:\s*swap/.test(css), "fonts: no font-display:swap — text would be invisible while loading");
  check(fs.existsSync(here("./docs/fonts/OFL.txt")), "fonts: licence notice not shipped");

  // no third-party origin may be fetched at load; outbound links are fine
  const fetched = [...html.matchAll(/(?:src|href)="(https?:\/\/[^"]+)"/g)]
    .map(m => new URL(m[1]).host)
    .filter(h => !/prasannabrabourame\.github\.io$/.test(h));
  const linkHosts = new Set(["linkedin.com", "github.com", "medium.com",
    "stackoverflow.com", "www.credly.com", "calendly.com", "www.skills.google"]);
  const uninvited = [...new Set(fetched)].filter(h => !linkHosts.has(h));
  check(uninvited.length === 0, `third party: page loads resources from ${uninvited.join(", ")}`);
}

/* ─────────── 404 ─────────── */
{
  const p = here("./docs/404.html");
  check(fs.existsSync(p), "404: docs/404.html not generated");
  if (fs.existsSync(p)) {
    const nf = fs.readFileSync(p, "utf8");
    check(/<title>/.test(nf), "404: no title");
    check(/noindex/.test(nf), "404: should not be indexed");
    check(!/\{\{/.test(nf), "404: unresolved placeholder");
    check(/prefers-color-scheme:dark/.test(nf), "404: no dark theme");
    check(!/https:\/\/fonts\./.test(nf), "404: pulls a webfont — it must never depend on anything");
  }
}

/* ─────────── contact form ─────────── */
{
  check(!/\{\{CONTACT_ENDPOINT\}\}/.test(html), "contact: endpoint placeholder not substituted");
  const ep = code.match(/var ENDPOINT = "([^"]*)"/);
  check(ep, "contact: ENDPOINT not found");
  check(ep && (ep[1] === "" || /^https:\/\//.test(ep[1])),
    "contact: endpoint must be https or empty");
  check(/AbortController/.test(code), "contact: no timeout — a hung request strands the button");
  check(/clearTimeout\(timer\)/.test(code), "contact: timer not cleared on both paths");

  const { window, d } = boot();
  const form = d.getElementById("contactForm");
  const note = d.getElementById("fNote");
  check(form && note, "contact: form or note element missing");

  // honeypot: a filled trap submits nothing at all
  let called = 0;
  window.fetch = () => { called++; return Promise.resolve({ ok: true }); };
  const fld = (f, n) => f.elements.namedItem(n);
  fld(form, "company_url").value = "http://spam.example";
  fld(form, "name").value = "Bot"; fld(form, "email").value = "bot@spam.example";
  form.dispatchEvent(new window.Event("submit"));
  check(called === 0, "contact: honeypot did not stop the submission");
  fld(form, "company_url").value = "";

  // validation speaks before anything is sent
  fld(form, "name").value = ""; fld(form, "email").value = "";
  form.dispatchEvent(new window.Event("submit"));
  check(/name and email/i.test(note.textContent), "contact: no prompt for the required fields");
  fld(form, "name").value = "Someone"; fld(form, "email").value = "not-an-email";
  form.dispatchEvent(new window.Event("submit"));
  check(/incomplete/i.test(note.textContent), "contact: accepted a malformed address");
}
{
  // a failing endpoint must hand back a prefilled mailto rather than a dead end
  const { window, d } = boot();
  const code2 = code.replace('var ENDPOINT = ""', 'var ENDPOINT = "https://example.test/f"');
  const dom2 = new JSDOM(html, {
    runScripts: "outside-only", pretendToBeVisual: true, url: "https://example.test/"
  });
  const w = dom2.window;
  w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {},
    addListener() {}, removeListener() {} });
  w.SVGElement.prototype.getTotalLength = () => 120;
  w.IntersectionObserver = class { constructor(cb) { this.cb = cb; } observe() {} unobserve() {} };
  w.requestAnimationFrame = () => 1; w.cancelAnimationFrame = () => {};
  w.AbortController = class { constructor() { this.signal = {}; } abort() {} };
  w.fetch = () => Promise.reject(new Error("network"));
  w.eval(code2);
  const f = w.document.getElementById("contactForm");
  const n = w.document.getElementById("fNote");
  const g = n => f.elements.namedItem(n);
  g("name").value = "Someone"; g("email").value = "someone@example.com";
  g("problem").value = "The pilot never made it past the demo.";
  f.dispatchEvent(new w.Event("submit"));
  await new Promise(r => setTimeout(r, 30));
  const link = n.querySelector('a[href^="mailto:"]');
  check(link, "contact: a failed send left no way to reach you");
  check(link && /someone%40example\.com|someone@example\.com/.test(decodeURI(link.href)),
    "contact: the fallback draft dropped what they typed");
  check(!w.document.getElementById("fSend").disabled,
    "contact: send button left disabled after a failure");
  void d;
}

/* ─────────── footer visit tally ─────────── */
{
  check(!/\{\{COUNTER_ENDPOINT\}\}/.test(html), "tally: endpoint placeholder not substituted");
  const ep = code.match(/var COUNTER = "([^"]*)"/);
  check(ep, "tally: COUNTER not found");
  check(ep && (ep[1] === "" || /^https:\/\//.test(ep[1])), "tally: endpoint must be https or empty");

  const { d } = boot();
  const el = d.getElementById("tally");
  check(el, "tally: no element in the footer");
  check(el && el.hasAttribute("hidden"),
    "tally: must ship hidden — an empty label is worse than no label");
  check(el && el.closest(".colophon"), "tally: not in the colophon");
  check(/\.tally\[hidden\]\{display:none\}/.test(css), "tally: hidden state not enforced in CSS");
}

// helper: boot with a stubbed fetch and let the promise chain settle
async function tally({ reply, reduced = false }) {
  const dom = new JSDOM(html, {
    runScripts: "outside-only", pretendToBeVisual: true, url: "https://example.test/"
  });
  const w = dom.window;
  w.matchMedia = q => ({
    matches: reduced && /reduced-motion/.test(q),
    addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}
  });
  w.SVGElement.prototype.getTotalLength = () => 120;
  w.IntersectionObserver = class { constructor(cb) { this.cb = cb; } observe() {} unobserve() {} };
  let raf = [];
  w.requestAnimationFrame = cb => { raf.push(cb); return raf.length; };
  w.cancelAnimationFrame = () => { raf = []; };
  w.AbortController = class { constructor() { this.signal = {}; } abort() {} };
  w.fetch = () => reply();
  w.eval(code);
  await new Promise(r => setTimeout(r, 40));
  // drive the count-up to completion: the clock has to actually move, and the
  // second frame has to land past the 900ms duration
  let now = 0;
  for (let i = 0; i < 8 && raf.length; i++) {
    const q = raf; raf = [];
    q.forEach(cb => cb(now));
    now += 1000;
  }
  return w.document.getElementById("tally");
}

{
  const el = await tally({ reply: () => Promise.resolve({ ok: true, json: () => Promise.resolve({ value: 1204 }) }) });
  check(!el.hidden, "tally: stayed hidden despite a good response");
  check(/1,204/.test(el.textContent), `tally: number not formatted — got "${el.textContent}"`);
  check(/visits/.test(el.textContent), "tally: no unit label");
}
{
  const el = await tally({ reply: () => Promise.resolve({ ok: true, json: () => Promise.resolve({ value: 1 }) }) });
  check(/^1 visit$/.test(el.textContent.trim()), `tally: singular not handled — got "${el.textContent}"`);
}
{
  // the whole point: a dead service must leave the footer untouched
  const el = await tally({ reply: () => Promise.reject(new Error("offline")) });
  check(el.hidden, "tally: a failed request revealed an empty label");
  check(el.textContent === "", "tally: wrote something despite a failed request");
}
{
  const el = await tally({ reply: () => Promise.resolve({ ok: false, status: 503, json: () => Promise.resolve({}) }) });
  check(el.hidden, "tally: a 503 still revealed the label");
}
{
  const el = await tally({ reply: () => Promise.resolve({ ok: true, json: () => Promise.resolve({ value: "not-a-number" }) }) });
  check(el.hidden, "tally: garbage payload revealed the label");
}
{
  const el = await tally({
    reply: () => Promise.resolve({ ok: true, json: () => Promise.resolve({ value: 512 }) }),
    reduced: true
  });
  check(!el.hidden && /^512 visits$/.test(el.textContent.trim()),
    `tally: reduced motion should set the final number outright — got "${el.textContent}"`);
}

console.log(fail.length
  ? "FAIL\n - " + fail.join("\n - ")
  : `theme / jsonld / fonts / 404 / contact / tally clean (${checks} checks)`);
process.exit(fail.length ? 1 : 0);
