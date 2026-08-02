"""One agent pipeline, and the eight ways production tests it.

The base architecture is drawn once. Each scenario is an overlay group the
page can switch on: a strike where it lands, and the thing that catches it.
"""
from rough import R, T, box, chain

r = R(1301)
W, H = 1000, 392
Y, BH = 112, 58          # the request path
Y2, BH2 = 250, 46        # what the orchestrator reaches for
s = []

def esc(v):
    return (str(v).replace("&", "&amp;").replace("<", "&lt;")
                  .replace(">", "&gt;").replace('"', "&quot;"))

def bolt(x, y, col="var(--amber)"):
    return chain(r, [(x, y), (x - 9, y + 17), (x + 5, y + 17), (x - 7, y + 38)],
                 2.1, col, .95)

def lines(x, y, rows, cls="da", anchor="middle", dy=15):
    return "".join(T(x, y + i * dy, t, cls, anchor) for i, t in enumerate(rows))

# ══ the pipeline, always on ════════════════════════════════════════
NODES = [
    ("request",      30, 96,  None,               None),
    ("guard",        152, 96, "in · schema", None),
    ("orchestrator", 274, 132, "plan, route, retry", "var(--teal)"),
    ("model",        432, 120, None,               None),
    ("guard",        578, 96, "out · policy", None),
    ("answer",       700, 110, None,               None),
    ("audit",        836, 104, "decision trace",   "var(--amber)"),
]
base = []
prev = None
for lab, x, w, sub, tint in NODES:
    base.append(box(r, x, Y, w, BH, lab, sub, tint=tint))
    if prev is not None:
        base.append(r.arrow(prev, Y + BH / 2, x - 6, Y + BH / 2, 1.7))
    prev = x + w
CX = {lab + str(x): x + w / 2 for lab, x, w, _, _ in NODES}
MODEL, ORCH, GIN, GOUT, ANS, AUD, REQ = 492, 340, 200, 626, 755, 888, 78

SUB = [("tools", 274, 100, "allow-listed"),
       ("vector store", 392, 116, "cited, fresh"),
       ("memory", 526, 100, "scoped, TTL")]
for lab, x, w, sub in SUB:
    base.append(box(r, x, Y2, w, BH2, lab, sub))
    base.append(r.line(x + w / 2, Y2 - 4, 340, Y + BH + 4, 1.4, "var(--ink)", 2, 1.0, op=.45))
s.append('<g class="base">%s</g>' % "".join(base))

# ══ the naive reading ══════════════════════════════════════════════
d = []
d.append(r.ellipse(ANS, Y - 34, 17, 17, 1.8, "var(--teal)", 2))
d.append(chain(r, [(ANS - 7, Y - 33), (ANS - 1, Y - 27), (ANS + 8, Y - 42)], 2.0, "var(--teal)", .95))
d.append(T(ANS, Y - 58, "works", "dt"))
d.append(T(500, 42, "one path, one time, in front of an audience", "dh"))
s.append('<g class="sc demo">%s</g>' % "".join(d))

# ══ eight ways production tests it ═════════════════════════════════
SCEN = []

# scale · serverless
o = [bolt(MODEL, Y - 66),
     lines(MODEL + 24, Y - 58, ["429, and a cold start", "under real concurrency"], "da", "start"),
     T(ORCH, Y2 - 76, "backoff · queue · warm path", "dt")]
SCEN.append(("scale", "".join(o)))

# malformed output
o = [bolt(560, Y + BH + 6),
     lines(596, Y + BH + 30, ['fenced JSON, truncated array,', "a stray control character"], "da", "start"),
     T(400, Y + BH + 52, "schema · salvage · deterministic fallback", "dt")]
SCEN.append(("malformed", "".join(o)))

# prompt injection
o = [bolt(450, Y2 + BH2 + 6),
     lines(486, Y2 + BH2 + 30, ["a retrieved document that", "gives the agent instructions"], "da", "start"),
     T(250, Y2 + BH2 + 40, "provenance · tool allow-list", "dt"),
     T(250, Y2 + BH2 + 55, "· output policy", "dt")]
SCEN.append(("injection", "".join(o)))

# context
o = [bolt(ORCH, Y - 66),
     lines(ORCH + 24, Y - 58, ["the window fills with", "everything, ranked by nothing"], "da", "start"),
     T(ORCH, Y2 - 76, "budget · rerank · summarise · evict", "dt")]
SCEN.append(("context", "".join(o)))

# memory
o = [bolt(576, Y2 + BH2 + 6),
     lines(612, Y2 + BH2 + 30, ["yesterday's session leaking", "into today's answer"], "da", "start"),
     T(330, Y2 + BH2 + 48, "scoped state · TTL · replayable", "dt")]
SCEN.append(("memory", "".join(o)))

# leakage
o = [bolt(GOUT, Y - 66),
     lines(GOUT + 24, Y - 58, ["a name, an NRIC, a salary", "on its way out of the region"], "da", "start"),
     T(GOUT, Y + BH + 34, "redaction · field controls · residency", "dt")]
SCEN.append(("leakage", "".join(o)))

# cost
o = [bolt(MODEL, Y - 66, "var(--ink)"),
     lines(MODEL + 24, Y - 58, ["the bill arrives, and it is", "the same call ten thousand times"], "da", "start"),
     T(ORCH, Y2 - 76, "route to the small model · cache · cap", "dt")]
SCEN.append(("cost", "".join(o)))

# audit
o = [bolt(AUD, Y - 66),
     lines(AUD, Y - 96, ["“why did it decide that?”"], "da"),
     T(AUD, Y + BH + 34, "rule reference", "dt"),
     T(AUD, Y + BH + 49, "evidence · who overrode it", "dt")]
SCEN.append(("audit", "".join(o)))

for key, body in SCEN:
    s.append('<g class="sc %s">%s</g>' % (key, body))

open("reality.svg", "w").write(
    '<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="%s">%s</svg>' % (W, H, esc(
      "An agent pipeline: a request passes an input guard to an orchestrator that plans, routes "
      "and retries; the orchestrator reaches for allow-listed tools, a cited vector store and "
      "scoped memory; a model answers; an output guard applies policy; the answer is recorded in "
      "an audit trail. Switching scenarios marks where production strikes it and what catches it."),
      "".join(s)))
print("reality.svg — %d scenarios" % (len(SCEN) + 1))
