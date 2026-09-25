# Leafy & Me website

A Jekyll website for the Leafy & Me iPhone and iPad plant care app. Bootstrap 5.3.8 provides the responsive layout. Navigation, FAQs, and automatic light/dark appearance work with **zero JavaScript**. Bootstrap CSS, photographs, and the app icon are served locally; fonts use the operating system’s font stack.

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
```

Upload the generated `_site/` directory to your static host. The checked-in configuration targets **https://leafyandme.com**, matching the app’s intended URLs. `/support/` and `/privacy/` are directory URLs; hosts should redirect their slashless equivalents or serve the directory index. Configure the host’s missing-page handler to use `404.html`.

For another domain or subdirectory deployment, change `url` and `baseurl` in `_config.yml` before building. All internal assets and navigation use Jekyll’s URL filters. `robots.txt` is effective only at a domain’s root; add the generated sitemap URL to the parent site’s robots file when publishing beneath a subdirectory.

## Content and release settings

- `_config.yml`: site URL, GitHub URLs, support email, minimum iOS version, catalog count, and App Store URL.
- `index.html` and `_data/features.yml`: homepage sections and feature copy.
- `support.html`: help articles and the direct GitHub new-issue link.
- `privacy.md`: policy covering Leafy & Me’s private iCloud sync and exported backups, including email support, optional public GitHub issues, and this website’s data handling.
- `assets/css/main.css`: visual design and CSS system-appearance media query.
- `_includes/` and `_layouts/`: shared menu, footer, inline SVG icons, and page shells.
- `credits.md`: creator attribution and license links for the three reused plant photos.

The website links to the App Store listing configured in `_config.yml` and describes the iCloud-capable app. Private iCloud sync is enabled explicitly in Settings. Export Collection provides separate snapshot backups, including to iCloud Drive; sync itself also propagates deletions. Keep support and privacy wording aligned with the app when storage behavior changes.

The homepage’s care note is an editorial illustration, not an app screenshot. The photos are taken from the app’s licensed offline catalog. Original source files are retained without additional file transformations; CSS crops them and lowers brightness in dark mode. Attribution is in the site’s footer-linked credits page.

Before publishing, check the deployment URL and the hosting provider’s actual logging practices against the website section of the privacy policy. The site itself does not include analytics, trackers, cookies, forms, or local storage.

The site is branded **Leafy & Me** and targets the root of `https://leafyandme.com`. App links point to `leafyandme/application`; the website repository is `leafyandme/website`. The domain must be registered and connected to your chosen host separately; changing the Jekyll configuration does not publish the site or modify DNS.

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
