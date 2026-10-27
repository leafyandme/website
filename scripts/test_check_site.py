#!/usr/bin/env python3
"""Exercise the JSON-LD exception and the responsive-image/indexing safeguards."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]


class SiteCheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='leafy-site-check-')
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name) / 'site'
        shutil.copytree(REPO / '_site', self.site)

    def check_site(self):
        return subprocess.run(
            [sys.executable, str(REPO / 'scripts/check_site.py'), str(self.site)],
            capture_output=True, text=True, check=False,
        )

    def edit(self, path, before, after):
        target = self.site / path
        text = target.read_text()
        self.assertIn(before, text)
        target.write_text(text.replace(before, after, 1))

    def assert_rejected(self, message):
        result = self.check_site()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(message, result.stdout + result.stderr)

    def test_inline_json_ld_is_allowed_without_executable_javascript(self):
        result = self.check_site()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_executable_scripts_are_rejected(self):
        self.edit('index.html', '</head>', '<script>alert(1)</script></head>')
        self.assert_rejected('Unexpected executable or external script')

    def test_json_ld_must_be_inline_and_valid_json(self):
        self.edit('index.html', '<script type="application/ld+json">',
                  '<script type="application/ld+json" src="https://example.com/data.json">')
        self.assert_rejected('Unexpected executable or external script')

    def test_malformed_json_ld_is_rejected(self):
        self.edit('index.html', '"@graph": [', '"@graph": INVALID [')
        self.assert_rejected('Invalid JSON-LD')

    def test_inline_event_handlers_are_rejected(self):
        self.edit('index.html', '<body>', '<body onload="alert(1)">')
        self.assert_rejected('Unexpected inline event handler')

    def test_missing_srcset_candidate_is_rejected(self):
        (self.site / 'assets/images/rubber-plant-400.webp').unlink()
        self.assert_rejected('missing target /assets/images/rubber-plant-400.webp')

    def test_404_document_cannot_be_indexable(self):
        self.edit('404.html', '<meta name="robots" content="noindex, follow">', '')
        self.assert_rejected('only the utility 404 document should be noindex')


if __name__ == '__main__':
    unittest.main()
