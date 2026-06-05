# ELBO.INK — deploy guide

This folder is your whole website. `index.html` is the site; `images/` is where the
tattoo photos will go later; `.nojekyll` just tells GitHub to serve the files as-is.

---

## Option A — GitHub Pages (what you asked for)

1. On GitHub, click **New repository**. Name it `elbo-ink`, keep it **Public**, create it.
2. On the new repo page, click **Add file → Upload files**. Drag in everything from this
   folder (`index.html`, the `images` folder, `.nojekyll`). Commit.
3. Go to **Settings → Pages**. Under **Source**, pick **Deploy from a branch**,
   branch **main**, folder **/ (root)**. Save.
4. Wait ~1 minute. Your site is live at:
   `https://YOUR-USERNAME.github.io/elbo-ink/`

### Prefer the command line? From inside this folder:
```
git init
git add .
git commit -m "ELBO.INK site"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/elbo-ink.git
git push -u origin main
```
Then do step 3 above.

---

## Option B — Netlify / Cloudflare Pages (no GitHub needed)

Go to netlify.com (or Cloudflare Pages), find the **drag-and-drop deploy** box, and drop
this whole folder onto it. Live in seconds. Add your custom domain from the dashboard.

---

## Connecting the domain (e.g. elbo.ink)

**On GitHub Pages:** Settings → Pages → **Custom domain** → type `elbo.ink` → Save.
Then at your domain registrar, add these DNS records:

- Four **A** records for the apex (`elbo.ink`), all pointing to GitHub:
  `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
- One **CNAME** record for `www` → `YOUR-USERNAME.github.io`

Back on GitHub, tick **Enforce HTTPS** once it's available (can take a few minutes to an hour).

**On Netlify/Cloudflare:** just add the domain in the dashboard and follow their DNS prompts —
they walk you through it automatically.

---

## Still to do

- **Photos:** the gallery currently shows placeholder tiles. Send the photos and they drop
  straight into `images/` and the grid.
- **Copy:** the bio and the `[LOCATION]` / `[EMAIL]` fields are placeholders — fill those in
  (search the code for those markers).

Static sites are easy to update: change the files, re-upload (or `git push` again), done.
