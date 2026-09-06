# ahnafakif.com — consulting site

Single-page static site. No build step, no dependencies.

- `index.html` — the whole site; photographs embedded as base64 data URIs
- `portrait.jpg` — referenced only by the `og:image` meta tag
- `favicon.svg` — tab icon

## Deploy

Any static host. Upload the folder as-is.

GitHub Pages: push to `main`, then Settings → Pages → Source: `main` / root.
