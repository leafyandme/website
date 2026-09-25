#!/usr/bin/env python3
"""Check built pages, local links, fragments, and the zero-JavaScript contract."""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '_site').resolve()
BASE = sys.argv[2] if len(sys.argv) > 2 else ''

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.headings, self.errors = [], set(), 0, []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.errors.append('Unexpected JavaScript')
        if tag == 'h1':
            self.headings += 1
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append('Duplicate id: ' + attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'img' and 'alt' not in attrs:
            self.errors.append('Image without alt text')
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])

pages = {p: Page(p) for p in ROOT.rglob('*.html')}
errors = []
for required in ('index.html', 'support/index.html', 'privacy/index.html', 'credits/index.html', '404.html'):
    if ROOT / required not in pages:
        errors.append('Missing page: ' + required)
for path, page in pages.items():
    errors.extend(f'{path.relative_to(ROOT)}: {e}' for e in page.errors)
    if page.headings != 1:
        errors.append(f'{path.name}: expected one h1, found {page.headings}')
    if re.search(r'\{%|\{\{', path.read_text()):
        errors.append(f'{path.name}: unrendered Liquid')
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = unquote(url.path)
        if not target:
            dest = path
        elif target.startswith('/'):
            if BASE and not (target == BASE or target.startswith(BASE + '/')):
                errors.append(f'{path.name}: link escapes baseurl: {link}')
                continue
            dest = ROOT / target.removeprefix(BASE).lstrip('/')
        else:
            dest = path.parent / target
        if dest.is_dir():
            dest /= 'index.html'
        dest = dest.resolve()
        if not dest.exists():
            errors.append(f'{path.name}: missing target {link}')
        elif url.fragment and dest in pages and unquote(url.fragment) not in pages[dest].ids:
            errors.append(f'{path.name}: missing fragment {link}')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'Passed: {len(pages)} pages, local links and fragments, image alt text, one h1 per page, no JavaScript.')

# Deployment files must survive the Jekyll build; source-only files must not leak.
assert (ROOT / 'CNAME').read_text().strip() == 'leafyandme.com', 'Missing or incorrect CNAME'
assert (ROOT / '.nojekyll').is_file(), 'Missing .nojekyll'
for name in ('AGENTS.md', 'Gemfile', 'Gemfile.lock', 'README.md', 'scripts', '.github'):
    assert not (ROOT / name).exists(), f'Source-only file published: {name}'
print("Deployment files verified.")
