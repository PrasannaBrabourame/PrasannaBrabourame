#!/usr/bin/env python3
"""Draw a Kanizsa triangle — the illusion where you see an edge that is not drawn.

    python3 illusion.py

Three discs with a wedge cut out of each, and three open corners. No triangle is
drawn anywhere in the file, yet one is plainly visible, brighter than the page it
sits on. The brain supplies the edges because three aligned gaps are better
explained by something lying on top than by coincidence.

It earns its place on this profile rather than being decoration: the whole site
argues that a demo looks like a working system until you look for the parts that
are not there. This is that argument as a picture.

Writes a light and a dark variant. The README picks between them with <picture>
and prefers-color-scheme, so the illusory surface always matches the page behind
it — which is the only way the effect survives a theme switch.
"""
import math, pathlib

OUT = pathlib.Path(__file__).parent.parent / "docs" / "img"

W, H = 520, 300
CX, CY = W / 2, H / 2 - 10
R = 84                      # distance from centre to each disc
DISC = 46                   # disc radius
WEDGE = 60                  # degrees cut out of each disc
BAR = 7                     # stroke of the open corners
OUT_R = 150                 # corners of the second, inverted triangle

THEMES = {
    "light": dict(ink="#16324F", teal="#2AA5A0", amber="#C9862F", dim="#8b9198"),
    "dark":  dict(ink="#e8e4dc", teal="#4bb3ac", amber="#dda053", dim="#767c84"),
}


def pt(angle_deg, radius, cx=None, cy=None):
    a = math.radians(angle_deg)
    return ((cx if cx is not None else CX) + radius * math.cos(a),
            (cy if cy is not None else CY) + radius * math.sin(a))


def pacman(cx, cy, r, facing_deg):
    """A disc with a wedge removed, the gap pointing along facing_deg."""
    a0 = facing_deg - WEDGE / 2
    a1 = facing_deg + WEDGE / 2
    x0, y0 = pt(a0, r, cx, cy)
    x1, y1 = pt(a1, r, cx, cy)
    # large-arc=1 sweep=0 is the combination that leaves a wedge out; the other
    # three draw a teardrop or a pie slice. Verified by rendering all four.
    return (f'<path d="M {cx:.2f} {cy:.2f} L {x0:.2f} {y0:.2f} '
            f'A {r} {r} 0 1 0 {x1:.2f} {y1:.2f} Z"')


def corner(cx, cy, toward_deg, arm, stroke):
    """An open corner: two arms meeting at a point, nothing closing them."""
    a = math.radians(toward_deg)
    # the two arms sit symmetrically either side of the inward direction
    left = math.radians(toward_deg - 60)
    right = math.radians(toward_deg + 60)
    p = (cx, cy)
    l = (cx + arm * math.cos(left), cy + arm * math.sin(left))
    r = (cx + arm * math.cos(right), cy + arm * math.sin(right))
    return (f'<path d="M {l[0]:.2f} {l[1]:.2f} L {p[0]:.2f} {p[1]:.2f} '
            f'L {r[0]:.2f} {r[1]:.2f}" fill="none" stroke="{stroke}" '
            f'stroke-width="{BAR}" stroke-linecap="round" stroke-linejoin="round"/>')


def build(theme):
    c = THEMES[theme]
    # discs at the corners of an upward triangle; each gap faces the centre
    angles = [-90, 30, 150]
    parts = []

    parts.append(f'<rect width="{W}" height="{H}" fill="none"/>')

    # the three discs. One carries the accent, so the eye has somewhere to land.
    accents = [c["ink"], c["ink"], c["teal"]]
    for a, fill in zip(angles, accents):
        x, y = pt(a, R)
        facing = a + 180                      # the mouth faces the centre
        parts.append(pacman(x, y, DISC, facing) + f' fill="{fill}"/>')

    # a single amber dot at the centroid of the triangle that is not there
    parts.append(f'<circle cx="{CX:.2f}" cy="{CY:.2f}" r="3.4" fill="{c["amber"]}"/>')

    label = ("There is no triangle in this image." if theme == "light"
             else "There is no triangle in this image.")
    parts.append(
        f'<text x="{W/2:.0f}" y="{H-16}" text-anchor="middle" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12.5" '
        f'letter-spacing="0.04em" fill="{c["dim"]}">{label}</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" '
            f'aria-label="A Kanizsa triangle: three discs each with a wedge removed, '
            f'arranged so that a bright triangle appears between them even though no '
            f'triangle is drawn.">\n  ' + "\n  ".join(parts) + "\n</svg>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        f = OUT / f"illusion-{theme}.svg"
        f.write_text(build(theme), encoding="utf-8")
        print("  wrote %s (%.1f KB)" % (f.name, f.stat().st_size / 1024))


if __name__ == "__main__":
    main()
