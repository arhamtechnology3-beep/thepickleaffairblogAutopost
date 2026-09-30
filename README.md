# The Pickle Affair — Daily Blog Autopost

Publishes **3 SEO blog posts per day** to Kitchen Tales on [thepickleaffair.com](https://thepickleaffair.com/blogs/kitchen-tales).

## Skip `npm init @shopify/app@latest`

That Partner command builds a full Node app. **Not needed.**

Use **`SETUP-CLI.md`** for:
- filling scopes on the Dev Dashboard **Create version** screen, or
- `shopify app config link` + `shopify app deploy`

This repo uses **Python + GitHub Actions**. The GitHub secret still needs a store **Admin API access token** (`shpat_…`) from **Develop apps** (see SETUP-CLI.md).

## 1. Create Admin API token

1. Open: https://the-pickle-affair.myshopify.com/admin
2. **Settings → Apps and sales channels → Develop apps**
3. Allow custom app development if prompted
4. **Create an app** → name: `Blog Autopost`
5. **Configure Admin API scopes** → enable:
   - `read_content`
   - `write_content`
6. **Save** → **Install app**
7. Copy **Admin API access token** (`shpat_…`) — shown once

If you are on [dev.shopify.com](https://dev.shopify.com/dashboard) Apps page: use **Create app** only if you prefer a Partner app, then install it on the store and copy the Admin API token. Still **do not** run `npm init @shopify/app@latest`.

## 2. GitHub secret

Repo → **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|--------|
| `SHOPIFY_ACCESS_TOKEN` | `shpat_…` from step 1 |

## 3. Enable the workflow

After the workflow file is on `main`, go to **Actions** → *The Pickle Affair Daily Blog Publisher* → **Run workflow** → mode `both`.

Schedule (IST): ~09:05, 11:05, 14:05, 17:05, 19:35.

## 4. Update products / keywords

Edit `scratch/product_registry.json`, commit, push.

## Featured images (new image per post)

Every new post gets its own 1600×900 featured image (`scratch/blog_image.py`):

- The **real product photo** is cut out of its white background and placed as-is — only scaled, never recoloured or redrawn — so jar colour, shape, label and packaging stay exactly like the product.
- Only the **scene around the jar** is new, in brand colours (cream, leaf green `#4A6B29`, mango, turmeric, terracotta) and matched to the topic (storage, pairing, ingredient…) plus the pickle's ingredients (`scene_props` in `product_registry.json`).
- AI backgrounds, tried in order:
  1. **Cloudflare Workers AI** (FLUX.2 klein at native 16:9, falling back to FLUX.1 schnell; free daily tier of 10,000 neurons, ~160 per image): GitHub secrets `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN`. Optional repo variable `CLOUDFLARE_IMAGE_MODEL` overrides the model.
  2. **OpenAI** (`gpt-image-1`, paid credits): GitHub secret `OPENAI_API_KEY`.
  3. Otherwise a procedural brand scene. Any failure falls back to the next option and never blocks a publish.
- Repo variable `BLOG_IMAGE_PROVIDER`: `auto` (default) · `cloudflare` · `openai` · `local` · `off` (old behaviour: raw product photo).

Preview locally: `pip install -r requirements.txt && python3 scratch/blog_image.py pickle-thepla --out preview.jpg`

## Local test

```bash
export SHOPIFY_ACCESS_TOKEN=shpat_xxx
export SHOPIFY_SHOP_URL=https://the-pickle-affair.myshopify.com
export SHOPIFY_BLOG_ID=96853164183
python3 scratch/generate_daily_blogs.py
```

## Files

| Path | Role |
|------|------|
| `scratch/product_registry.json` | Products + focus keywords |
| `scratch/generate_daily_blogs.py` | Create today's 5 posts |
| `scratch/blog_image.py` | Unique featured image per post |
| `scratch/daily_publish_daemon.py` | Publish drafts if needed |
| `.github/workflows/daily_blog_publisher.yml` | Schedule + manual run |

## Always-on daily posting

See [ALWAYS_ON.md](ALWAYS_ON.md) — runs on GitHub Actions every day until you disable the workflow.
