# Abhishek Singh — Portfolio

A single-page personal portfolio. **Pure HTML + CSS + JavaScript — no build step, no
dependencies.** Whatever is in this folder is the finished website.

```
portfolio/
├── index.html   ← all the content (text, links, projects)
├── styles.css   ← all the design (colors, fonts, animations)
├── script.js    ← interactions (cursor, menu, reveals, copy-email)
└── README.md    ← this file
```

Open `index.html` in a browser and it just works.

---

## 🚀 Hosting — pick one (all free)

### Option 1 — GitHub Pages (recommended: you already use GitHub)

Your site ends up at `https://abhi-aks.github.io/portfolio/` and updates every time
you push. Recruiters can also see the repo — bonus.

1. Copy this `portfolio` folder somewhere outside the StudyBridge repo, e.g. `D:\portfolio`.
2. Open a terminal in that folder and run:
   ```bash
   git init
   git add .
   git commit -m "Portfolio v1"
   ```
3. Create a new **public** repo on github.com named `portfolio` (no README, keep it empty).
4. Connect and push (replace nothing — your username is already in the URL):
   ```bash
   git remote add origin https://github.com/abhi-aks/portfolio.git
   git branch -M main
   git push -u origin main
   ```
5. On GitHub: **Settings → Pages → Branch: `main` / `(root)` → Save.**
6. Wait ~1 minute. Your site is live at `https://abhi-aks.github.io/portfolio/`.

> 💡 Name the repo `abhi-aks.github.io` instead and the site lives at
> `https://abhi-aks.github.io/` — the cleanest possible free URL.

### Option 2 — Netlify Drop (fastest: 60 seconds, no git)

1. Go to <https://app.netlify.com/drop>
2. Drag the whole `portfolio` folder onto the page.
3. Done. You get a URL like `https://random-name.netlify.app`
   (rename it under **Site settings → Change site name**, e.g. `abhishek-singh.netlify.app`).

Downside: to update the site you drag the folder again (or connect the GitHub repo later).

### Option 3 — Vercel (nice if you later move to Next.js)

1. Push the folder to GitHub (steps from Option 1).
2. Go to <https://vercel.com>, sign in with GitHub, **Import** the repo.
3. Framework preset: **Other**. Deploy. Live at `https://portfolio-xxx.vercel.app`.

### Custom domain later (optional, ~€10/year)

Buy `abhisheksingh.dev` / `abhi.codes` / similar at **Porkbun** or **Namecheap**, then in
GitHub Pages / Netlify / Vercel settings add the domain and follow the DNS instructions
shown there. HTTPS is automatic on all three.

---

## ✏️ Editing content

Everything lives in `index.html` — search for the text you want to change.

| What                      | Where in `index.html`                          |
| ------------------------- | ---------------------------------------------- |
| Headline / intro          | `<section class="hero">`                       |
| Projects                  | the three `<article class="project">` blocks   |
| About text & principles   | `<section id="about">`                         |
| Skills chips              | `<section id="stack">`                         |
| Email & social links      | `<section id="contact">` and `<div class="menu">` |
| Accent colors, fonts      | `:root { … }` at the top of `styles.css`       |

## ✅ TODO before sharing widely

- [ ] **LinkedIn:** the LinkedIn link in the Contact section points to `#` —
      replace it with your real profile URL (search for `TODO` in `index.html`).
- [ ] **Text-to-SQL repo:** push the `D:\texttosql` project to GitHub and update the
      two `https://github.com/abhi-aks` links on that project card to the real repo URL.
- [ ] Optional: add a real Open Graph image (`og:image` meta tag) so links preview
      nicely on LinkedIn/WhatsApp — a 1200×630 screenshot of the hero works great.
