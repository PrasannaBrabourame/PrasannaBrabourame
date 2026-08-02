import cv2, numpy as np, sys, math
sys.path.insert(0, "/sessions/happy-keen-tesla/mnt/Resume/site/diagrams")
from rough import R, chain, bundle

# ── the subject: the man wearing the watch. Nobody else is traced. ──
POLY = [
 (358,62),(400,42),(455,40),(510,55),(556,85),(585,130),(596,185),(590,235),
 (575,275),(558,312),(548,342),(566,362),(602,402),(630,452),(646,510),(650,545),
 (330,545),(150,545),(86,545),                     # crop line, chest height
 (88,528),(96,516),(105,470),(112,425),            # up the outside of the forearm
 (150,400),(200,356),(232,330),(252,322),(276,314),(298,300),   # wrist → hand → chin
 (296,270),(288,250),(296,230),(298,212),(310,196),(316,180),(322,165),
 (334,150),(344,130),(352,100)                     # up the profile to the hair
]
PAD = 12
xs = [p[0] for p in POLY]; ys = [p[1] for p in POLY]
X0, Y0 = min(xs) - PAD, min(ys) - PAD
X1, Y1 = max(xs) + PAD, max(ys) + PAD
SC = 420.0 / (X1 - X0)                                  # tracing resolution

im = cv2.imread("src.png")
crop = im[Y0:Y1, X0:X1]
W = int(round((X1 - X0) * SC)); H = int(round((Y1 - Y0) * SC))
crop = cv2.resize(crop, (W, H), interpolation=cv2.INTER_AREA)
poly = np.array([[int(round((x - X0) * SC)), int(round((y - Y0) * SC))] for x, y in POLY], np.int32)

mask = np.zeros((H, W), np.uint8)
cv2.fillPoly(mask, [poly], 255)
mask = cv2.erode(mask, np.ones((3, 3), np.uint8), 1)

gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
tone = cv2.bilateralFilter(gray, 9, 55, 55)                       # tones: true luminance
clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
detail = cv2.bilateralFilter(clahe.apply(gray), 7, 45, 45)        # edges: equalised

ins = tone[mask > 0]
t_dark, t_mid = np.percentile(ins, [30, 60])

r = R(4211)
out = []

def strokes(pts, sw, col, op, close=False):
    return chain(r, pts, sw, col, op, close)

def hatch(band, angle, gap, minlen=6):
    m = (band & (mask > 0)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((4, 4), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    a = math.radians(angle); dx, dy = math.cos(a), math.sin(a); nx, ny = -dy, dx
    diag = int(math.hypot(W, H)); cx, cy = W / 2, H / 2
    segs = []
    for off in np.arange(-diag / 2, diag / 2, gap):
        px, py = cx + nx * off, cy + ny * off
        run = None
        for t in np.arange(-diag / 2, diag / 2, 1.2):
            x, y = int(px + dx * t), int(py + dy * t)
            hit = 0 <= x < W and 0 <= y < H and m[y, x] > 0
            if hit and run is None: run = (x, y)
            elif not hit and run is not None:
                if math.hypot(x - run[0], y - run[1]) > minlen: segs.append((run, (x, y)))
                run = None
    return segs

# ── tone: cross-hatch the darks, one pass on the mids, nothing on the lights ──
dark = tone <= t_dark
mid = (tone > t_dark) & (tone <= t_mid)
hs, n = [], 0
for band, ang, gap, w, op in [(dark, 54, 7.4, .85, .44),
                              (dark, -48, 12.5, .8, .34),
                              (mid, 54, 12.5, .75, .30)]:
    segs = hatch(band, ang, gap)
    n += len(segs)
    hs.append(bundle(r, segs, w, "var(--ink)", op))
out.append('<g class="hh">%s</g>' % "".join(hs))

# ── features: the line work that makes it a face ──
edges = cv2.bitwise_and(cv2.Canny(detail, 30, 82), mask)
cnts, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
cnts = sorted(cnts, key=lambda c: cv2.arcLength(c, False), reverse=True)
kept = 0
for c in cnts:
    if cv2.arcLength(c, False) < 24: break
    ap = cv2.approxPolyDP(c, 1.1, False).reshape(-1, 2)
    if len(ap) < 2: continue
    out.append(strokes([tuple(map(int, p)) for p in ap], 1.05, "var(--ink)", .8))
    kept += 1
    if kept >= 104: break

# ── the silhouette, drawn firmly ──
out.append(strokes([tuple(map(int, p)) for p in poly], 2.0, "var(--ink)", .95, close=True))

# ── the watch: the one thing he asked to keep ──
def px(x, y): return ((x - X0) * SC, (y - Y0) * SC)
wx, wy = px(163, 449)
wr = 26 * SC
ax, ay = -0.59, 0.81            # the forearm axis, chin down to elbow
out.append(r.ellipse(wx, wy, wr, wr, 2.0, "var(--amber)", 2, op=1.0))
out.append(r.ellipse(wx, wy, wr * .55, wr * .55, 1.1, "var(--amber)", 1, op=.65))
for sg in (1, -1):
    out.append(r.line(wx + ax * wr * sg, wy + ay * wr * sg,
                      wx + ax * wr * 1.75 * sg, wy + ay * wr * 1.75 * sg,
                      1.8, "var(--amber)", 2, op=.8))

svg = ('<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" '
       'aria-label="A hand-drawn portrait: Prasanna Brabourame in profile, listening, '
       'chin resting on his hand, a watch on his wrist.">%s</svg>' % (W, H, "".join(out)))
open("portrait.svg", "w").write(svg)
print("hatch segs %d in %d paths | features %d | viewBox %dx%d | %.1f KB"
      % (n, len(hs), kept, W, H, len(svg)/1024))
