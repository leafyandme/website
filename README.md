# Leafy & Me website

A Jekyll website for the Leafy & Me iPhone and iPad plant care app. Bootstrap 5.3.8 provides the responsive layout. Navigation, FAQs, and automatic light/dark appearance work with **zero executable JavaScript**. Static JSON-LD describes the app, website, and creator without running code. CSS, photographs, app screenshots, and icons are served locally; fonts use the operating system’s font stack.

## Run locally

Install Ruby 3.2 or later with Bundler, then:

```sh
bundle install
bundle exec jekyll serve --baseurl ""
```

Open http://localhost:4000. `--baseurl ""` serves at the root during development.

## Build

```sh
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter
python3 scripts/check_site.py
python3 scripts/test_check_site.py
git diff --check
```

Upload the generated `_site/` directory to your static host. The checked-in configuration targets **https://leafyandme.com**, matching the app’s intended URLs. `/support/` and `/privacy/` are directory URLs; hosts should redirect their slashless equivalents or serve the directory index. Configure the host’s missing-page handler to use `404.html`.

For another domain or subdirectory deployment, change `url` and `baseurl` in `_config.yml` before building. All internal assets and navigation use Jekyll’s URL filters. `robots.txt` is effective only at a domain’s root; add the generated sitemap URL to the parent site’s robots file when publishing beneath a subdirectory.

## Content and release settings

- `_config.yml`: site URL, public website source, creator, support email, minimum iOS version, catalog count, and App Store URL.
- `index.html` and `_data/features.yml`: homepage sections and feature copy.
- `support.html`: help articles and email support, available without repository access or a GitHub account.
- `privacy.md`: policy covering Leafy & Me’s private iCloud sync and exported backups, email support, and this website’s data handling.
- `assets/css/main.css`: visual design and CSS system-appearance media query.
- `_includes/` and `_layouts/`: shared menu, footer, inline SVG icons, and page shells.
- `credits.md`: creator attribution and license links for the three reused plant photos.
- `catalog-sources.md`: accessible catalog methodology and all 206 reference-photo credits, including photographs visible in app screenshots.
- `_includes/structured-data.html`: homepage WebSite, Person, and MobileApplication JSON-LD. Keep the free offer, device requirements, and creator consistent with visible copy and the App Store listing. Do not add ratings or reviews without real evidence; Schema.org validity does not guarantee Google software-app rich results.
- `llms.txt`: optional summary and official content links; it is not required for search indexing.

The website links to the App Store listing configured in `_config.yml`. Private iCloud sync is conditional on a version offering Enable Private iCloud Sync in Settings, and requires explicit opt-in. The repository has both Local and Cloud configurations, but CI compile proof does not establish which version was published or validate production CloudKit provisioning. Do not promise sync availability in every downloaded version without checking the shipped app. Export Collection provides separate snapshot backups, including to iCloud Drive; sync itself also propagates deletions. Keep support and privacy wording aligned with the app when storage behavior changes.

The homepage’s care note is an editorial illustration. The separate screenshot gallery uses the actual iPhone Plants, Care, and Catalog images published in the App Store listing, retrieved on 27 October 2026 at 642 × 1389. These are public example collections, not user-provided private photos. Refresh them when the shipped UI changes; do not synthesize app screens. Original plant-photo files are retained alongside resized WebP variants. CSS crops the three standalone photographs and lowers their brightness in dark mode. Attribution and transformation notices are in the footer-linked credits pages.

Run `sh scripts/generate_images.sh` from the repository root to regenerate responsive images, small icons, and the 1200 × 630 social preview. This requires ImageMagick 7 and Fontconfig, only for asset maintenance. The preview uses installed fonts; website fonts remain system fonts. The checked-in JPEG screenshots are the inputs for their WebP variants. Build and deployment do not require image tools.

The site checker validates rendered titles, descriptions, canonicals, the sitemap, noindex on the 404 document, accessible label references, and every responsive-image candidate. Only inline `application/ld+json` is allowed in a script element; executable scripts, external scripts, event handlers, and JavaScript URLs are rejected. Regression tests exercise that exception and the image/indexing safeguards.

Before publishing, check the deployment URL and the hosting provider’s actual logging practices against the website section of the privacy policy. The site itself does not include analytics, trackers, cookies, forms, or local storage.

The site is branded **Leafy & Me** and targets the root of `https://leafyandme.com`. Public source links point to `leafyandme/website`. The application repository and its issues returned 404 anonymously on 27 October 2026, so they are not offered as public support destinations. Check any replacement support link while signed out. Changing the Jekyll configuration does not publish the site or modify DNS.

## Branches and production deployment

Work, commit, and push only on `develop`. The owner merges into `main` to release. `main` and `develop` share a fresh initial commit. `gh-pages` is a separate generated-output branch created automatically by the deployment workflow; it contains the compiled site, `CNAME`, and `.nojekyll`. Do not commit source edits to `main` or generated output to `gh-pages` manually.

`.github/workflows/check.yml` builds and validates pushes to `develop` and pull requests to `develop` or `main`. `.github/workflows/deploy.yml` runs only for pushes to `main`, or a manual retry selected on `main`. It builds with pinned actions and Ruby 3.3, validates the result, pushes it to `gh-pages`, and deploys the identical output through the official Pages artifact actions. It uses only `GITHUB_TOKEN`; no personal access token or deploy key is required.

**When you are ready to publish:**

1. Make the repository public (or use a GitHub plan that supports Pages for the private repository).
2. In **Settings → Pages → Build and deployment**, choose **GitHub Actions** as the source. The workflow keeps `gh-pages` as a compiled-output branch, but explicitly deploys the artifact because pushes made with `GITHUB_TOKEN` do not trigger another Pages build.
3. In Pages settings, set the custom domain to **leafyandme.com**. The committed `CNAME` is included in every build, but Actions deployments also need the custom domain configured in Pages settings.
4. Point your domain's DNS to GitHub Pages using GitHub's custom-domain instructions, and enable **Enforce HTTPS** once GitHub has issued the certificate. No DNS or repository visibility changes are performed by this source setup.
5. Merge `develop` into `main`. Check **Actions → Deploy website**. If Pages was not enabled for the first run, rerun that workflow on `main` after configuring it. If deployment branch restrictions are enabled for the `github-pages` environment, allow `main`.

Reference: [GitHub Pages publishing sources](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and [custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site).

The website does not use semantic versions or build numbers. App versioning is maintained separately in the application repository.
