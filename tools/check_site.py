#!/usr/bin/env python3
"""Site checks: run before every push. Exits 1 on any failure.

  cd ~/Documents/ClaudeCode/PortfolioSite && python3 tools/check_site.py

- every local href/src exists, with the exact case (GitHub Pages is case-sensitive, macOS is not)
- no em dashes; external links open in a new tab with rel="noopener noreferrer"
- the hero count equals the number of cards; each directory's "NN entries" note matches its cards
- every case page's crumb "NN of MM" and pagination match its card's place on the homepage
- no copy that ranks a page within its directory ("the second game", "the more ambitious one"),
  since that goes stale the moment the directory changes
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []

def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return f.read()

def exists_exact(rel):
    parts, cur = os.path.normpath(rel).split(os.sep), ROOT
    for part in parts:
        if part == '..':
            cur = os.path.dirname(cur); continue
        if part not in os.listdir(cur):
            return False
        cur = os.path.join(cur, part)
    return True

pages = ['index.html', '404.html'] + ['projects/' + f for f in sorted(os.listdir(os.path.join(ROOT, 'projects'))) if f.endswith('.html')]
RANKING = re.compile(r'\b(first|second|third|fourth|last) (game|product|one) in this directory\b|\bthe more ambitious one\b|\bodd one out\b', re.I)

for p in pages:
    s = read(p)
    if '—' in s:
        fails.append(f'{p}: em dash')
    for m in RANKING.finditer(re.sub(r'<[^>]+>', '', s)):
        fails.append(f'{p}: ranks itself within its directory: "{m.group(0)}"')
    for u in re.findall(r'(?:href|src)="([^"]+)"', s):
        if u.startswith(('http:', 'https:', '//', 'mailto:', '#')):
            continue
        path = u.split('#')[0].split('?')[0]
        if path and not exists_exact(os.path.join(os.path.dirname(p), path)):
            fails.append(f'{p}: missing (or wrong case) {u}')
    for tag in re.findall(r'<a [^>]*href="https?://[^"]*"[^>]*>', s):
        if 'target="_blank"' not in tag or 'rel="noopener noreferrer"' not in tag:
            fails.append(f'{p}: external link without target/rel: {tag[:90]}')

# Homepage order is the source of truth: cards per directory, in order.
idx = read('index.html')
heads = [(m.start(), m.group(1)) for m in re.finditer(r'<h2>ls ~/([a-z-]+)/</h2>', idx)]
dirs = {}
for i, (start, name) in enumerate(heads):
    end = heads[i + 1][0] if i + 1 < len(heads) else idx.find('id="about"')
    chunk = idx[start:end]
    dirs[name] = re.findall(r'<a class="proj win reveal" href="projects/([^"]+)"', chunk)
    note = re.search(r'<span class="note">(\d+) entries', chunk)
    if not note or int(note.group(1)) != len(dirs[name]):
        fails.append(f'index.html: ~/{name} note says {note.group(1) if note else "?"} entries, has {len(dirs[name])} cards')
    for n, f in enumerate(dirs[name], 1):
        if not re.search(r'<a class="proj win reveal" href="projects/%s">\s*<span class="win-bar">.*?<span class="idx">%02d</span>' % (re.escape(f), n), chunk, re.S):
            fails.append(f'index.html: card {f} is not numbered {n:02d}')

total = sum(len(v) for v in dirs.values())
hero = re.search(r'f3"><strong>(\d+)</strong>', idx)
if not hero or int(hero.group(1)) != total:
    fails.append(f'index.html: hero count {hero.group(1) if hero else "?"} != {total} cards')

for name, files in dirs.items():
    for n, f in enumerate(files, 1):
        s = read('projects/' + f)
        if not re.search(r'<p class="crumbs"><a href="\.\./index\.html#[a-z]+">~/%s</a> / [a-z-]+ <span>%02d of %02d</span></p>' % (name, n, len(files)), s):
            fails.append(f'projects/{f}: crumb is not ~/{name} {n:02d} of {len(files):02d}')
        nav = re.search(r'<nav class="pagination".*?</nav>', s, re.S)
        hrefs = re.findall(r'href="([^"]+)"', nav.group(0)) if nav else []
        want_prev = files[n - 2] if n > 1 else None
        want_next = files[n] if n < len(files) else None
        if len(hrefs) != 2 or (want_prev and hrefs[0] != want_prev) or (want_next and hrefs[1] != want_next) \
           or (not want_prev and not hrefs[0].startswith('../index.html#')) or (not want_next and not hrefs[1].startswith('../index.html#')):
            fails.append(f'projects/{f}: pagination {hrefs} != prev {want_prev} / next {want_next}')

for f in fails:
    print('FAIL', f)
print(f'{len(pages)} pages, {total} cards, {len(fails)} failures')
sys.exit(1 if fails else 0)
