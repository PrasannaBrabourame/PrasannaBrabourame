from rough import R, T, bracket

r = R(881)
W, H = 840, 330
BASE = 236
s = []

# Google Cloud skill badges earned per month in 2026, from the public profile
MONTHS = [("Feb", 13, "var(--teal)"), ("Mar", 5, "var(--teal)"),
          ("Jun", 5, "var(--amber)"), ("Jul", 15, "var(--amber)")]
MAX, BW, GAP, X0 = 15, 84, 62, 132
UNIT = 150.0 / MAX

s.append(r.line(X0 - 40, BASE, X0 + 4 * BW + 3 * GAP + 36, BASE, 1.8, "var(--ink)", 2, .9))

for i, (m, n, col) in enumerate(MONTHS):
    x = X0 + i * (BW + GAP)
    h = n * UNIT
    s.append(r.hachure(x + 4, BASE - h + 4, BW - 8, h - 8, col, 8, .9, .30))
    s.append(r.rect(x, BASE - h, BW, h, 1.8, "var(--ink)", r=5))
    s.append(T(x + BW / 2, BASE - h - 12, str(n), "dl"))
    s.append(T(x + BW / 2, BASE + 22, m, "dl"))

s.append(T(X0 + 4 * BW + 3 * GAP + 4, BASE + 22, "2026", "dc", "start"))

# what changed between the two halves
a1, a2 = X0 - 8, X0 + BW + GAP + BW + 8
b1, b2 = X0 + 2 * (BW + GAP) - 8, X0 + 3 * (BW + GAP) + BW + 8
s.append(bracket(r, a1, a2, BASE + 44, 9, "var(--teal)", 1.4, .55))
s.append(T((a1 + a2) / 2, BASE + 74, "search, data stores,", "dt"))
s.append(T((a1 + a2) / 2, BASE + 90, "enterprise assistants", "dt"))
s.append(bracket(r, b1, b2, BASE + 44, 9, "var(--amber)", 1.4, .55))
s.append(T((b1 + b2) / 2, BASE + 74, "agents, tools, memory,", "da"))
s.append(T((b1 + b2) / 2, BASE + 90, "guardrails, evaluation", "da"))

s.append(T(420, 34, "the count is not the point — the subject changed", "dh"))
s.append(T(420, 56, "Google Cloud skill badges earned per month", "dc"))

open("learning.svg", "w").write(
    '<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="A bar chart of Google Cloud skill badges earned per month in 2026: '
    'thirteen in February, five in March, five in June, fifteen in July. The first two '
    'months were search, data stores and enterprise assistants; the last two were agents, '
    'tools, memory, guardrails and evaluation.">%s</svg>' % (W, H, "".join(s)))
print("learning.svg written")
