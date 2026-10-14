#!/usr/bin/env bash
# Build the site and check it, then tell you what to commit.
#   ./publish.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "── regenerating the drawings"
( cd diagrams && for g in reality cases exp learn glyphs; do python3 "$g.py" >/dev/null; done )
echo "   ok"

# A dirty stamp has shipped twice now: build.py runs before the sources are
# committed, bakes "<sha>-dirty" into the footer, and that gets committed into
# docs/ and deployed. Refuse to build rather than produce it again.
if [ -n "$(git status --porcelain -- . ':(exclude)docs' 2>/dev/null)" ]; then
  echo "✗ uncommitted source changes — the build stamp would read '-dirty'."
  echo "  Commit sources first, then rebuild, then commit docs/:"
  git status --porcelain -- . ':(exclude)docs' | sed 's/^/    /'
  echo "  Override with:  ALLOW_DIRTY=1 ./publish.sh"
  [ "${ALLOW_DIRTY:-}" = "1" ] || exit 1
fi

echo "── building docs/"
if [ ! -f fonts.css ]; then
  echo "   vendoring the webfonts (once)"; python3 fonts.py
fi
python3 build.py

echo "── tests"
if [ ! -d node_modules/jsdom ]; then
  echo "   installing jsdom (once)"; npm install --no-save --silent jsdom
fi
for t in test-page test-reduced-motion test-walk-strip test-ambient test-confidentiality test-features; do
  printf "   %-26s " "$t"
  node "$t.mjs" < /dev/null
done

echo
echo "── ready. Commit docs/ and push:"
echo "     git add docs && git commit -m 'Update site' && git push"
