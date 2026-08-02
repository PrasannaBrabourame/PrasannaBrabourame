#!/usr/bin/env python3
"""Build og.jpg, the 1200x630 social card, from the hero illustration."""
import cv2, glob, pathlib
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent
ART = HERE.parent / "docs" / "img" / "hero-illustration@2x.jpg"
OUT = HERE.parent / "docs" / "og.jpg"

W, H = 1200, 630
PAPER, INK, BODY, TEAL = (251, 250, 247), (20, 24, 28), (86, 92, 99), (31, 122, 117)

def f(pat, size):
    m = glob.glob("/usr/share/fonts/**/" + pat, recursive=True) or \
        glob.glob("/System/Library/Fonts/**/" + pat, recursive=True)
    return ImageFont.truetype(m[0], size) if m else ImageFont.load_default(size)

art = cv2.cvtColor(cv2.imread(str(ART)), cv2.COLOR_BGR2RGB)
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

aw = 640; ah = int(art.shape[0] * aw / art.shape[1])
img.paste(Image.fromarray(cv2.resize(art, (aw, ah), interpolation=cv2.INTER_AREA)),
          (W - aw + 30, (H - ah) // 2))
d.rectangle([0, 0, int(W * 0.50), H], fill=PAPER)

M = 76
d.text((M, 74), "FORWARD DEPLOYED AI SPECIALIST  ·  SINGAPORE", font=f("DejaVuSans-Bold.ttf", 18), fill=BODY)
y = 134
for line, fo, col in [("A demo has to", f("DejaVuSerif.ttf", 50), INK),
                      ("work once.", f("DejaVuSerif.ttf", 50), INK),
                      ("Production has to", f("DejaVuSerif-Italic.ttf", 50), TEAL),
                      ("work on the worst", f("DejaVuSerif-Italic.ttf", 50), TEAL),
                      ("day of the quarter.", f("DejaVuSerif-Italic.ttf", 50), TEAL)]:
    d.text((M, y), line, font=fo, fill=col); y += 66
d.line([(M, H - 104), (int(W * 0.47), H - 104)], fill=(228, 224, 216), width=2)
d.text((M, H - 84), "Prasanna Brabourame", font=f("DejaVuSerif-Bold.ttf", 30), fill=INK)
d.text((M, H - 44), "Regulated-domain AI systems, built end to end", font=f("DejaVuSans.ttf", 20), fill=BODY)

img.save(OUT, quality=88, optimize=True, progressive=True)
print("og.jpg %.0f KB" % (OUT.stat().st_size / 1024))
