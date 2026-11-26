#!/usr/bin/env python3
"""One figure per section that needs one, each carrying that section's argument.

    python3 illusions.py

These are not decoration. Each figure restates the section's claim as a
picture a first-time reader can get without the caption:

  gap           Kanizsa triangle — a system you can see that nobody built
  capabilities  the same two bars, judged by eye and then measured
  learning      four quarters of tools; what came in, what got dropped
  ready         five questions, two boxes still empty, no score

Four, not seven. The Ebbinghaus, Necker, Müller-Lyer, Hermann grid and café
wall figures that used to sit on the other sections were tricks hunting for a
caption: a reader saw a puzzle, not the point. The sketches below those
sections already carry them, so the figures went.

Written with var(--ink), var(--teal), var(--amber) and var(--rule) and nothing
else, so they re-theme with the page like the other thirteen drawings. The
Kanizsa figure in particular depends on it: the triangle it suggests is made of
page colour, so it only works while the fill really is the page.
"""
import math, pathlib

OUT = pathlib.Path(__file__).parent
W, H = 300, 168                 # a compact band, not a full-width sketch

INK, TEAL, AMBER = "var(--ink)", "var(--teal)", "var(--amber)"
RULE = "var(--rule)"
FONT = 'font-family="DejaVu Sans, Helvetica, Arial, sans-serif"'


def svg(name, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{label}">\n  ' + "\n  ".join(body) + "\n</svg>\n")


def tick(x, y, s=9, color=TEAL, w=2.2):
    """A check mark whose bottom-left corner sits at (x, y)."""
    return (f'<path d="M {x} {y - s*0.45} L {x + s*0.4} {y} L {x + s} {y - s}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def qmark(x, y, size=14, color=INK, opacity=1):
    return (f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="600" '
            f'text-anchor="middle" fill="{color}" opacity="{opacity}">?</text>')


# ── gap: a triangle nobody drew ───────────────────────────────────────────
def kanizsa():
    cx, cy, r, disc, wedge = W / 2, H / 2, 54, 29, 60
    out = []
    for a in (-90, 30, 150):
        x = cx + r * math.cos(math.radians(a))
        y = cy + r * math.sin(math.radians(a))
        f = a + 180                                   # the gap faces the centre
        x0 = x + disc * math.cos(math.radians(f - wedge / 2))
        y0 = y + disc * math.sin(math.radians(f - wedge / 2))
        x1 = x + disc * math.cos(math.radians(f + wedge / 2))
        y1 = y + disc * math.sin(math.radians(f + wedge / 2))
        # large-arc=1 sweep=0 is the only pair that removes a wedge
        out.append(f'<path d="M {x:.1f} {y:.1f} L {x0:.1f} {y0:.1f} '
                   f'A {disc} {disc} 0 1 0 {x1:.1f} {y1:.1f} Z" fill="{INK}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.6" fill="{AMBER}"/>')
    return out, ("Three discs with a wedge cut from each. A bright triangle appears "
                 "between them although no triangle is drawn.")


# ── caps: measured, not judged ────────────────────────────────────────────
def measured():
    out = []
    bw, bh = 66, 18
    # left: judged by eye. Same bar, two grounds, and they do not look equal.
    lx = 18
    out.append(f'<rect x="{lx}" y="34" width="118" height="48" fill="{INK}" opacity="0.12"/>')
    out.append(f'<rect x="{lx}" y="90" width="118" height="48" fill="{INK}" opacity="0.6"/>')
    for y in (49, 105):
        out.append(f'<rect x="{lx + 26}" y="{y}" width="{bw}" height="{bh}" fill="{TEAL}"/>')
    out.append(qmark(lx + 59, 24, 15, AMBER))
    # right: measured. Same two bars on plain ground under a ruler.
    rx = 164
    for y in (49, 105):
        out.append(f'<rect x="{rx + 26}" y="{y}" width="{bw}" height="{bh}" fill="{TEAL}"/>')
    # guides from both bar ends down to the ruler
    for x in (rx + 26, rx + 26 + bw):
        out.append(f'<line x1="{x}" y1="46" x2="{x}" y2="150" stroke="{AMBER}" '
                   f'stroke-width="1.2" stroke-dasharray="3 3"/>')
    # the ruler
    ry = 150
    out.append(f'<line x1="{rx + 10}" y1="{ry}" x2="{rx + 108}" y2="{ry}" '
               f'stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>')
    for i in range(0, 11):
        x = rx + 10 + i * 9.8
        h = 7 if i % 5 == 0 else 4
        out.append(f'<line x1="{x:.1f}" y1="{ry}" x2="{x:.1f}" y2="{ry - h}" '
                   f'stroke="{INK}" stroke-width="1.3"/>')
    out.append(tick(rx + 54, 26, 10, TEAL))
    # a thin divider so the two halves read as "before / after"
    out.append(f'<line x1="150" y1="30" x2="150" y2="150" stroke="{RULE}" stroke-width="1"/>')
    return out, ("Two identical teal bars. On the left they sit on a light and a dark "
                 "ground and look different. On the right the same bars sit under a "
                 "ruler and are plainly equal.")


# ── learning: the tools change every quarter ──────────────────────────────
def quarters():
    out = []
    cols = (52, 117, 182, 247)
    tw, th, gap = 40, 13, 4
    base = 126
    # new-this-quarter (amber) vs carried over (teal) per quarter, bottom-up;
    # 'x' is a tool that was dropped that quarter, drawn as a dashed ghost
    plan = (
        ("t", "t", "t", "t"),
        ("t", "t", "a", "a"),
        ("t", "a", "a", "a"),
        ("t", "a", "a", "a"),
    )
    dropped = (0, 2, 3, 3)
    out.append(f'<line x1="22" y1="{base + 1}" x2="278" y2="{base + 1}" stroke="{INK}" '
               f'stroke-width="1.4" stroke-linecap="round"/>')
    for q, (cx, stack) in enumerate(zip(cols, plan)):
        for i, kind in enumerate(stack):
            y = base - (i + 1) * (th + gap) + gap
            if kind == "a":
                out.append(f'<rect x="{cx - tw/2}" y="{y}" width="{tw}" height="{th}" rx="2" '
                           f'fill="{AMBER}"/>')
            else:
                out.append(f'<rect x="{cx - tw/2}" y="{y}" width="{tw}" height="{th}" rx="2" '
                           f'fill="none" stroke="{TEAL}" stroke-width="1.7"/>')
        # ghosts of what was dropped, floating above the stack
        for j in range(dropped[q]):
            y = base - (len(stack) + 1 + j) * (th + gap) + gap
            out.append(f'<rect x="{cx - tw/2 + 6}" y="{y + 2}" width="{tw - 12}" height="{th - 4}" '
                       f'rx="2" fill="none" stroke="{RULE}" stroke-width="1.3" '
                       f'stroke-dasharray="3 3"/>')
        out.append(f'<text x="{cx}" y="{base + 20}" {FONT} font-size="11" text-anchor="middle" '
                   f'fill="{INK}" opacity="0.7">Q{q + 1}</text>')
    # the arrow of time
    out.append(f'<line x1="26" y1="{base + 32}" x2="270" y2="{base + 32}" stroke="{RULE}" '
               f'stroke-width="1.2"/>')
    out.append(f'<path d="M 266 {base + 28} L 274 {base + 32} L 266 {base + 36}" fill="none" '
               f'stroke="{RULE}" stroke-width="1.2" stroke-linejoin="round"/>')
    return out, ("Four quarters side by side, each with a stack of four tools. "
                 "More of each stack is amber, meaning new that quarter, and more "
                 "dashed outlines of dropped tools float above it as the year goes on.")


# ── ready: five questions, no score ───────────────────────────────────────
def checklist():
    out = []
    answers = ("tick", "tick", "empty", "tick", "empty")
    for i, a in enumerate(answers):
        y = 28 + i * 25
        out.append(f'<circle cx="40" cy="{y}" r="9" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        out.append(qmark(40, y + 4.5, 12, INK))
        # the question itself, as a line of varying length
        ln = (118, 96, 132, 104, 124)[i]
        out.append(f'<line x1="60" y1="{y}" x2="{60 + ln}" y2="{y}" stroke="{RULE}" '
                   f'stroke-width="2.4" stroke-linecap="round"/>')
        bx, by = 236, y - 8
        if a == "tick":
            out.append(f'<rect x="{bx}" y="{by}" width="16" height="16" rx="2" fill="none" '
                       f'stroke="{INK}" stroke-width="1.5"/>')
            out.append(tick(bx + 3.5, by + 12, 9, TEAL))
        else:
            out.append(f'<rect x="{bx}" y="{by}" width="16" height="16" rx="2" fill="none" '
                       f'stroke="{AMBER}" stroke-width="2"/>')
            out.append(f'<line x1="{bx + 24}" y1="{y}" x2="{bx + 44}" y2="{y}" stroke="{AMBER}" '
                       f'stroke-width="1.8" stroke-linecap="round"/>')
            out.append(f'<path d="M {bx + 36} {y - 5} L {bx + 30} {y} L {bx + 36} {y + 5}" '
                       f'fill="none" stroke="{AMBER}" stroke-width="1.8" '
                       f'stroke-linecap="round" stroke-linejoin="round"/>')
    # deliberately no total line: there is no score at the end
    return out, ("A checklist of five questions. Three boxes are ticked. Two are "
                 "empty, outlined in amber, with an arrow pointing at each. There "
                 "is no total.")


FIGURES = {
    "g-illu-gap": kanizsa,
    "g-illu-caps": measured,
    "g-illu-learning": quarters,
    "g-illu-ready": checklist,
}


def main():
    for name, fn in FIGURES.items():
        body, label = fn()
        (OUT / f"{name}.svg").write_text(svg(name, body, label), encoding="utf-8")
        print("  %-20s %4d bytes" % (name + ".svg", (OUT / f"{name}.svg").stat().st_size))


if __name__ == "__main__":
    main()
