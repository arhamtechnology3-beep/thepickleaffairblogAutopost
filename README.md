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
| `scratch/daily_publish_daemon.py` | Publish drafts if needed |
| `.github/workflows/daily_blog_publisher.yml` | Schedule + manual run |

## Always-on daily posting

See [ALWAYS_ON.md](ALWAYS_ON.md) — runs on GitHub Actions every day until you disable the workflow.
