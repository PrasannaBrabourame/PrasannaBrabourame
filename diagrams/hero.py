#!/usr/bin/env python3
"""Recolour the hero illustration into the site palette and export it.

    python3 hero.py

Input : diagrams/hero-source.png  (the original blue/purple watercolour)
Output: docs/img/hero-illustration{,@2x}.{webp,jpg}

Blues become the site teal, purples become the site amber, skin is left alone.
The white background is keyed out and re-composited onto the page's paper
colour — keeping an alpha channel instead costs five times the bytes for a
result nobody can tell apart, because the paper behind it is the same colour.
"""
import cv2, numpy as np, os, pathlib

HERE = pathlib.Path(__file__).parent
SRC = HERE.parent.parent / "source-art" / "hero-source.png"
OUT = HERE.parent / "docs" / "img"
WHITE = np.array([255, 255, 255], np.float32)
OUT.mkdir(parents=True, exist_ok=True)

im = cv2.imread(str(SRC), cv2.IMREAD_UNCHANGED)[:, :, :3].astype(np.float32)

# ── hue remap ─────────────────────────────────────────────────────────
hsv = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
h = hsv[:, :, 0] * 2.0
s, v = hsv[:, :, 1], hsv[:, :, 2]
seg = lambda x, a, b, c, d: c + (x - a) * (d - c) / (b - a)

cool = (h >= 178) & (h < 216)      # cyan edge
core = (h >= 216) & (h < 244)      # the bulk of the wash
warm = (h >= 244) & (h < 292)      # purples
skin = (h < 46) | (h > 340)

nh = h.copy()
nh[cool] = seg(h[cool], 178, 216, 193, 181)
nh[core] = seg(h[core], 216, 244, 181, 168)
nh[warm] = seg(h[warm], 244, 292, 46, 30)

ns = s.copy()
ns[skin] *= 0.82
ns[cool | core] *= 1.45
ns[warm] *= 1.75

nv = v.copy()
nv[(cool | core | warm) & (s > 18)] *= 0.90

hsv[:, :, 0] = np.clip(nh / 2.0, 0, 179)
hsv[:, :, 1] = np.clip(ns, 0, 255)
hsv[:, :, 2] = np.clip(nv, 0, 255)
out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
out = np.clip((out - 255.0) * 1.10 + 255.0, 0, 255)    # firm up the pencil

# ── key out the white, re-composite onto paper, trim the margin ───────
mn = out.min(axis=2) / 255.0
alpha = np.clip((1.0 - mn) * 1.06, 0, 1)
alpha[alpha < 0.03] = 0.0
a3 = np.dstack([alpha] * 3)
with np.errstate(divide="ignore", invalid="ignore"):
    unmul = np.clip(np.where(a3 > 0.004, (out - 255.0 * (1.0 - a3)) / a3, 0.0), 0, 255)
# composite onto WHITE, not the paper colour: the <img> is multiply-blended, and
# white x paper == paper exactly, so the rectangle disappears. Compositing onto
# paper instead multiplies paper by itself and leaves a visible darker box.
flat = (unmul * a3 + WHITE * (1 - a3)).astype(np.uint8)

# feather the outer 3% so the art dissolves rather than stopping at an edge
fh, fw = flat.shape[:2]
fade = np.ones((fh, fw), np.float32)
band = max(8, int(min(fh, fw) * 0.03))
ramp = np.linspace(0, 1, band, dtype=np.float32) ** 0.8
fade[:band, :] *= ramp[:, None]
fade[-band:, :] *= ramp[::-1][:, None]
fade[:, :band] *= ramp[None, :]
fade[:, -band:] *= ramp[::-1][None, :]
f3 = np.dstack([fade] * 3)
flat = (flat.astype(np.float32) * f3 + WHITE * (1 - f3)).astype(np.uint8)

ys, xs = np.where(alpha > 0.02)
flat = flat[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

for w, suffix in [(620, ""), (1180, "@2x")]:
    hh = int(round(flat.shape[0] * w / flat.shape[1]))
    r = cv2.resize(flat, (w, hh), interpolation=cv2.INTER_AREA)
    for ext, params in [("webp", [cv2.IMWRITE_WEBP_QUALITY, 82]),
                        ("jpg",  [cv2.IMWRITE_JPEG_QUALITY, 86])]:
        p = OUT / ("hero-illustration%s.%s" % (suffix, ext))
        cv2.imwrite(str(p), r, params)
        print("%-32s %4d x %-4d %6.0f KB" % (p.name, w, hh, p.stat().st_size / 1024))
print("intrinsic size for the <img> tag: %d x %d" % (620, int(round(flat.shape[0]*620/flat.shape[1]))))
