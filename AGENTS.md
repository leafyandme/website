# Leafy & Me website conventions

- Work on `develop`. Commit and push validated changes only to `origin/develop`.
- The owner merges `develop` into `main`. Never merge or push source changes to `main` on the owner's behalf unless explicitly requested.
- `gh-pages` is generated output managed by the deployment workflow. Do not edit or push it manually after initial branch setup.
- The website has no semantic version or build number. Do not add release metadata or version-bump requirements; app versioning is managed separately.
- Run `JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter`, `python3 scripts/check_site.py`, and `git diff --check` before committing. Report checks that could not run.
- Keep the site JavaScript-free, responsive, and compatible with system light/dark appearance.
- Keep support and privacy wording consistent with the app's actual behavior. All assets are served locally and plant image attribution must be retained.
