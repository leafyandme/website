#!/usr/bin/env python3
"""Check built pages, SEO metadata, JSON-LD, and the zero-JavaScript contract."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '_site').resolve()
BASE = sys.argv[2] if len(sys.argv) > 2 else ''

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.headings, self.errors = [], set(), 0, []
        self.meta, self.canonicals, self.schemas = {}, [], []
        self.title, self.in_title, self.script = '', False, None
        self.feed(path.read_text())
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            if attrs != {'type': 'application/ld+json'}:
                self.errors.append('Unexpected executable or external script')
            self.script = []
        if any(key.startswith('on') for key in attrs):
            self.errors.append('Unexpected inline event handler')
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            self.meta[attrs.get('name', attrs.get('property', ''))] = attrs.get('content', '')
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href', ''))
        if tag == 'h1':
            self.headings += 1
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append('Duplicate id: ' + attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'img':
            if 'alt' not in attrs:
                self.errors.append('Image without alt text')
            if not all(attrs.get(key, '').isdigit() and int(attrs[key]) > 0 for key in ('width', 'height')):
                self.errors.append('Image without explicit positive dimensions')
        if attrs.get('srcset'):
            for candidate in attrs['srcset'].split(','):
                parts = candidate.split()
                if len(parts) != 2 or not re.fullmatch(r'[1-9][0-9]*w', parts[1]):
                    self.errors.append('Malformed responsive image candidate: ' + candidate)
                elif parts:
                    self.links.append(parts[0])
        for key in ('href', 'src'):
            if attrs.get(key):
                if urlsplit(attrs[key]).scheme.lower() == 'javascript':
                    self.errors.append('Unexpected JavaScript URL')
                self.links.append(attrs[key])
        if tag == 'meta' and attrs.get('property', attrs.get('name')) in ('og:image', 'twitter:image'):
            self.links.append(attrs.get('content', ''))

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.script is not None:
            self.script.append(data)

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'script' and self.script is not None:
            try:
                schema = json.loads(''.join(self.script))
                if not isinstance(schema, dict) or schema.get('@context') != 'https://schema.org':
                    self.errors.append('JSON-LD must use the Schema.org context')
                else:
                    self.schemas.append(schema)
            except (ValueError, TypeError):
                self.errors.append('Invalid JSON-LD')
            self.script = None

pages = {p: Page(p) for p in ROOT.rglob('*.html')}
errors = []
for required in ('index.html', 'support/index.html', 'privacy/index.html', 'credits/index.html', 'catalog-sources/index.html', '404.html'):
    if ROOT / required not in pages:
        errors.append('Missing page: ' + required)
for path, page in pages.items():
    errors.extend(f'{path.relative_to(ROOT)}: {e}' for e in page.errors)
    if page.headings != 1:
        errors.append(f'{path.name}: expected one h1, found {page.headings}')
    if re.search(r'\{%|\{\{', path.read_text()):
        errors.append(f'{path.name}: unrendered Liquid')
    relative = path.relative_to(ROOT).as_posix()
    route = '/' + relative.removesuffix('index.html') if relative.endswith('index.html') else '/' + relative
    canonical = 'https://leafyandme.com' + BASE + route
    if page.canonicals != [canonical]:
        errors.append(f'{relative}: expected one clean canonical: {canonical}')
    if not page.title.strip() or not page.meta.get('description', '').strip():
        errors.append(f'{relative}: missing title or description')
    if page.meta.get('og:title') != page.title.strip() or page.meta.get('og:url') != canonical:
        errors.append(f'{relative}: social metadata differs from page title or canonical')
    if page.meta.get('twitter:card') != 'summary_large_image':
        errors.append(f'{relative}: missing landscape Twitter card')
    noindex = 'noindex' in page.meta.get('robots', '').lower()
    if noindex != (relative == '404.html'):
        errors.append(f'{relative}: only the utility 404 document should be noindex')
    for labelled in re.findall(r'aria-labelledby="([^"]+)"', path.read_text()):
        for target in labelled.split():
            if target not in page.ids:
                errors.append(f'{relative}: missing accessible label target {target}')
    for link in page.links:
        url = urlsplit(link)
        if (url.scheme or url.netloc) and url.netloc != 'leafyandme.com':
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

public_pages = [p for path, p in pages.items() if path.name != '404.html']
for label, values in (
    ('title', [page.title.strip() for page in public_pages]),
    ('description', [page.meta.get('description', '') for page in public_pages]),
):
    if len(values) != len(set(values)):
        errors.append('Content pages must have unique ' + label + ' metadata')

home = pages.get(ROOT / 'index.html')
if home and len(home.schemas) == 1:
    nodes = {node.get('@type'): node for node in home.schemas[0].get('@graph', [])}
    if not {'WebSite', 'MobileApplication', 'Person'} <= nodes.keys():
        errors.append('Homepage schema must describe the website, application, and real creator')
    else:
        app = nodes['MobileApplication']
        if app.get('offers', {}).get('price') != '0' or not app.get('isAccessibleForFree'):
            errors.append('Application schema must match the visible free offer')
        if app.get('offers', {}).get('url') != app.get('downloadUrl') or 'apps.apple.com/' not in app.get('downloadUrl', ''):
            errors.append('Application offer must link to its App Store download')
        if nodes['Person'].get('name') != 'Tijme Gommers':
            errors.append('Application creator must match the App Store seller')
        if not app.get('screenshot') or not app.get('operatingSystem'):
            errors.append('Application schema must include screenshots and operating system')
        for image in [app.get('image', ''), *app.get('screenshot', [])]:
            parsed = urlsplit(image)
            image_path = unquote(parsed.path).removeprefix(BASE).lstrip('/')
            if parsed.scheme != 'https' or parsed.netloc != 'leafyandme.com' or not (ROOT / image_path).is_file():
                errors.append('Missing local application schema image: ' + image)
else:
    errors.append('Homepage must have exactly one valid JSON-LD graph')

try:
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    locations = [entry.text for entry in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    expected = [page.canonicals[0] for page in public_pages if len(page.canonicals) == 1]
    if sorted(locations) != sorted(expected):
        errors.append('Sitemap must contain each public page once, excluding the 404 document')
except (OSError, ET.ParseError):
    errors.append('Missing or invalid sitemap')

robots = (ROOT / 'robots.txt').read_text()
if 'Disallow: /' in robots or 'Sitemap: https://leafyandme.com' + BASE + '/sitemap.xml' not in robots:
    errors.append('Robots policy must permit crawling and reference the sitemap')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'Passed: {len(pages)} pages, links and responsive images, accessible labels, unique metadata, canonicals, sitemap, valid JSON-LD, no executable JavaScript.')

# Deployment files must survive the Jekyll build; source-only files must not leak.
assert (ROOT / 'CNAME').read_text().strip() == 'leafyandme.com', 'Missing or incorrect CNAME'
assert (ROOT / '.nojekyll').is_file(), 'Missing .nojekyll'
for name in ('AGENTS.md', 'Gemfile', 'Gemfile.lock', 'README.md', 'scripts', '.github'):
    assert not (ROOT / name).exists(), f'Source-only file published: {name}'
print("Deployment files verified.")
