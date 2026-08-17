# Publishing to PrasannaBrabourame/PrasannaBrabourame

No pipeline. You build on your machine, commit `docs/`, and GitHub Pages serves those
files as-is. Nothing runs on GitHub.

**`README.md` is deliberately not in this folder** — yours stays exactly as it is.

## The layout

```
README.md          ← yours, untouched. Still what your profile page shows.
docs/              ← THE ONLY THING PAGES SERVES
  index.html
  img/
  og.jpg
  robots.txt
  sitemap.xml
  .nojekyll
build.py           ← writes docs/
publish.sh         ← regenerate → build → test, one command
template.html      ← the source you edit
diagrams/          ← the drawing generators
test-*.mjs         ← 238 assertions
```

Pages is pointed at `docs/`, so everything above it is in the repo but never served.
That keeps the sources versioned without putting them on the web.

## One-time setup

**This folder is not a git repository.** Running `git add` in it gives you
`fatal: not a git repository` — you have to clone your repo first and copy these files
into the clone.

### The easy way

```bash
cd /Users/prasi/Documents/Claude/Projects/Resume/github-profile-repo
./install-into-repo.sh
```

That clones `PrasannaBrabourame/PrasannaBrabourame` next to this folder, copies everything
in, checks `README.md` came through byte-identical, and prints `git status`. It stops
rather than continue if the README changed. Then:

```bash
cd ../PrasannaBrabourame
git add .
git commit -m "Add profile site"
git push origin main
```

Already have a clone somewhere? Pass the path: `./install-into-repo.sh ~/code/PrasannaBrabourame`

### By hand, if you prefer

```bash
cd ~/Documents
git clone https://github.com/PrasannaBrabourame/PrasannaBrabourame.git
cd PrasannaBrabourame

# the trailing /. matters — it copies dotfiles too
cp -R /Users/prasi/Documents/Claude/Projects/Resume/github-profile-repo/. .
rm -f install-into-repo.sh          # the helper doesn't belong in the repo

git status                          # README.md must NOT be listed as modified
git add .
git commit -m "Add profile site"
git push origin main
```

Nothing here is named `README.md`, so yours cannot be overwritten. Any other files
already in your repo are left alone too — this copies in, it never deletes.

### Then turn Pages on

**Settings → Pages → Build and deployment**

- Source: **Deploy from a branch**
- Branch: **main**, folder: **/docs**
- Save

Live in a minute or two at:

```
https://prasannabrabourame.github.io/PrasannaBrabourame/
```

### If the push asks for a password

GitHub stopped accepting account passwords over HTTPS. Either use a personal access token
as the password, or switch the clone to SSH:

```bash
git remote set-url origin git@github.com:PrasannaBrabourame/PrasannaBrabourame.git
```

## Changing something later

Work **inside the clone** from now on — that is the repo. This staging folder has done
its job and you can ignore it.

```bash
cd ~/Documents/PrasannaBrabourame     # wherever you cloned it
# edit template.html, or a generator in diagrams/
./publish.sh
git add docs && git commit -m "Update site" && git push
```

`publish.sh` regenerates every drawing, rebuilds `docs/`, and runs all five test suites.
It installs `jsdom` the first time and never again.

**If a test fails, don't commit.** The confidentiality suite is the one that matters: it
fails if a client name or a product name reappears anywhere in the page or in any
accessible label. With no CI, that check only runs if you run it — which is the one real
cost of dropping the pipeline.

### Rebuilding by hand

```bash
cd diagrams && python3 reality.py && python3 cases.py && python3 exp.py \
  && python3 learn.py && python3 glyphs.py && cd ..
python3 build.py
```

`build.py` takes the canonical URL from `SITE_URL`, defaulting to the URL above:

```bash
SITE_URL=https://prasannabrabourame.com python3 build.py
```

## The contact form

Set `CONTACT_ENDPOINT` and the form POSTs JSON — `{name, email, organization,
problem}` — to it, expecting any 2xx back:

```bash
CONTACT_ENDPOINT=https://formspree.io/f/xxxxxxx python3 build.py
```

It must be `https://`; `build.py` refuses anything else. Anything that accepts a
JSON POST works — Formspree, Web3Forms, a Cloudflare Worker, your own handler.

**Leave it unset and the Send button only opens a `mailto:` draft**, which does
nothing at all for a visitor whose browser has no mail client registered. That is
most people on a work laptop using webmail. Set it before you rely on the form.

If the request fails or takes longer than 12 seconds, the form hands back a
`mailto:` link with everything they typed already in the draft, so a bad endpoint
loses a click rather than an enquiry.

## The visit counter

The footer shows a visit tally, next to the copyright line. `COUNTER_ENDPOINT`
sets where the count comes from; it must return JSON with a numeric `value`:

```bash
COUNTER_ENDPOINT=https://abacus.jasoncameron.dev/hit/prasannabrabourame-site/visits python3 build.py
```

That is the default, so a plain `python3 build.py` already has it. To remove the
counter — and with it the only third-party request the page makes:

```bash
COUNTER_ENDPOINT= python3 build.py
```

Three things worth knowing about it:

- **It is the page's only third-party request.** Everything else, fonts included,
  is served from your own origin. Visitors' IPs reach `abacus.jasoncameron.dev`.
- **Anyone can inflate it.** The increment endpoint is a public unauthenticated
  GET. Treat the number as decoration, not analytics. If you want numbers you can
  actually reason about, use GoatCounter or Plausible instead.
- **It fails invisibly by design.** The element ships with `hidden` and is only
  revealed once a real number arrives. If the service is slow, blocked by a
  content blocker, or discontinued, the footer looks exactly as it did before —
  no stuck ellipsis, no `NaN`. `test-features.mjs` covers all four failure modes.

This is separate from the `komarev` badge in `README.md`, which counts **GitHub
profile views**, not visits to this site.

## Fonts

The three webfonts are vendored into `docs/fonts/` so the page makes no
third-party requests. They are committed; you only need to re-run this when the
font stack itself changes:

```bash
python3 fonts.py
```

It writes `fonts.css`, which `build.py` inlines into the page. All three families
are SIL Open Font License 1.1 — `docs/fonts/OFL.txt` records that.

## Requirements on your machine

| For | Needs |
|---|---|
| Building the page | Python 3 only — no packages |
| Running the tests | Node 18+, and `npm install --no-save jsdom` (publish.sh does it) |
| Re-vendoring the **fonts** | Python 3 and a network connection |
| Regenerating the **artwork** | `pip install opencv-python pillow`, plus the two source photographs from `Resume/source-art/` |

The artwork is already generated and committed. You only need that third row if you want
to change the illustration or a diagram's colours.

## After the first deploy, check three things

1. **Your profile page still renders the README.** Adding `docs/` cannot change that.
2. **The site loads**, illustration included.
3. **Set the repo's Website field** — the ⚙ beside *About* → paste the URL. It currently
   points at your GitHub profile, which is circular.

## Optional: link to it from your README

You asked me to leave `README.md` alone, so I have. But a site nothing links to gets no
visitors. This matches the badge style already in your README:

```markdown
<p align="center">
  <a href="https://prasannabrabourame.github.io/PrasannaBrabourame/"><img src="https://img.shields.io/badge/PORTFOLIO-prasannabrabourame.github.io-2AA5A0?style=for-the-badge&labelColor=16324F"/></a>
</p>
```

## If you want the clean URL later

`https://prasannabrabourame.github.io/` — no `/PrasannaBrabourame` subpath, and
`robots.txt` actually gets honoured (crawlers only read it at a domain root, so on a
subpath it is ignored).

Create a public repo named exactly `prasannabrabourame.github.io`, push this same folder,
point Pages at `main /docs`, then rebuild once so the canonical URL matches:

```bash
SITE_URL=https://prasannabrabourame.github.io python3 build.py
```

Your profile repo then goes back to doing its one job.

## Custom domain

1. Put a file named `CNAME` inside `docs/`, containing `prasannabrabourame.com`
2. `SITE_URL=https://prasannabrabourame.com python3 build.py`
3. Point DNS at GitHub and set the domain under Settings → Pages

`CNAME` must live in `docs/` — it has to be served, not just committed.

## Verified

`docs/` was served from a `/PrasannaBrabourame/` subpath over HTTP and every asset
returned 200. The build is byte-identical across runs. All 238 assertions pass.
Pages gzips automatically: `index.html` is 353 KB on disk, **73 KB over the wire**.
