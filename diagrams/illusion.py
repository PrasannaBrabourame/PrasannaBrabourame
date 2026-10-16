#!/usr/bin/env python3
"""Draw a Kanizsa triangle that assembles and falls apart.

    python3 illusion.py

Three discs, each with a wedge removed. When the three gaps line up a triangle
appears — brighter than the page, with crisp edges — although no triangle is
drawn anywhere in the file. Turn the discs a little and it is gone. Nothing was
added or taken away; only the alignment changed.

That is the argument the rest of the site makes, as a picture. A demo is a few
things lined up so the gap between them reads as a system. Turn one of them and
you find out how much was really there.

Animated with CSS rather than SMIL, because CSS can be switched off under
prefers-reduced-motion and SMIL cannot. Light and dark variants: the illusory
surface takes its colour from the page behind it, so the effect only survives a
theme change if both exist.
"""
import math, pathlib

OUT = pathlib.Path(__file__).parent.parent / "docs" / "img"

W, H = 520, 300
CX, CY = W / 2, H / 2 - 10
R = 84                      # centre of the figure to each disc centre
DISC = 46                   # disc radius
WEDGE = 60                  # degrees removed — 60 gives an equilateral triangle
SWING = 52                  # how far each disc turns to break the illusion
DUR = 7.5                   # seconds for one assemble / dissolve cycle

THEMES = {
    "light": dict(ink="#16324F", teal="#2AA5A0", amber="#C9862F", dim="#8b9198"),
    "dark":  dict(ink="#e8e4dc", teal="#4bb3ac", amber="#dda053", dim="#767c84"),
}


def pt(angle_deg, radius, cx=CX, cy=CY):
    a = math.radians(angle_deg)
    return cx + radius * math.cos(a), cy + radius * math.sin(a)


def pacman(cx, cy, r, facing_deg):
    """A disc with a wedge removed, the gap centred on facing_deg.

    Of the four arc-flag combinations only large-arc=1 sweep=0 leaves a wedge
    out; the others draw a teardrop or a pie slice. Checked by rendering all
    four side by side.
    """
    x0, y0 = pt(facing_deg - WEDGE / 2, r, cx, cy)
    x1, y1 = pt(facing_deg + WEDGE / 2, r, cx, cy)
    return (f'M {cx:.2f} {cy:.2f} L {x0:.2f} {y0:.2f} '
            f'A {r} {r} 0 1 0 {x1:.2f} {y1:.2f} Z')


def build(theme):
    c = THEMES[theme]
    angles = [-90, 30, 150]
    accents = [c["ink"], c["ink"], c["teal"]]

    discs, rules = [], []
    for i, (a, fill) in enumerate(zip(angles, accents)):
        x, y = pt(a, R)
        d = pacman(x, y, DISC, a + 180)          # the gap faces the centre
        discs.append(f'<path class="p p{i}" d="{d}" fill="{fill}"/>')
        # rotate about the disc's own centre, not its bounding box — a pac-man's
        # bbox centre is not the centre of the circle it came from
        rules.append(f'.p{i}{{transform-origin:{x:.2f}px {y:.2f}px;'
                     f'animation-delay:{i * 0.14:.2f}s}}')

    css = (
        f'.p{{animation:swing {DUR}s ease-in-out infinite}}'
        + "".join(rules)
        + '@keyframes swing{'
          '0%,38%{transform:rotate(0deg)}'
          f'56%,70%{{transform:rotate({SWING}deg)}}'
          '88%,100%{transform:rotate(0deg)}}'
          f'.dot{{animation:fade {DUR}s ease-in-out infinite}}'
          '@keyframes fade{0%,38%{opacity:1}56%,70%{opacity:.12}88%,100%{opacity:1}}'
          '@media(prefers-reduced-motion:reduce){.p,.dot{animation:none}}'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Three discs, each with a wedge cut out. When the gaps line up a '
        f'triangle appears between them, although no triangle is drawn. The discs turn '
        f'slowly and the triangle dissolves.">\n'
        f'  <style>{css}</style>\n  '
        + "\n  ".join(discs)
        + f'\n  <circle class="dot" cx="{CX:.2f}" cy="{CY:.2f}" r="3.4" fill="{c["amber"]}"/>'
          f'\n  <text x="{W/2:.0f}" y="{H-16}" text-anchor="middle" '
          f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12.5" '
          f'letter-spacing="0.04em" fill="{c["dim"]}">'
          f'There is no triangle in this image.</text>\n</svg>\n'
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        f = OUT / f"illusion-{theme}.svg"
        f.write_text(build(theme), encoding="utf-8")
        print("  wrote %s (%.1f KB)" % (f.name, f.stat().st_size / 1024))


if __name__ == "__main__":
    main()
