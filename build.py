#!/usr/bin/env python3
"""Build the site locally into docs/, which is what GitHub Pages serves.

    python3 build.py
    SITE_URL=https://example.com python3 build.py

Nothing runs on GitHub. You build here, commit docs/, and Pages serves it.

Writes:  docs/index.html  docs/robots.txt  docs/sitemap.xml  docs/.nojekyll
Expects: docs/img/ and docs/og.jpg, written by diagrams/hero.py and diagrams/og.py
"""
import datetime, os, pathlib, re, sys

SITE_URL = os.environ.get("SITE_URL", "https://prasannabrabourame.github.io/PrasannaBrabourame").rstrip("/")

HERE = pathlib.Path(__file__).parent
TPL = HERE / "template.html"
DIA = HERE / "diagrams"
OUT = HERE / "docs"


def main():
    html = TPL.read_text(encoding="utf-8")

    names = re.findall(r"\{\{SVG:([a-z0-9_-]+)\}\}", html)
    if not names:
        sys.exit("no {{SVG:...}} placeholders found in template.html")
    for name in names:
        f = DIA / (name + ".svg")
        if not f.exists():
            sys.exit("missing %s — run the generators in diagrams/ first" % f)
        svg = f.read_text(encoding="utf-8").strip()
        if name.startswith("g-"):                      # a small inline glyph, not a diagram
            html = html.replace("{{SVG:%s}}" % name, svg)
        else:
            html = html.replace("{{SVG:%s}}" % name, svg.replace("<svg ", '<svg class="sk" ', 1))

    html = html.replace("{{SITE_URL}}", SITE_URL)
    left = re.findall(r"\{\{[A-Za-z0-9_:-]+\}\}", html)
    if left:
        sys.exit("unresolved placeholders: %s" % sorted(set(left)))

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(html, encoding="utf-8")

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL, encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n    <loc>%s/</loc>\n    <lastmod>%s</lastmod>\n"
        "    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>\n  </url>\n"
        "</urlset>\n" % (SITE_URL, datetime.date.today().isoformat()), encoding="utf-8")

    # GitHub Pages runs Jekyll on a branch deploy unless this file exists.
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # The image generators write straight into docs/, so there is only ever one
    # copy of each. Verify rather than duplicate.
    missing = [r for r in ("img/hero-illustration.webp", "img/hero-illustration.jpg",
                           "img/hero-illustration@2x.webp", "img/hero-illustration@2x.jpg",
                           "og.jpg") if not (OUT / r).exists()]
    if missing:
        sys.exit("missing from docs/: %s\n  regenerate with:  cd diagrams && "
                 "python3 hero.py && python3 og.py\n  (needs the source photographs in "
                 "../source-art/ — see DEPLOY.md)" % ", ".join(missing))

    kb = len(html.encode()) / 1024
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1024
    print("built docs/ — %d drawings, index.html %.0f KB, %.0f KB total" % (len(names), kb, total))
    print("canonical: %s" % SITE_URL)
    print("\nnext:  git add docs && git commit -m 'Update site' && git push")


if __name__ == "__main__":
    main()
