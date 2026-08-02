from rough import R, T, box

def wrap(name, W, H, body, aria):
    open(name + ".svg", "w").write(
        '<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="%s">%s</svg>' % (W, H, aria, "".join(body)))

# ═════════════════ document review (certification) ═════════════════
r = R(31); s = []
W, H = 760, 260
s.append(box(r, 20, 92, 96, 50, "documents", "uploaded"))
s.append(box(r, 156, 92, 92, 50, "classify"))
s.append(box(r, 288, 92, 92, 50, "extract"))
for a, b in [(116, 156), (248, 288)]:
    s.append(r.arrow(a, 117, b - 5, 117, 1.6))

# the barrier
s.append(r.line(420, 40, 420, 208, 2.0, "var(--amber)", 2, 1.0, "7 6"))
s.append(T(420, 30, "all extracted?", "da"))
s.append(T(420, 224, "one transaction, fires once", "da"))
s.append(r.arrow(380, 117, 414, 117, 1.6))

s.append(box(r, 452, 62, 96, 46, "verify", tint="var(--teal)"))
s.append(box(r, 452, 126, 96, 46, "cross-check", tint="var(--teal)"))
s.append(r.arrow(426, 112, 448, 88, 1.6))
s.append(r.arrow(426, 122, 448, 146, 1.6))
s.append(box(r, 604, 92, 130, 50, "officer decides", "pass / warn / fail"))
s.append(r.arrow(548, 88, 600, 112, 1.6))
s.append(r.arrow(548, 148, 600, 124, 1.6))

# watchdog loop
s.append(r.line(200, 196, 560, 196, 1.3, "var(--ink)", 2, 1.0, "2 6", .4))
s.append(r.arrow(560, 196, 560, 150, 1.3, "var(--ink)", 6, "2 6", .4))
s.append(r.line(200, 196, 200, 148, 1.3, "var(--ink)", 2, 1.0, "2 6", .4))
s.append(T(380, 190, "watchdog sweeps up anything that stalled", "dc"))
s.append(T(650, 44, "the model never", "dh"))
s.append(T(650, 62, "gets the last word", "dh"))
wrap("certify", W, H, s,
     "Sketch of a document review pipeline: documents are classified then extracted, then a dashed "
     "barrier marked all extracted, one transaction fires once, after which verify and "
     "cross-check run and an officer decides. A dashed watchdog loop sweeps up stalled work.")

# ═════════════════ compliance review (AML/CFT) ═════════════════════
r = R(47); s = []
W, H = 760, 246
s.append(box(r, 20, 96, 100, 52, "evidence", "uploaded"))
s.append(box(r, 158, 96, 96, 52, "extract", "per schema"))
s.append(r.arrow(120, 122, 152, 122, 1.6))
s.append(r.arrow(254, 122, 292, 96, 1.6))
s.append(r.arrow(254, 122, 292, 152, 1.6))

s.append(box(r, 300, 62, 152, 50, "LLM judgement", "reads, proposes"))
s.append(box(r, 300, 132, 152, 50, "rule-book check", "deterministic", tint="var(--teal)"))
s.append(T(376, 44, "two tracks, same rule", "dh"))

s.append(r.arrow(452, 88, 498, 112, 1.6))
s.append(r.arrow(452, 158, 498, 132, 1.6))
s.append(box(r, 506, 96, 128, 52, "finding", "+ evidence + clause"))
s.append(r.arrow(634, 122, 668, 122, 1.6))
s.append(box(r, 672, 96, 72, 52, "officer", "signs off"))
s.append(r.curly(296, 66, 178))
s.append(T(376, 208, "severity is stamped from the rule book — never inferred", "dc"))
wrap("comply", W, H, s,
     "Sketch of a compliance review engine: uploaded evidence is extracted per schema, then each "
     "rule runs down two tracks at once, an LLM judgement track and a deterministic rule-book "
     "check, which merge into a finding carrying its evidence and clause for officer sign-off.")

# ═════════════════ vulnerability remediation ══════════════════════
r = R(59); s = []
W, H = 760, 300
for i, lab in enumerate(["GitLab", "AWS", "CI"]):
    s.append(box(r, 20, 30 + i * 58, 76, 42, lab))
    s.append(r.arrow(96, 51 + i * 58, 138, 118, 1.4, op=.75))
s.append(box(r, 142, 94, 104, 50, "de-dup", "+ risk score"))
s.append(r.arrow(246, 119, 282, 119, 1.6))
s.append(box(r, 286, 94, 88, 50, "analyse"))
s.append(r.arrow(374, 119, 410, 119, 1.6))
s.append(box(r, 414, 94, 88, 50, "approve", tint="var(--amber)"))
s.append(T(458, 82, "human, or low-risk policy", "da"))
s.append(r.arrow(502, 119, 540, 119, 1.6))
s.append(box(r, 544, 94, 92, 50, "fix branch"))
s.append(r.arrow(590, 144, 556, 176, 1.6))

# the test gate — a diamond
s.append(r.line(546, 180, 600, 214, 1.9))
s.append(r.line(600, 214, 546, 248, 1.9))
s.append(r.line(546, 248, 492, 214, 1.9))
s.append(r.line(492, 214, 546, 180, 1.9))
s.append(T(546, 218, "tests", "dl"))

s.append(r.arrow(600, 214, 656, 214, 1.6, "var(--teal)"))
s.append(T(628, 200, "pass", "dl"))
s.append(T(700, 210, "merge", "dl"))
s.append(T(700, 226, "request", "dl"))
s.append(r.arrow(492, 214, 418, 214, 1.6, "var(--ink)"))
s.append(T(456, 200, "fail", "dl"))
s.append(T(392, 240, "back to a human", "dc"))
s.append(T(210, 246, "nothing is pushed", "dh"))
s.append(T(210, 266, "until the tests are green", "dh"))
wrap("remediate", W, H, s,
     "Sketch of a vulnerability remediation pipeline: findings from GitLab, AWS and CI are "
     "de-duplicated and risk scored, then analysed, approved by a human or low-risk policy, "
     "and a fix branch is created. A test gate sends passing fixes to a merge request and "
     "failing ones back to a human.")

# ═════════════════ learning insight (early years) ═════════════════
r = R(73); s = []
W, H = 760, 262
s.append(box(r, 20, 88, 104, 54, "tracking", "spreadsheets"))
s.append(r.arrow(124, 115, 160, 115, 1.6))
s.append(box(r, 164, 88, 116, 54, "name resolver", tint="var(--amber)"))
s.append(r.line(170, 152, 274, 152, 1.3, "var(--amber)", 1, .9, op=.65))
for i in range(4):
    s.append(r.line(174 + i * 33, 152, 174 + i * 33, 160, 1.3, "var(--amber)", 1, .8, op=.65))
s.append(T(222, 178, "four strategies before it gives up", "da"))
s.append(box(r, 164, 16, 116, 44, "BigQuery", "curriculum"))
s.append(r.arrow(222, 60, 222, 84, 1.5, op=.6))
s.append(r.arrow(280, 115, 312, 115, 1.6))

s.append(r.rect(316, 74, 272, 82, 1.5, "var(--ink)", r=8, op=.4))
s.append(T(452, 66, "agent sequence", "dh"))
for i, lab in enumerate(["retrieve", "summarise", "evaluate"]):
    x = 330 + i * 84
    s.append(box(r, x, 92, 66, 46, lab))
    if i:
        s.append(r.arrow(x - 17, 115, x - 5, 115, 1.3))
s.append(r.arrow(588, 115, 616, 115, 1.6))
s.append(box(r, 620, 88, 124, 54, "per-child", "readiness insight", tint="var(--teal)"))
s.append(T(380, 226, "an unmatched row is a child with no insight", "dc"))
s.append(T(380, 244, "a mismatched one is worse", "dc"))
wrap("insight", W, H, s,
     "Sketch of a learning-insight pipeline: teacher tracking spreadsheets pass through a name "
     "resolver that tries four strategies, joined with BigQuery curriculum data, into an "
     "agent sequence of retrieve, summarise and evaluate, producing a per-child readiness insight.")

print("done")
