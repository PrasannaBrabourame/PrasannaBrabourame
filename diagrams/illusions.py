#!/usr/bin/env python3
"""One optical illusion per section, each carrying that section's argument.

    python3 illusions.py

These are not decoration. Each figure is the section's claim restated as
something the reader's own eyes get wrong:

  gap           Kanizsa triangle — a system you can see that nobody built
  work          Ebbinghaus — the same finding looks graver beside small ones
  how           Necker cube — one architecture, two readings, no third
  track         Müller-Lyer — the same ten years, measured from different ends
  capabilities  simultaneous contrast — two identical greys, judged by eye
  learning      Hermann grid — the more you look, the more you see that is absent
  ready         café wall — the rows are parallel; it does not look like it

Written with var(--ink), var(--teal) and var(--amber) and nothing else, so they
re-theme with the page like the other thirteen drawings. The Kanizsa figure in
particular depends on it: the triangle it suggests is made of page colour, so it
only works while the fill really is the page.
"""
import math, pathlib

OUT = pathlib.Path(__file__).parent
W, H = 300, 168                 # a compact band, not a full-width sketch

INK, TEAL, AMBER = "var(--ink)", "var(--teal)", "var(--amber)"
RULE = "var(--rule)"


def svg(name, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{label}">\n  ' + "\n  ".join(body) + "\n</svg>\n")


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


# ── work: the same circle, made to look bigger ────────────────────────────
def ebbinghaus():
    out, r = [], 15
    for cx, ring_r, ring_n, ring_d in ((88, 40, 6, 17), (212, 26, 7, 7)):
        for i in range(ring_n):
            a = math.radians(i * 360 / ring_n - 90)
            out.append(f'<circle cx="{cx + ring_r * math.cos(a):.1f}" '
                       f'cy="{H/2 + ring_r * math.sin(a):.1f}" r="{ring_d}" '
                       f'fill="none" stroke="{RULE}" stroke-width="1.6"/>')
        out.append(f'<circle cx="{cx}" cy="{H/2}" r="{r}" fill="{TEAL}"/>')
    return out, ("Two identical teal circles. The one ringed by large circles looks "
                 "smaller than the one ringed by small circles.")


# ── how: one architecture, two readings ───────────────────────────────────
def necker():
    ox, oy, s, d = 96, 44, 72, 34
    f = [(ox, oy), (ox + s, oy), (ox + s, oy + s), (ox, oy + s)]
    b = [(x + d, y - d * 0.62) for x, y in f]
    out = []
    for p in (f, b):
        for i in range(4):
            x1, y1 = p[i]; x2, y2 = p[(i + 1) % 4]
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                       f'stroke="{INK}" stroke-width="1.7" stroke-linecap="round"/>')
    for (x1, y1), (x2, y2) in zip(f, b):
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="{INK}" stroke-width="1.7" stroke-linecap="round"/>')
    out.append(f'<circle cx="{f[1][0]:.1f}" cy="{f[1][1]:.1f}" r="3" fill="{AMBER}"/>')
    return out, ("A wireframe cube that can be seen two ways, with no way to see it "
                 "both ways at once.")


# ── track: the same length, measured from different ends ──────────────────
def muller_lyer():
    out, x0, x1 = [], 70, 230
    for y, flip in ((60, 1), (112, -1)):
        out.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{INK}" '
                   f'stroke-width="1.9" stroke-linecap="round"/>')
        for x, sgn in ((x0, 1), (x1, -1)):
            for dy in (-15, 15):
                out.append(f'<line x1="{x}" y1="{y}" x2="{x + sgn * flip * 15}" '
                           f'y2="{y + dy}" stroke="{TEAL}" stroke-width="1.7" '
                           f'stroke-linecap="round"/>')
    out.append(f'<circle cx="{(x0+x1)/2}" cy="86" r="2.6" fill="{AMBER}"/>')
    return out, ("Two horizontal lines of exactly equal length. The arrowheads make "
                 "one look longer than the other.")


# ── capabilities: two identical greys ─────────────────────────────────────
def contrast():
    out = [f'<rect x="26" y="40" width="112" height="88" fill="{INK}" opacity="0.14"/>',
           f'<rect x="162" y="40" width="112" height="88" fill="{INK}" opacity="0.62"/>']
    for x in (58, 194):
        out.append(f'<rect x="{x}" y="70" width="48" height="28" fill="{TEAL}"/>')
    out.append(f'<circle cx="{W/2}" cy="84" r="2.6" fill="{AMBER}"/>')
    return out, ("Two identical teal bars. On the darker ground one looks lighter "
                 "than the other.")


# ── learning: dots that are not there ─────────────────────────────────────
def hermann():
    out, n, cell, gap = [], 7, 17, 4
    x0 = (W - (n * cell + (n - 1) * gap)) / 2
    y0 = (H - (n * cell + (n - 1) * gap)) / 2 + 2
    for r in range(n):
        for c in range(n):
            out.append(f'<rect x="{x0 + c*(cell+gap):.1f}" y="{y0 + r*(cell+gap):.1f}" '
                       f'width="{cell}" height="{cell}" fill="{INK}" opacity="0.82"/>')
    return out, ("A grid of squares. Grey smudges appear at the crossings between "
                 "them, where nothing is drawn.")


# ── ready: the rows really are parallel ───────────────────────────────────
def cafe_wall():
    out, rows, tile, bh = [], 6, 40, 16
    pad = 18
    y0 = (H - rows * bh) / 2
    for r in range(rows):
        y = y0 + r * bh
        # half a PERIOD, not a whole one: shifting by `tile` lands the rows
        # back on top of each other and you get vertical stripes
        off = (r % 2) * (tile / 2)
        x = pad - tile
        while x < W - pad:
            x1 = max(x + off, pad)
            x2 = min(x + off + tile / 2, W - pad)
            if x2 - x1 > 4:          # drop clipped slivers at the edges
                out.append(f'<rect x="{x1:.1f}" y="{y:.1f}" width="{x2-x1:.1f}" '
                           f'height="{bh}" fill="{INK}" opacity="0.9"/>')
            x += tile
        if r < rows - 1:
            out.append(f'<line x1="{pad}" y1="{y + bh:.1f}" x2="{W-pad}" '
                       f'y2="{y + bh:.1f}" stroke="{INK}" stroke-width="1.5" '
                       f'opacity="0.42"/>')
    return out, ("Rows of offset blocks separated by straight lines. The lines are "
                 "parallel but appear to slope.")


FIGURES = {
    "g-illu-gap": kanizsa,
    "g-illu-work": ebbinghaus,
    "g-illu-how": necker,
    "g-illu-track": muller_lyer,
    "g-illu-caps": contrast,
    "g-illu-learning": hermann,
    "g-illu-ready": cafe_wall,
}


def main():
    for name, fn in FIGURES.items():
        body, label = fn()
        (OUT / f"{name}.svg").write_text(svg(name, body, label), encoding="utf-8")
        print("  %-20s %4d bytes" % (name + ".svg", (OUT / f"{name}.svg").stat().st_size))


if __name__ == "__main__":
    main()
