from rough import R, T, box, blob, bracket, tick, road

def esc(v):
    """escape a value destined for an XML attribute"""
    return (str(v).replace("&", "&amp;").replace("<", "&lt;")
                  .replace(">", "&gt;").replace('"', "&quot;"))

def wrap(name, W, H, body, aria):
    open(name + ".svg", "w").write(
        '<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="%s">%s</svg>' % (W, H, aria, "".join(body)))

# ══════════════════════ 1. CAREER TIMELINE ════════════════════════
r = R(101); s = []
W, H = 1000, 448
Y = 296
X0, X1 = 122, 878
def yx(year): return X0 + (year - 2016) * (X1 - X0) / 10.0

s.append(road(r, X0, X1, Y))

# phase brackets on top
for a, b, lab in [(2016, 2019, "research & NLP"),
                  (2019, 2023, "platform & product"),
                  (2023, 2026.4, "AI in production")]:
    s.append(bracket(r, yx(a), yx(b), 52, 9, "var(--ink)", 1.4, .38))
    s.append(T((yx(a) + yx(b)) / 2, 42, lab, "dh"))

roles = [
  (2016, "2016 — 2019", "Senior Programmer, R&D", "Integra Software", 108),
  (2019, "2019 — 2022", "Senior Product Engineer", "Logical Steps", 178),
  (2022, "2022 — 2023", "Team Lead (R&D)", "2359 Media", 108),
  (2023, "2023 — 2024", "Tech Lead", "NCS", 178),
  (2024, "2024 — 2026", "Senior Consultant", "NCS Gov+", 108),
  (2026, "2026 — now",  "Forward Deployed", "NCS AI Central", 178),
]
for year, when, title, org, ty in roles:
    x = yx(year)
    s.append(tick(r, x, Y, 7))
    s.append(r.ellipse(x, Y, 8.5, 8.5, 1.9))
    if year == 2026:
        s.append(r.hachure(x - 7, Y - 7, 14, 14, "var(--amber)", 4, .9, .8))
    s.append(r.line(x, Y - 10, min(max(x, 96), W - 96), ty + 26, 1.1, "var(--ink)", 1, .8, "2 5", .4))
    tx = min(max(x, 96), W - 96)
    s.append(T(tx, ty, when, "dm", "middle"))
    s.append(T(tx, ty + 17, title, "dl", "middle"))
    s.append(T(tx, ty + 32, org, "dt", "middle"))

# what changed, under the road
thread = [(2017.4, "custom NER, NMT,"), (2017.4, "a patent filing"),
          (2020.6, "conversational AI"), (2020.6, "search at scale"),
          (2023.4, "monolith → microservices,"), (2023.4, "national platforms"),
          (2025.4, "agentic AI officers"), (2025.4, "can defend")]
for i in range(0, len(thread), 2):
    x = yx(thread[i][0])
    s.append(T(x, 340, thread[i][1], "dc"))
    s.append(T(x, 356, thread[i + 1][1], "dc"))

# geography
s.append(bracket(r, X0, yx(2019) - 8, 396, 8, "var(--ink)", 1.4, .35))
s.append(T((X0 + yx(2019)) / 2, 418, "Puducherry, India", "dt"))
s.append(bracket(r, yx(2019) + 8, X1, 396, 8, "var(--ink)", 1.4, .35))
s.append(T((yx(2019) + X1) / 2, 418, "Singapore", "dt"))

wrap("career", W, H, s,
     "A hand-drawn career timeline from 2016 to 2026. Three phases: research and NLP at "
     "Integra Software in Puducherry, then platform and product work at Logical Steps and "
     "2359 Media in Singapore, then AI in production across three NCS roles ending as "
     "Forward Deployed at NCS AI Central.")

# ══════════════════════ 2. WHOLE-STACK CUTAWAY ════════════════════
r = R(211); s = []
W, H = 780, 430
# Deliberately capability-level, not product-level. Products change every year;
# these layers have not, and naming them is what a client can actually buy.
layers = [
  ("experience",             "the screen the person actually uses",
   None,          "Most AI work is judged here, by someone who never saw the prompt."),
  ("agents & orchestration", "retrieval, tools, memory, routing between models",
   "var(--teal)", "Which model, which tool, which order \u2014 and what happens when one is down."),
  ("evaluation & guardrails","offline harness, deterministic backstops, red-teaming",
   "var(--teal)", "You cannot improve what you cannot score, or defend what you cannot reproduce."),
  ("governance & compliance","policy, access, audit trail, data residency, explainability",
   "var(--amber)","In a regulated domain this is not a phase at the end. It is a design constraint."),
  ("data & integration",     "one record, many systems that never agreed on it",
   None,          "Fragmented operations rarely have a storage problem. They have a truth problem."),
  ("platform & delivery",    "infrastructure as code, CI/CD, observability, cost",
   None,          "The bill and the pager both arrive after go-live. Design for both."),
]
LX, LW, LH, TOP, GAP = 176, 452, 54, 26, 8
for i, (lab, sub, tint, note) in enumerate(layers):
    y = TOP + i * (LH + GAP)
    g = []
    if tint:
        g.append(r.hachure(LX + 4, y + 4, LW - 8, LH - 8, tint, 9, .9, .22))
    g.append(r.rect(LX, y, LW, LH, 1.8, "var(--ink)", r=6))
    g.append(T(LX + 20, y + 23, lab, "dl", "start"))
    g.append(T(LX + 20, y + 39, sub, "ds", "start"))
    s.append('<g class="lyr" tabindex="0" role="button" data-note="%s" '
             'aria-label="%s. %s">%s</g>'
             % (esc(note), esc(lab), esc(note), "".join(g)))

BOT = TOP + len(layers) * (LH + GAP) - GAP
# left brace: one pair of hands
s.append(r.line(154, TOP + 2, 154, BOT - 2, 1.6, "var(--ink)", 2, 1.0, op=.5))
s.append(r.line(154, TOP + 2, 164, TOP + 2, 1.4, op=.5))
s.append(r.line(154, BOT - 2, 164, BOT - 2, 1.4, op=.5))
mid = (TOP + BOT) / 2
s.append('<text x="118" y="%d" class="dh" text-anchor="middle" '
         'transform="rotate(-90 118 %d)">one pair of hands</text>' % (mid, mid))

# right: the seams a project usually hands off at
for i in range(len(layers) - 1):
    y = TOP + i * (LH + GAP) + LH + GAP / 2
    s.append(r.line(LX + LW - 40, y, LX + LW + 54, y, 1.2, "var(--ink)", 1, .9, "3 5", .38))
for k, line in enumerate(["where a", "project", "usually", "hands off"]):
    s.append(T(LX + LW + 62, mid - 24 + k * 15, line, "dc", "start"))

wrap("stack", W, H, s,
     "A cutaway of six layers, all owned by one person: experience, agents and orchestration, "
     "evaluation and guardrails, governance and compliance, data and integration, and platform "
     "and delivery. Dashed lines on the right mark the seams where a project usually hands off "
     "between teams.")

# ══════════════════════ 3. DOMAIN MAP ═════════════════════════════
r = R(307); s = []
W, H = 760, 400
doms = [("publishing & NLP", "iNLP, iAuthor", 158, 132, 118, 78, None),
        ("fintech", "LNDDO, CardsPe", 352, 108, 96, 66, None),
        ("GovTech", "FWMOMCare, Exit Pass", 566, 138, 116, 76, "var(--teal)"),
        ("RegTech", "certification, AML/CFT", 250, 262, 112, 74, "var(--amber)"),
        ("EdTech", "early years, gig work", 452, 268, 104, 70, None),
        ("DevSecOps", "remediation", 638, 268, 92, 62, None)]
for lab, ex, cx, cy, rx, ry, tint in doms:
    if tint:
        s.append(r.hachure(cx - rx * .68, cy - ry * .6, rx * 1.36, ry * 1.2, tint, 10, .85, .2))
    s.append(blob(r, cx, cy, rx, ry, 1.8, "var(--ink)", 2, .085))
    s.append(T(cx, cy - 2, lab, "dl"))
    s.append(T(cx, cy + 15, ex, "ds"))
s.append(T(392, 366, "different industries, the same underlying problem:", "dc"))
s.append(T(392, 382, "high-consequence decisions buried in documents", "dc"))
wrap("domains", W, H, s,
     "Six overlapping hand-drawn regions showing the sectors worked in: publishing and NLP, "
     "fintech, GovTech, RegTech, EdTech and DevSecOps, each with example projects. The shared "
     "problem across all of them is high-consequence decisions buried in documents.")

# ══════════════════════ 4. SKILLS CONSTELLATION ═══════════════════
r = R(409); s = []
W, H = 960, 372
clusters = [
 ("AI & LLM", 128, 118, 100, 76, "var(--teal)",
  ["Claude", "Gemini", "Vertex Agent", "MCP", "RAG", "agentic"]),
 ("languages", 330, 92, 92, 66, None,
  ["TypeScript", "Python", "Go", "Node", "C#"]),
 ("cloud", 522, 118, 88, 68, None,
  ["GCP", "Firebase", "AWS", "Cloud Run", "Docker", "K8s"]),
 ("data", 716, 92, 84, 62, None,
  ["Postgres", "Firestore", "BigQuery", "Pub/Sub"]),
 ("front end", 232, 276, 88, 62, None,
  ["React", "Next.js", "Tailwind"]),
 ("hardening", 468, 278, 100, 68, "var(--amber)",
  ["RBAC", "audit", "secrets", "rate limits", "redaction"]),
 ("delivery", 716, 274, 86, 60, None,
  ["CI/CD", "Terraform", "handover"]),
]
pos = {}
for lab, cx, cy, rx, ry, tint, items in clusters:
    if tint:
        s.append(r.hachure(cx - rx * .7, cy - ry * .6, rx * 1.4, ry * 1.2, tint, 11, .85, .18))
    s.append(blob(r, cx, cy, rx, ry, 1.7, "var(--ink)", 2, .075))
    pos[lab] = (cx, cy)
    n = len(items)
    for i, it in enumerate(items):
        row = i - (n - 1) / 2.0
        s.append(T(cx, cy + row * 14 + 4, it, "ds"))
    s.append(T(cx, cy - ry - 10, lab, "dh"))
link = [("AI & LLM", "languages"), ("languages", "cloud"), ("cloud", "data"),
        ("AI & LLM", "front end"), ("front end", "hardening"),
        ("hardening", "cloud"), ("hardening", "delivery"), ("delivery", "data")]
for a, b in link:
    (x1, y1), (x2, y2) = pos[a], pos[b]
    s.append(r.line(x1, y1, x2, y2, 1.1, "var(--ink)", 1, .9, "2 6", .18))
wrap("skills", W, H, s,
     "A sketched constellation of seven skill clusters joined by faint lines: AI and LLM, "
     "languages, cloud, data, front end, hardening and delivery, each listing the specific "
     "tools within it.")
print("done")
