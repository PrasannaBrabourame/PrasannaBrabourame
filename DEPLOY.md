# prasannabrabourame.com — deploy notes

Single-page profile site. One self-contained HTML file, no build step, no dependencies.

## Files

`index.html` is **generated**. Edit `template.html`, then run `python3 build.py`.

| File | Purpose |
|---|---|
| `template.html` | The source — HTML, CSS and JS, with `{{SVG:name}}` placeholders |
| `build.py` | Injects `diagrams/*.svg` into the placeholders → `index.html` |
| `index.html` | The built markup, one self-contained file (280 KB raw, ~60 KB gzipped) |
| `diagrams/` | Sketch engine and generated SVGs |
| `img/` | The hero illustration, 2 widths × webp + jpg |
| `og.jpg` | Social share card, 1200×630 |
| `robots.txt` | Crawler policy + sitemap pointer |
| `sitemap.xml` | Single URL entry |

**One raster image: the hero illustration.** Everything else — the logo mark, nine diagrams,
the paper grain, the section rules, the favicon, the walking figures — is inline SVG or ASCII.
The page is ~60 KB gzipped plus one 43 KB illustration and three Google Font files.

## Publishing

See `PUBLISH.md`. Short version: there is no CI. `./publish.sh` regenerates the drawings,
builds `docs/`, and runs the tests; you commit `docs/` and GitHub Pages serves it from
`main /docs`.

`build.py` writes `docs/index.html`, `docs/robots.txt`, `docs/sitemap.xml` and
`docs/.nojekyll`, and copies `img/` and `og.jpg` in. The canonical URL comes from the
`SITE_URL` environment variable and appears in exactly one place in the source —
`{{SITE_URL}}` in `template.html`.

**`.nojekyll` matters.** On a branch deploy GitHub runs Jekyll, which would read the
thirteen `{{SVG:...}}` placeholders in `template.html` as Liquid tags and fail. Pointing
Pages at `docs/` keeps the template out of reach anyway, and the marker makes it certain.

**The source photographs are not in the repo.** `diagrams/hero.py` and `diagrams/trace.py`
read them from `../../source-art/`, and `.gitignore` excludes `diagrams/*-source.png`. One
of them is the original crowd photograph and still contains the other person — that is why
it stays off the web. The generated artwork is committed, so a normal build never needs them.

## Accessibility and performance notes

- Skip link, single `<h1>`, ordered headings, labelled form fields, `aria-live` status.
- `prefers-reduced-motion` disables every animation including the orbiting mark.
- Mobile nav is a real focus-trappable drawer with Escape to close.
- Print stylesheet flattens the dark contact section and reveals hidden content.
- No `localStorage`, no cookies, no third-party scripts. Only Google Fonts is external.

## The diagrams

Thirteen hand-drawn sketches (ten diagrams and three small glyphs), all inline SVG — no image files, nothing to load.

**Four experience diagrams** — the career, drawn:

| Diagram | Where | Source |
|---|---|---|
| Career timeline, 2016→2026 | top of Track record, above the written roles | `exp.py` |
| Whole-stack cutaway (interactive) | How I work | `exp.py` |
| Domain / sector map | Track record, below the roles | `exp.py` |
| Skills constellation | Capabilities | `exp.py` |

**Six flow diagrams** — the systems, drawn:

| Diagram | Where | Source |
|---|---|---|
| Scenario explorer (interactive) | "Most AI projects don't fail at the model" | `reality.py` |
| Two-phase barrier | `certify` case note | `cases.py` |
| Dual-track evaluation | `comply` case note | `cases.py` |
| Test gate | `remediate` case note | `cases.py` |
| Three tiers | `insight` case note | `cases.py` |
| Learning cadence | Certification & continuous learning | `learn.py` |

They are generated, not drawn by hand in an editor. `diagrams/` holds the source:

```
cd diagrams
python3 reality.py && python3 cases.py && python3 exp.py && python3 learn.py && python3 glyphs.py
python3 render.py career stack domains skills reality certify comply remediate insight learning
```

`rough.py` is the sketch engine — wobbly lines, rects, ellipses, arrows and hachure fills,
seeded so output is identical every run. Change a seed (`R(31)`) to reshuffle the wobble.

**To edit a diagram:** change the coordinates in `gap.py` / `cases.py` / `exp.py`, regenerate, then
re-inline the `.svg` contents into `index.html` inside the matching
`<figure class="sketch">`. Keep the `class="sk"`, `role="img"` and `aria-label` attributes —
the label is what a screen reader announces in place of the picture.

Colours come from the page, not the SVG: strokes use `var(--ink)`, `var(--teal)` and
`var(--amber)`, so the diagrams re-tint automatically if you change the palette.
Below 680px they scroll horizontally rather than shrinking into illegibility.

`rough.py` also carries `blob`, `bracket`, `tick` and `road` for the experience diagrams, and
a Catmull-Rom smoother so the sketched loops read as hand-drawn rather than polygonal.

Page weight with all nine: **228 KB raw, ~48 KB gzipped.** Every static host gzips by default.

**One editorial note:** the career timeline now carries the Track record section, with the
written roles underneath as detail. If you ever trim the page, trim the prose — not the
timeline; it is the thing people look at first.


## Confidentiality

**No client agency and no product name appears anywhere in this site** — not in the copy, not in
a diagram, not in an `aria-label`, not in a filename, not in an HTML comment. The four AI case
notes are described by sector and shape only:

| Case note | Sector shown |
|---|---|
| Certification document review | National certification authority · Singapore |
| Regulatory compliance review | AML/CFT compliance · Singapore |
| Vulnerability remediation pipeline | DevSecOps · vulnerability remediation |
| Early-years learning insight | Early-childhood education · Singapore |

The Work section says so out loud — *"Clients, product names and figures are withheld. What
follows is the shape of each problem and how it was solved, which is the part that transfers
anyway."* Discretion reads as a professional signal rather than a gap, which is the point.

Older projects that are already public on your LinkedIn (FWMOMCare, Exit Pass, the Ola suite,
iNLP, LNDDO, CardsPe, NUS IASS) are still named — they are not confidential. Move them behind
the same wall if you'd rather.

`test-confidentiality.mjs` enforces this: it fails the build if any of `MUIS`, `ACRA`, `halal`,
`HIVA`, `ComplAI`, `SecWiz`, `LighTool` or `Corporate Service Provider` reappears in the page or
in any accessible label. **Run it before you publish, and after any edit to the case notes.**

## The hero illustration

`img/hero-illustration*.{webp,jpg}` — the pencil-and-watercolour portrait beside the headline.
Generated from `diagrams/hero-source.png` by `diagrams/hero.py`:

```
cd diagrams && python3 hero.py
```

**What it does to the original.** The source art was blue and purple. `hero.py` remaps hue by
band — 178-244° (the blues) onto the site teal, 244-292° (the purples) onto the site amber —
leaves skin tones alone, lifts saturation, and deepens the value slightly so the washes read at
the same weight as `--teal` and `--amber` elsewhere on the page. Change those two `seg()` calls
if you ever change the palette.

**Why there's no alpha channel.** The white background is keyed out, then re-composited onto the
paper colour rather than left transparent. Keeping alpha cost 196 KB against 41 KB for a result
nobody can distinguish — the paper behind it is the same colour either way. The `<img>` also
carries `mix-blend-mode:multiply`, so it sits *on* the paper grain instead of on a white card.

**Served responsively.** `<picture>` offers webp first with a jpg fallback, each at 620 and
1180 wide, with `sizes` so a phone never downloads the 2x file. Intrinsic `width`/`height` are
set, so the page doesn't jump while it loads.

| File | Size |
|---|---|
| `hero-illustration.webp` | 43 KB |
| `hero-illustration@2x.webp` | 124 KB |
| `hero-illustration.jpg` (fallback) | 65 KB |
| `hero-illustration@2x.jpg` | 197 KB |

`og.jpg` is built from the same illustration so a shared link looks like the page.

**The earlier traced portrait** is still in `diagrams/portrait.svg`, with its tracing script at
`diagrams/trace.py`. It is no longer used. Delete both if you're sure, or drop the SVG back into
the template with a `{{SVG:portrait}}` placeholder if you want it somewhere else.

## The strip

Directly under the hero, a small ASCII engineer walks a sketched ground line and stops to do
the things this page is about:

| Action | What you see | Bubble |
|---|---|---|
| `deploy` | sets something down that builds itself: `.` → `o` → `[]` → `[#]` | (deploying) → (live) |
| `dog` | leaves a sentinel that blinks `[..]` / `[oo]` for as long as it lives | (setting a watchdog) → (it will notice) |
| `test` | types, throws sparks, leaves a `v` | (running the suite) → (green) |
| `katch` | a malformed response — `{"sev`, ```` ```json ```` — falls in; he reaches up, catches it, leaves `ok` | (incoming…) → (caught it) |

Between jobs he mutters: *(what is actually in the way?)*, *(the demo worked. now the hard
part)*, *(this one needs a backstop)*, *(who gets paged at 2am?)*, *(ship it, then harden it)*.

It is purely decorative — `aria-hidden`, so no screen reader ever meets it — and it is **off**
entirely under `prefers-reduced-motion`. Unlike the reference implementation it also stops when
scrolled out of view and when the tab is in the background, so it costs nothing while unread.

To change what he does: the actions are picked in `pickAction()` (weights are the `r <` cut-offs),
and each one's animation lives in the `frame()` branch of the same name. Frames are 5-row ASCII
arrays; `mirror()` flips them when he walks left, so only draw him facing right.

## The interactive bits

**Diagrams draw themselves.** Each sketch animates `stroke-dashoffset` as it scrolls into
view, so the line work appears as though someone is drawing it. Hachure fills are texture
rather than line work, so they fade in as a group; dashed guide lines keep their pattern and
fade via `stroke-opacity`. The flourish is capped at ~1.2s per diagram however many strokes
it contains.

All of it is gated behind an `.anim` class that JavaScript adds at runtime — so with JS off,
or with `prefers-reduced-motion` set, every diagram simply renders complete. That's tested,
not assumed.

**The self-check** (`#ready`) asks five questions one at a time, each answer producing a short
reflection rather than a score, and closes with one of three summaries depending on how the
answers fell. There's a `<noscript>` paragraph carrying the gist for anyone without JS.

To change the questions, edit the `QUESTIONS` array in `template.html` — each option is
`[label, weight 0-2, reflection]`. The three closing summaries are in `CLOSE`, keyed by score
band out of 10. Add or remove questions freely; the bands are the only thing to keep in step.

**Little actors.** One ticker at ~11fps drives every ASCII figure: a *pacer* who walks the
career timeline and pauses at each role to say what happened there, and a small *worker* beside
each case note doing that project's job — stamping and checking, weighing two tracks, fixing then
testing, reading then seeing. Actors only tick while on screen, and the whole set is absent under
`prefers-reduced-motion`. Frames live in the `WORKERS` map and the pacer's stops in `STOPS`,
whose percentages match the drawn tick marks on the timeline — **if you move a station in
`exp.py`, move its percentage too.**

**Marginalia.** Three handwritten asides (`.marg`) in Caveat, plus the signature in the contact
block. Keep it to three — the restraint is what stops it reading as decoration.

**Paper.** A tiled `feTurbulence` grain over the whole page at low opacity, and a hand-drawn
rule as the top border of every section instead of a 1px line. Both are inline data URIs;
together they cost under 700 bytes.

## Tests

```
npm install jsdom
node test-page.mjs             # reveals, quiz, diagram drawing
node test-reduced-motion.mjs   # everything must switch itself off
node test-walk-strip.mjs       # the walker
node test-ambient.mjs          # cursor wash, living mark, no stray canvas
node test-confidentiality.mjs  # no client or product name, hero art, actors
```

106 assertions in total. Between them they check that the quiz advances, guards against
double-answers, resets, and picks the right closing text for both a top and a bottom score;
that diagram strokes are hidden before scroll and drawn after, with hachure excluded; that the
walker stays inside its stage, pauses off-screen, resumes on return, and leaks neither DOM nodes
nor timers over 12,000 frames; and that every animation disables itself under
`prefers-reduced-motion`.

`test-ambient.mjs` additionally proves the canvas is cleared every frame (otherwise the lines
smear), that the orbiting dot never leaves its ring across 400 frames, that the crossing fires
and clears itself, that 26 rapid clicks leave zero ring elements behind, that touch input spawns
nothing, and that a browser with no 2d context is left with no empty holder div.

`test-walk-strip.mjs`, `test-ambient.mjs` and `test-confidentiality.mjs` run a virtual clock —
frames and timers advance together — so the cleanup assertions are real rather than vacuous.

**A note on the leak assertions.** They check that pending timers stay *bounded*, not that they
never grow. Timers legitimately rise and fall: footprints live 5 seconds, ground marks up to 70.
Measured over 576 virtual seconds the walker holds 9-23 pending timers and 0-4 repeating
intervals, so the thresholds are 60 and 12. A monotonic climb in the interval count is the real
signal that a `clearInterval` has stopped firing.


## Certification & continuous learning

`#learning`, between Capabilities and the self-check. Figures come from the two public
profiles and are checked by `test-confidentiality.mjs` — **if you re-fetch either profile,
update the numbers in `template.html` and the expectations in the test together.**

| Claim on the page | Source |
|---|---|
| Diamond League, 13,895 points, 38 skill badges in 2026 | skills.google public profile |
| 15 verified badges — Google Cloud, AWS, IBM, back to 2019 | credly.com badges API |
| The Anthropic certificate list | your LinkedIn export |

`learn.py` draws the cadence chart from the badge dates: 13 in February, 5 in March, 5 in
June, 15 in July. The bars are deliberately annotated with *what* changed rather than just how
many — February and March were search, data stores and enterprise assistants; June and July
were agents, tools, memory, guardrails and evaluation. That shift is the argument; the count
is not.

**One thing the page deliberately does not claim.** Credly's API returns strings like
"Professional Cloud Architect Certification" and "Associate Cloud Engineer Certification" —
but only inside each badge's *recommended next* list. They are suggestions, not credentials you
hold. The test asserts none of them appears on the page. Don't add them by hand later.

## Two bugs fixed in this pass

**The top nav was invisible.** `.masthead` sat at `z-index:30` and painted a translucent
gradient across the full width; `.nav` was a *separate* fixed element at `z-index:29`, so the
gradient covered the links. The nav is now a flex child of the masthead, sharing one stacking
context with the gradient behind both. On mobile it still becomes a fixed drawer, with the
toggle raised above it. Tested.

**The hero illustration looked like a box.** The `<img>` uses `mix-blend-mode:multiply`, but
the file had been composited onto the paper colour — and paper multiplied by paper is darker
than paper, which drew a rectangle. It is now composited onto pure white, so white × paper =
paper exactly and the edge disappears. `hero.py` also feathers the outer 3%. Verified
numerically: the corners now multiply to the paper colour with zero deviation.


## The explorable stack

The "how I work" cutaway is the one diagram you can poke. Each of its six layers is a
`<g class="lyr">` carrying `tabindex="0"`, an `aria-label` and a `data-note`; hovering, clicking
or tabbing to one prints its note underneath in an `aria-live` region. It is not an animation,
so it stays available under `prefers-reduced-motion` and works from the keyboard.

**The layers are capability-level on purpose.** They used to name products — React, Firestore,
Terraform — which dates the page and describes the wrong thing. A client is not buying Firestore.
The layers are now:

| Layer | Note shown |
|---|---|
| experience | Most AI work is judged here, by someone who never saw the prompt. |
| agents & orchestration | Which model, which tool, which order — and what happens when one is down. |
| evaluation & guardrails | You cannot improve what you cannot score, or defend what you cannot reproduce. |
| governance & compliance | In a regulated domain this is not a phase at the end. It is a design constraint. |
| data & integration | Fragmented operations rarely have a storage problem. They have a truth problem. |
| platform & delivery | The bill and the pager both arrive after go-live. Design for both. |

The specific tools still appear once, in **Capabilities** — which is where a reader goes looking
for them. `test-confidentiality.mjs` asserts no product name creeps back into the stack diagram,
and that it keeps mentioning governance, guardrails, evaluation, observability and the harness.

**Two layout fixes in this pass.** The timeline pacer was attached to the whole `<figure>` at
`bottom:0`, so he stood on top of the caption; he is now a child of `.sk-scroll` positioned at
`calc(66% - 54px)` — 66% being where the road is drawn — so he walks the road and cannot reach
the caption. And the Certification section and How I work section each gained a worker, so all
six `data-actor` slots are now filled: `certify`, `comply`, `remediate`, `insight`, `how`, `learn`.


## The scenario explorer

The section that opens "Most AI projects don't fail at the model" carries `reality.svg` and a row
of nine chips. It was a two-state demo/production toggle; a binary turned out to be too small for
the argument.

**The pipeline is drawn once** — request → input guard → orchestrator (plan, route, retry) →
model → output guard → answer → audit trail, with allow-listed tools, a cited vector store and
scoped memory hanging off the orchestrator. That base group is always visible.

**Nine overlays sit on top of it** as sibling `<g class="sc {key}">` groups. Each marks where
production strikes and, in teal, what catches it. The prose lives in HTML rather than inside the
SVG — easier to edit, and a screen reader gets it from an `aria-live` region instead of from a
picture.

| Chip | Strikes | Caught by |
|---|---|---|
| as a demo | — | one path, one time, in front of an audience |
| 429 & cold start | scale · serverless | backoff with jitter, a queue that holds order, a warm path |
| malformed output | schema | strict schema, layered salvage, deterministic fallback |
| prompt injection | guardrails | provenance per chunk, tool allow-list, output policy |
| context blowout | optimisation | token budget, reranking, rolling summarisation, deliberate eviction |
| memory drift | agent state | state scoped to a conversation, a TTL that expires, replayable sessions |
| data leakage | residency | redaction before the call, field-level controls, residency at the boundary |
| cost at scale | routing | route easy work to a smaller model, cache the deterministic, cap the budget |
| "why did it decide that?" | governance | decision trace keeping rule, evidence, proposal and override |

**Keyboard.** Left and right arrows walk the chip row and switch as they go, the way a real
toolbar behaves. Each chip is a `<button>` carrying `aria-pressed`.

**Without JavaScript** every overlay renders at once — busy, but legible, which beats a blank box.

**If you add a scenario, add all three parts** or the tests will fail: a `SCEN` entry in
`reality.py`, a chip, and a note. `test-confidentiality.mjs` checks that every chip has a matching
overlay *and* a matching note, that exactly one of each is ever showing, and that the section
still covers orchestration, serverless, guardrails, vectors, memory, injection, residency, audit,
token budget and allow-listing.
