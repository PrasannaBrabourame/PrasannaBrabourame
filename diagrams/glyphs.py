"""Three tiny marks, one per principle in the gap section."""
from rough import R, chain

def wrap(name, body, label):
    open(name + ".svg", "w").write(
        '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">%s</svg>'
        % "".join(body))

# 1. a stamp coming down on a page — the rule book, not the model
r = R(61); s = []
s.append(r.rect(8, 18, 22, 26, 1.7, "var(--ink)", r=2))
s.append(r.line(13, 26, 25, 26, 1.2, op=.5)); s.append(r.line(13, 32, 25, 32, 1.2, op=.5))
s.append(r.line(13, 38, 21, 38, 1.2, op=.5))
s.append(r.rect(26, 6, 16, 9, 1.7, "var(--amber)", r=2))
s.append(r.line(34, 15, 34, 21, 1.7, "var(--amber)", 2))
s.append(r.line(28, 21, 40, 21, 2.0, "var(--amber)", 2))
wrap("g-stamp", s, "")

# 2. a brace that broke — malformed output
r = R(83); s = []
s.append(chain(r, [(30,8),(18,14),(20,22),(12,24)], 2.0, "var(--ink)", .9))
s.append(chain(r, [(12,24),(20,26),(18,34),(30,40)], 2.0, "var(--ink)", .9))
s.append(r.line(34, 16, 42, 24, 1.8, "var(--amber)", 2))
s.append(r.line(42, 16, 34, 24, 1.8, "var(--amber)", 2))
s.append(r.line(34, 32, 41, 32, 1.4, op=.45))
wrap("g-brace", s, "")

# 3. an eye that sweeps — the watchdog
r = R(107); s = []
s.append(chain(r, [(6,26),(16,14),(30,12),(42,24)], 1.8, "var(--ink)", .9))
s.append(chain(r, [(42,24),(30,36),(16,34),(6,26)], 1.8, "var(--ink)", .9))
s.append(r.ellipse(24, 24, 7, 7, 1.7, "var(--teal)", 2))
s.append(r.ellipse(24, 24, 2.6, 2.6, 2.2, "var(--teal)", 1))
s.append(r.line(4, 40, 44, 40, 1.2, "var(--ink)", 1, .9, "2 4", .5))
wrap("g-eye", s, "")
print("glyphs written")
