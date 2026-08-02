#!/usr/bin/env bash
# Build the site and check it, then tell you what to commit.
#   ./publish.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "── regenerating the drawings"
( cd diagrams && for g in reality cases exp learn glyphs; do python3 "$g.py" >/dev/null; done )
echo "   ok"

echo "── building docs/"
python3 build.py

echo "── tests"
if [ ! -d node_modules/jsdom ]; then
  echo "   installing jsdom (once)"; npm install --no-save --silent jsdom
fi
for t in test-page test-reduced-motion test-walk-strip test-ambient test-confidentiality; do
  printf "   %-26s " "$t"
  node "$t.mjs"
done

echo
echo "── ready. Commit docs/ and push:"
echo "     git add docs && git commit -m 'Update site' && git push"
