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

/* ─────────── footer build stamp ─────────── */
{
  check(!/\{\{BUILT_/.test(html), "stamp: a BUILT_ placeholder was not substituted");

  const { d } = boot();
  const built = d.querySelector(".built");
  check(built, "stamp: no .built line in the footer");
  check(built && built.closest("footer"), "stamp: build stamp is not in the footer");

  const time = built && built.querySelector("time");
  check(time, "stamp: the date is not in a <time> element");
  const iso = time && time.getAttribute("datetime");
  check(iso && /^\d{4}-\d{2}-\d{2}$/.test(iso), `stamp: datetime is not ISO — got "${iso}"`);
  check(time && time.textContent.trim().length > 0, "stamp: <time> has no readable text");

  // the date must be baked in, not computed in the browser: a reader wants to
  // know when the page was published, not what today happens to be
  const scriptSetsIt = /getElementById\("?built"?\)|\.built[^{]*textContent/.test(code);
  check(!scriptSetsIt, "stamp: the date is written by script — it must be baked in at build time");

  // it must not be in the future, and must be a real date
  if (iso && /^\d{4}-\d{2}-\d{2}$/.test(iso)) {
    const when = new Date(iso + "T00:00:00Z");
    check(!isNaN(when), `stamp: unparseable date "${iso}"`);
    check(when.getTime() <= Date.now() + 864e5, `stamp: build date is in the future — ${iso}`);
    check(when.getFullYear() >= 2026, `stamp: build date looks stale — ${iso}`);
  }

  // the sitemap should agree with the page, or search engines get a different story
  const sm = fs.readFileSync(here("./docs/sitemap.xml"), "utf8");
  const lastmod = (sm.match(/<lastmod>([^<]+)<\/lastmod>/) || [])[1];
  check(lastmod === iso, `stamp: sitemap lastmod ${lastmod} disagrees with the page ${iso}`);

  // the revision, when present, has to point somewhere real and not be an empty link
  const rev = built && built.querySelector("a.rev");
  if (rev) {
    check(rev.textContent.trim().length >= 7, "stamp: revision link has no text");
    check(/^https:\/\/github\.com\//.test(rev.getAttribute("href")),
      "stamp: revision does not link to GitHub");
    check(!/>\s*<\/a>/.test(built.innerHTML), "stamp: empty revision anchor rendered");
  }
  check(!/&middot;\s*$/.test(built.textContent.trim()),
    "stamp: trailing separator with nothing after it");
}

/* ─────────── the page has to stay readable ─────────── */
{
  // Only real prose: <p>/<h1-3> blocks containing an actual sentence. Chip rows
  // and tech-stack labels have no full stops and would skew the sentence length.
  const body = html.slice(html.indexOf("<body>"), html.indexOf("<script>"))
    .replace(/<svg[\s\S]*?<\/svg>/g, "")
    .replace(/<!--[\s\S]*?-->/g, "");
  const paras = [];
  for (const m of body.matchAll(/<(p|h1|h2|h3)\b[^>]*>([\s\S]*?)<\/\1>/g)) {
    const t = m[2].replace(/<[^>]+>/g, " ")
      .replace(/&[a-z]+;|&#\d+;/g, " ").replace(/\s+/g, " ").trim();
    if (t.split(" ").length >= 5 && /[.!?]/.test(t)) paras.push(t);
  }
  check(paras.length > 25, `readability: only found ${paras.length} prose blocks — extractor broken?`);

  const syll = w => {
    w = w.toLowerCase().replace(/^[^a-z]+|[^a-z]+$/g, "");
    if (!w) return 0;
    let n = (w.match(/[aeiouy]+/g) || []).length;
    if (w.endsWith("e") && n > 1) n -= 1;
    return Math.max(1, n);
  };

  const text = paras.join(" ");
  const words = text.match(/[A-Za-z][A-Za-z'-]*/g) || [];
  const sents = paras.flatMap(p => p.split(/(?<=[.!?])\s+/).filter(x => x.split(" ").length > 1));
  const W = words.length, S = sents.length;
  const syl = words.reduce((a, w) => a + syll(w), 0);
  const flesch = 206.835 - 1.015 * (W / S) - 84.6 * (syl / W);
  const grade = 0.39 * (W / S) + 11.8 * (syl / W) - 15.59;
  const hard = 100 * words.filter(w => syll(w) >= 4).length / W;

  // The site was rewritten for a non-technical reader. These are floors, not
  // targets: drifting back under them means the jargon has crept in again.
  check(flesch >= 58,
    `readability: Flesch reading ease fell to ${flesch.toFixed(1)} — needs to stay at 58+ (plain English is 60+)`);
  check(grade <= 9.5,
    `readability: reading level rose to grade ${grade.toFixed(1)} — needs to stay at or under 9.5`);
  check(hard <= 4,
    `readability: ${hard.toFixed(1)}% of words are 4+ syllables — needs to stay at or under 4%`);
  check(W / S <= 18,
    `readability: sentences average ${(W / S).toFixed(1)} words — needs to stay at or under 18`);

  // no single sentence should be a monster
  const longest = sents.reduce((a, b) => (b.split(" ").length > a.split(" ").length ? b : a), "");
  check(longest.split(" ").length <= 46,
    `readability: a ${longest.split(" ").length}-word sentence — "${longest.slice(0, 90)}…"`);
}

/* ─────────── the open learning resource ─────────── */
{
  const { d } = boot();
  const box = d.querySelector(".resource");
  check(box, "resource: no learning-resource block");
  check(box && box.closest("#learning"),
    "resource: block is outside the learning section, where it belongs");
  const cta = box && box.querySelector("a.resource-cta");
  check(cta, "resource: no call to action link");
  check(cta && cta.getAttribute("href") === "https://prasannabrabourame.github.io/learning-guide/",
    `resource: wrong link — got "${cta && cta.getAttribute("href")}"`);
  check(cta && cta.textContent.trim().length > 8, "resource: link has no readable text");
  check(box && box.querySelector("h3"), "resource: no heading");
  // the count is a claim; keep it where a person will notice it needs updating
  check(box && /267/.test(box.textContent), "resource: topic count missing");
}

/* ─────────── Top K / Top P explorer ─────────── */
function sampler() {
  const { window, d } = boot();
  const set = (el, v) => {
    el.value = String(v);
    el.dispatchEvent(new window.Event("input"));
  };
  const rows = () => [...d.querySelectorAll("#smBars li")];
  const inWords = () => rows().filter(li => !li.classList.contains("out"))
    .map(li => li.querySelector(".sm-word").textContent);
  const tab = m => d.querySelector(`.sm-tab[data-mode="${m}"]`)
    .dispatchEvent(new window.Event("click"));
  return { window, d, set, rows, inWords, tab };
}

{
  const { d, rows } = sampler();
  check(d.getElementById("sampler"), "sampler: section missing");
  check(rows().length === 12, `sampler: expected 12 candidate words, got ${rows().length}`);
  check(d.querySelector("#sampler").closest("#sampling"), "sampler: not inside the sampling section");
  check(d.getElementById("smGo"), "sampler: no draw button");
  check(d.getElementById("smRead").getAttribute("role") === "status",
    "sampler: readout is not announced to screen readers");

  // the percentages shown must actually add up, or the explanation is a lie
  const total = rows().reduce((a, li) =>
    a + parseFloat(li.querySelector(".sm-pct").textContent), 0);
  check(Math.abs(total - 100) <= 1, `sampler: probabilities sum to ${total}%, not 100%`);
}
{
  // Top K keeps exactly K, no matter the shape of the distribution
  const { d, set, inWords, rows } = sampler();
  for (const k of [1, 3, 5, 12]) {
    set(d.getElementById("dialK"), k);
    check(inWords().length === k,
      `sampler: K=${k} kept ${inWords().length} words, expected ${k}`);
  }
  set(d.getElementById("dialK"), 5);
  check(rows()[4].classList.contains("edge"), "sampler: the cut-off word is not marked");
  check(/top <b>5<\/b>/i.test(d.getElementById("smRead").innerHTML),
    "sampler: readout does not state the count");
}
{
  // Top P keeps a varying number — that difference is the entire teaching point
  const { d, set, inWords, tab } = sampler();
  tab("p");
  check(d.querySelector('.sm-tab[data-mode="p"]').getAttribute("aria-pressed") === "true",
    "sampler: Top P tab not marked pressed");
  check(d.querySelector('.sm-dial[data-dial="k"]').hidden,
    "sampler: the K dial is still showing in P mode");
  check(!d.querySelector('.sm-dial[data-dial="p"]').hidden,
    "sampler: the P dial did not appear");

  set(d.getElementById("dialP"), 50);
  const at50 = inWords().length;
  set(d.getElementById("dialP"), 90);
  const at90 = inWords().length;
  set(d.getElementById("dialP"), 100);
  const at100 = inWords().length;
  check(at50 < at90 && at90 < at100,
    `sampler: P should widen the set as it rises — got ${at50}, ${at90}, ${at100}`);
  check(at50 === 2, `sampler: P=50% should keep 2 words on this distribution, got ${at50}`);
  check(at90 === 8, `sampler: P=90% should keep 8 words on this distribution, got ${at90}`);
  check(at90 !== 9, "sampler: P=90% must not just mirror the K dial");
}
{
  // the one that matters: a discarded word must never come out
  const { window, d, set, inWords } = sampler();
  set(d.getElementById("dialK"), 3);
  const allowed = new Set(inWords());
  const go = d.getElementById("smGo");
  const blank = d.querySelector(".sm-blank");
  const drawn = new Set();
  for (let i = 0; i < 400; i++) {
    go.dispatchEvent(new window.Event("click"));
    drawn.add(blank.textContent);
  }
  const leaked = [...drawn].filter(w => !allowed.has(w));
  check(leaked.length === 0,
    `sampler: drew words that were cut off — ${leaked.join(", ")}`);
  check(drawn.size > 1, "sampler: 400 draws produced one word — is it sampling at all?");
  check(/drew/.test(d.getElementById("smOut").textContent), "sampler: no draw feedback");
}
{
  // K=1 is the degenerate case: it must be deterministic, not merely likely
  const { window, d, set } = sampler();
  set(d.getElementById("dialK"), 1);
  const go = d.getElementById("smGo");
  const blank = d.querySelector(".sm-blank");
  const seen = new Set();
  for (let i = 0; i < 60; i++) {
    go.dispatchEvent(new window.Event("click"));
    seen.add(blank.textContent);
  }
  check(seen.size === 1, `sampler: K=1 should always give the same word, got ${[...seen].join("/")}`);
}

console.log(fail.length
  ? "FAIL\n - " + fail.join("\n - ")
  : `theme / jsonld / fonts / 404 / contact / tally / stamp / readability / resource / sampler clean (${checks} checks)`);
process.exit(fail.length ? 1 : 0);
