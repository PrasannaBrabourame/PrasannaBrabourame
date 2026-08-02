"""Deterministic hand-drawn SVG primitives."""
import math, random


def _closed_spline(pts):
    """Catmull-Rom through pts, emitted as a closed cubic bezier path."""
    n = len(pts)
    d = "M%.1f %.1f" % pts[0]
    for i in range(n):
        p0, p1 = pts[(i - 1) % n], pts[i]
        p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    return d + " Z"


class R:
    def __init__(self, seed=7):
        self.r = random.Random(seed)
    def j(self, a=1.0):
        return (self.r.random() - .5) * 2 * a

    # ---- a single wobbly stroke from p1 to p2 -------------------------
    def _stroke(self, x1, y1, x2, y2, rough=1.0, bow=1.0):
        L = math.hypot(x2 - x1, y2 - y1)
        off = min(L / 10, 4) * rough
        # midpoint control points, bowed perpendicular to the line
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        nx, ny = -(y2 - y1) / (L or 1), (x2 - x1) / (L or 1)
        b = self.j(bow * min(L / 22, 3.2))
        c1 = (x1 + (mx - x1) * .55 + nx * b + self.j(off * .6),
              y1 + (my - y1) * .55 + ny * b + self.j(off * .6))
        c2 = (mx + (x2 - mx) * .45 + nx * b + self.j(off * .6),
              my + (y2 - my) * .45 + ny * b + self.j(off * .6))
        s = (x1 + self.j(off * .5), y1 + self.j(off * .5))
        e = (x2 + self.j(off * .5), y2 + self.j(off * .5))
        return "M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f" % (
            s[0], s[1], c1[0], c1[1], c2[0], c2[1], e[0], e[1])

    def line(self, x1, y1, x2, y2, w=1.7, col="var(--ink)", passes=2, rough=1.0,
             dash=None, op=1.0):
        out = []
        for _ in range(passes):
            d = self._stroke(x1, y1, x2, y2, rough)
            out.append('<path class="%s" d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
                       'stroke-linecap="round" opacity="%.2f"%s/>'
                       % ('dsh' if dash else 'st', d, col, w,
                          op / (1 if passes == 1 else 1.35),
                          ' stroke-dasharray="%s"' % dash if dash else ''))
        return "".join(out)

    def rect(self, x, y, w, h, sw=1.7, col="var(--ink)", r=0, passes=2, rough=1.0, op=1.0):
        pts = [(x + r, y), (x + w - r, y), (x + w, y + r), (x + w, y + h - r),
               (x + w - r, y + h), (x + r, y + h), (x, y + h - r), (x, y + r)]
        out = []
        seq = [(0, 1), (2, 3), (4, 5), (6, 7)] if r else [(0, 1), (1, 2), (2, 3), (3, 0)]
        if not r:
            pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        for a, b in seq:
            out.append(self.line(pts[a][0], pts[a][1], pts[b][0], pts[b][1],
                                 sw, col, passes, rough, op=op))
        if r:  # corner arcs
            for (ax, ay), (bx, by) in [(pts[1], pts[2]), (pts[3], pts[4]),
                                       (pts[5], pts[6]), (pts[7], pts[0])]:
                out.append('<path class="st" d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" '
                           'stroke="%s" stroke-width="%.2f" stroke-linecap="round" opacity="%.2f"/>'
                           % (ax, ay, (ax + bx) / 2 + self.j(1.2) + (0 if ax == bx else 0),
                              (ay + by) / 2 + self.j(1.2), bx, by, col, sw, op))
        return "".join(out)

    def ellipse(self, cx, cy, rx, ry, sw=1.7, col="var(--ink)", passes=2, op=1.0):
        out = []
        for _ in range(passes):
            n = 9
            pts, start = [], self.r.random() * .7
            for i in range(n):
                a = start + i * 2 * math.pi / n
                k = 1 + self.j(.045)
                pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
            out.append('<path class="st" d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
                       'stroke-linecap="round" opacity="%.2f"/>'
                       % (_closed_spline(pts), col, sw, op / 1.3))
        return "".join(out)

    def arrow(self, x1, y1, x2, y2, w=1.7, col="var(--ink)", head=8, dash=None, op=1.0):
        s = self.line(x1, y1, x2, y2, w, col, 2, 1.0, dash, op)
        a = math.atan2(y2 - y1, x2 - x1)
        for sg in (1, -1):
            hx = x2 - head * math.cos(a - sg * .42)
            hy = y2 - head * math.sin(a - sg * .42)
            s += self.line(x2, y2, hx, hy, w, col, 1, .7, op=op)
        return s

    def hachure(self, x, y, w, h, col="var(--teal)", gap=7, sw=1.0, op=.3):
        out = []
        i = -h
        while i < w:
            x1, y1 = x + i, y + h
            x2, y2 = x + i + h, y
            cx1, cy1, cx2, cy2 = x1, y1, x2, y2
            if x1 < x:
                cx1, cy1 = x, y + h - (x - x1)
            if x2 > x + w:
                cx2, cy2 = x + w, y + (x2 - (x + w))
            out.append(self.line(cx1, cy1, cx2, cy2, sw, col, 1, .8, op=op))
            i += gap
        # one group, faded in rather than drawn — hachure is texture, not line work
        return '<g class="hh">%s</g>' % "".join(out)

    def curly(self, x, y1, y2, col="var(--ink)", sw=1.4, op=.5):
        m = (y1 + y2) / 2
        return ('<path class="st" d="M%.1f %.1f q-6 0 -6 8 L%.1f %.1f q0 8 -6 8 q6 0 6 8 '
                'L%.1f %.1f q0 8 6 8" fill="none" stroke="%s" stroke-width="%.2f" '
                'stroke-linecap="round" opacity="%.2f"/>'
                % (x, y1, x - 6, m - 8, x - 6, m + 8, col, sw, op))

def T(x, y, s, cls="dl", anchor="middle"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return '<text x="%.1f" y="%.1f" class="%s" text-anchor="%s">%s</text>' % (x, y, cls, anchor, s)

def box(rr, x, y, w, h, label, sub=None, tint=None, seed_shift=0):
    """rounded rough box with centred label"""
    out = ""
    if tint:
        out += rr.hachure(x + 3, y + 3, w - 6, h - 6, tint, 8, .9, .22)
    out += rr.rect(x, y, w, h, 1.8, "var(--ink)", r=7)
    if sub:
        out += T(x + w / 2, y + h / 2 - 1, label, "dl")
        out += T(x + w / 2, y + h / 2 + 14, sub, "ds")
    else:
        out += T(x + w / 2, y + h / 2 + 5, label, "dl")
    return out

# ── extra primitives for the experience diagrams ──────────────────
def blob(rr, cx, cy, rx, ry, sw=1.8, col="var(--ink)", passes=2, wob=.10, op=1.0):
    import math
    out = []
    for _ in range(passes):
        n = 10
        pts, start = [], rr.r.random()
        for i in range(n):
            a = start + i * 2 * math.pi / n
            k = 1 + rr.j(wob)
            pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
        out.append('<path class="st" d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
                   'stroke-linecap="round" opacity="%.2f"/>'
                   % (_closed_spline(pts), col, sw, op / 1.35))
    return "".join(out)

def bracket(rr, x1, x2, y, depth=8, col="var(--ink)", sw=1.4, op=.45, down=True):
    d = depth if down else -depth
    return (rr.line(x1, y, x2, y, sw, col, 1, .9, op=op)
            + rr.line(x1, y, x1, y + d, sw, col, 1, .9, op=op)
            + rr.line(x2, y, x2, y + d, sw, col, 1, .9, op=op))

def tick(rr, x, y, h=6, col="var(--ink)", sw=1.3, op=.5):
    return rr.line(x, y - h, x, y + h, sw, col, 1, .8, op=op)

def road(rr, x1, x2, y, col="var(--ink)"):
    """a slightly undulating double rule"""
    o, step = [], (x2 - x1) / 6
    for i in range(6):
        a, b = x1 + i * step, x1 + (i + 1) * step
        o.append(rr.line(a, y + rr.j(1.4), b + rr.j(1.4), y + rr.j(1.4), 2.3, col, 2, .8))
    return "".join(o)

# ── compact emitters: one <path> for many strokes ─────────────────────
def chain(rr, pts, sw=1.1, col="var(--ink)", op=.8, close=False, rough=.5):
    """A whole polyline as ONE path — per-segment jitter, a fraction of the bytes."""
    if len(pts) < 2:
        return ""
    d = []
    seq = list(pts) + ([pts[0]] if close and len(pts) > 2 else [])
    d.append("M%d %d" % (round(seq[0][0]), round(seq[0][1])))
    for i in range(len(seq) - 1):
        s = rr._stroke(seq[i][0], seq[i][1], seq[i+1][0], seq[i+1][1], rough)
        # _stroke returns "M x y C a b c d e f" — keep only the curve
        d.append("C" + s.split("C", 1)[1])
    return ('<path class="st" d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
            'stroke-linecap="round" stroke-linejoin="round" opacity="%.2f"/>'
            % (" ".join(d), col, sw, op))

def bundle(rr, segs, sw=.8, col="var(--ink)", op=.4, jitter=.7):
    """Many independent short strokes as ONE path of M/L subpaths."""
    if not segs:
        return ""
    d = []
    for (x1, y1), (x2, y2) in segs:
        d.append("M%d %dL%d %d" % (round(x1 + rr.j(jitter)), round(y1 + rr.j(jitter)),
                                   round(x2 + rr.j(jitter)), round(y2 + rr.j(jitter))))
    return ('<path class="st" d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
            'stroke-linecap="round" opacity="%.2f"/>' % ("".join(d), col, sw, op))
