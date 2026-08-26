#!/usr/bin/env python3
"""Build the site locally into docs/, which is what GitHub Pages serves.

    python3 build.py
    SITE_URL=https://example.com python3 build.py

Nothing runs on GitHub. You build here, commit docs/, and Pages serves it.

Writes:  docs/index.html  docs/404.html  docs/robots.txt  docs/sitemap.xml  docs/.nojekyll
Expects: docs/img/ and docs/og.jpg, written by diagrams/hero.py and diagrams/og.py
         docs/fonts/, written by fonts.py
"""
import datetime, os, pathlib, re, subprocess, sys

SITE_URL = os.environ.get("SITE_URL", "https://prasannabrabourame.github.io/PrasannaBrabourame").rstrip("/")

HERE = pathlib.Path(__file__).parent
REPO_URL = "https://github.com/PrasannaBrabourame/PrasannaBrabourame"


def build_stamp():
    """When this build happened, and which commit it came from.

    The date is the build date rather than anything computed in the browser: a
    visitor should see when the page was last published, not when they opened
    it. The revision makes the deployed page traceable to a commit, which is the
    whole point of showing a version at all.

    Falls back to a date-only stamp outside a git checkout, and marks the
    revision dirty when the tree has uncommitted changes — a page built from
    unsaved edits should not claim to be a clean commit.
    """
    today = datetime.date.today()
    stamp = {
        "iso": today.isoformat(),
        "human": "%d %s %d" % (today.day, today.strftime("%b"), today.year),
        "rev": "",
        "url": REPO_URL,
    }

    def git(*args):
        return subprocess.run(("git",) + args, cwd=str(HERE), capture_output=True,
                              text=True, timeout=10).stdout.strip()

    try:
        rev = git("rev-parse", "--short", "HEAD")
        if not rev:
            return stamp
        # docs/ is this script's own output and is modified by the very act of
        # building, so it can never count towards "dirty" — otherwise every
        # build after the first would report a dirty tree forever. What matters
        # is whether the *sources* are committed.
        dirty = bool(git("status", "--porcelain", "--", ".", ":(exclude)docs"))
        stamp["rev"] = rev + ("-dirty" if dirty else "")
        stamp["url"] = REPO_URL + ("/commits/main" if dirty else "/commit/" + rev)
    except (OSError, subprocess.SubprocessError):
        pass                                    # no git, no revision, still a date
    return stamp

# Where the contact form POSTs. Unset, the form degrades to a mailto: draft,
# which does nothing at all for a reader whose browser has no mail client.
CONTACT_ENDPOINT = os.environ.get("CONTACT_ENDPOINT", "").strip()
if CONTACT_ENDPOINT and not CONTACT_ENDPOINT.startswith("https://"):
    sys.exit("CONTACT_ENDPOINT must be an https:// URL, got: %r" % CONTACT_ENDPOINT)
if '"' in CONTACT_ENDPOINT or "\\" in CONTACT_ENDPOINT:
    sys.exit("CONTACT_ENDPOINT contains characters that would break out of the JS string")

# The footer visit tally. Must return JSON with a numeric `value`. Set to an
# empty string to drop the counter — and the third-party request with it.
COUNTER_ENDPOINT = os.environ.get(
    "COUNTER_ENDPOINT",
    "https://abacus.jasoncameron.dev/hit/prasannabrabourame-site/visits").strip()
if COUNTER_ENDPOINT and not COUNTER_ENDPOINT.startswith("https://"):
    sys.exit("COUNTER_ENDPOINT must be an https:// URL, got: %r" % COUNTER_ENDPOINT)
if '"' in COUNTER_ENDPOINT or "\\" in COUNTER_ENDPOINT:
    sys.exit("COUNTER_ENDPOINT contains characters that would break out of the JS string")

TPL = HERE / "template.html"
DIA = HERE / "diagrams"
OUT = HERE / "docs"

# Deliberately standalone: no webfonts, no diagrams, nothing that can itself 404.
NOT_FOUND = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Not here — Prasanna Brabourame</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#fbfaf7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16191d" media="(prefers-color-scheme: dark)">
<style>
  :root{--ink:#14181c;--body:#565c63;--paper:#fbfaf7;--amber:#c9862f}
  @media (prefers-color-scheme:dark){
    :root{--ink:#e8e4dc;--body:#a8adb4;--paper:#16191d;--amber:#dda053}
  }
  *{box-sizing:border-box}
  body{
    margin:0;min-height:100vh;display:grid;place-items:center;padding:8vw 6vw;
    background:var(--paper);color:var(--ink);
    font:16px/1.55 "Inter","Helvetica Neue",Helvetica,Arial,sans-serif;
  }
  main{max-width:44ch}
  h1{
    font-family:Newsreader,Georgia,"Times New Roman",serif;
    font-weight:500;font-size:clamp(30px,6vw,46px);line-height:1.12;margin:0 0 18px;
  }
  p{color:var(--body);margin:0 0 26px}
  a{
    color:var(--ink);text-decoration:none;font-weight:600;font-size:15px;
    border-bottom:2px solid var(--amber);padding-bottom:2px;
  }
  a:hover{border-bottom-color:var(--ink)}
</style>
</head>
<body>
<main>
  <h1>That page isn't here.</h1>
  <p>The link may be old, or I may have moved something. Everything lives on one
     page anyway, so nothing is more than a scroll away.</p>
  <a href="%s/">Back to the start</a>
</main>
</body>
</html>
"""


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

    fonts_css = HERE / "fonts.css"
    if not fonts_css.exists():
        sys.exit("missing fonts.css — run:  python3 fonts.py")
    html = html.replace("/*{{FONTCSS}}*/", fonts_css.read_text(encoding="utf-8").strip())

    html = html.replace("{{SITE_URL}}", SITE_URL)
    html = html.replace("{{CONTACT_ENDPOINT}}", CONTACT_ENDPOINT)
    html = html.replace("{{COUNTER_ENDPOINT}}", COUNTER_ENDPOINT)

    stamp = build_stamp()
    rev_html = ""
    if stamp["rev"]:
        rev_html = ('  &middot;  <a class="rev" href="%s" rel="noopener">%s</a>'
                    % (stamp["url"], stamp["rev"]))
    html = html.replace("{{BUILT_ISO}}", stamp["iso"])
    html = html.replace("{{BUILT_HUMAN}}", stamp["human"])
    html = html.replace("{{BUILT_REV_HTML}}", rev_html)
    left = re.findall(r"\{\{[A-Za-z0-9_:-]+\}\}", html)
    if left:
        sys.exit("unresolved placeholders: %s" % sorted(set(left)))

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    (OUT / "404.html").write_text(NOT_FOUND % SITE_URL, encoding="utf-8")

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL, encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n    <loc>%s/</loc>\n    <lastmod>%s</lastmod>\n"
        "    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>\n  </url>\n"
        "</urlset>\n" % (SITE_URL, stamp["iso"]), encoding="utf-8")

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

    # Every @font-face the inlined CSS points at has to actually be on disk,
    # or the page silently falls back to system fonts in production.
    faces = re.findall(r"url\(fonts/([^)]+)\)", html)
    gone = [f for f in faces if not (OUT / "fonts" / f).exists()]
    if gone:
        sys.exit("fonts.css references missing files: %s\n  run:  python3 fonts.py"
                 % ", ".join(sorted(set(gone))))

    kb = len(html.encode()) / 1024
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1024
    print("built docs/ — %d drawings, index.html %.0f KB, %.0f KB total" % (len(names), kb, total))
    print("canonical: %s" % SITE_URL)
    print("stamped:   %s%s" % (stamp["human"], "  rev " + stamp["rev"] if stamp["rev"] else ""))
    if stamp["rev"].endswith("-dirty"):
        print("           ^ built from an uncommitted tree; commit before publishing")
    if CONTACT_ENDPOINT:
        print("contact:   %s" % CONTACT_ENDPOINT)
    else:
        print("contact:   NOT SET — the form only opens a mail draft.\n"
              "           Fix with:  CONTACT_ENDPOINT=https://... python3 build.py")
    if COUNTER_ENDPOINT:
        print("counter:   %s" % COUNTER_ENDPOINT)
        print("           ^ the page's only third-party request. COUNTER_ENDPOINT= to drop it.")
    else:
        print("counter:   off — no third-party requests at all")
    print("\nnext:  git add docs && git commit -m 'Update site' && git push")


if __name__ == "__main__":
    main()
