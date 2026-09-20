# Blog Autopost — CLI setup (do this in your Mac Terminal)

You do **not** need `npm init @shopify/app@latest`. Use the files in this folder.

## Option A — Fastest (same result as CLI deploy)

On the **Create version** page you have open:

1. **Scopes** — paste exactly:
   ```
   read_content,write_content
   ```
2. Uncheck **Embed app in Shopify admin** (optional; autopost is not an admin UI).
3. Leave App URL as-is, or set: `https://shopify.dev/apps/default-app-home`
4. Click **Release**

## Option B — Shopify CLI (from this folder)

```bash
cd "/Users/apple/Documents/Shopify Theme VS code/The Pickle Affair/blog-autopost"

# Refresh login if needed
shopify auth login --alias=cs@thepickleaffair.com

# Client ID (from install URL): e47ce2d8e254ca7eaf7a59dee082fd71
shopify app deploy \
  --auth-alias=cs@thepickleaffair.com \
  --client-id=e47ce2d8e254ca7eaf7a59dee082fd71 \
  --allow-updates \
  --message "Fix app URL + content scopes for blog autopost"
```

This replaces `example.com` with Shopify’s default app home and keeps scopes `read_content,write_content`.


## After Install — get token with Postman (not a permanent shpat_)

See **`POSTMAN-TOKEN.md`** and import `postman/Blog_Autopost.postman_collection.json`.

1. Dev Dashboard → Blog Autopost → Credentials → copy **Client secret**
2. Postman: POST `https://the-pickle-affair.myshopify.com/admin/oauth/access_token`
   - `grant_type` = `client_credentials`
   - `client_id` = `e47ce2d8e254ca7eaf7a59dee082fd71`
   - `client_secret` = (from dashboard)
3. Response `access_token` works in `X-Shopify-Access-Token` (~24h)

### GitHub secrets (preferred)

| Secret | Value |
|--------|--------|
| `SHOPIFY_CLIENT_ID` | `e47ce2d8e254ca7eaf7a59dee082fd71` |
| `SHOPIFY_CLIENT_SECRET` | from Dev Dashboard |

Do not paste the short-lived Postman token into GitHub — Actions refreshes it each run via `scratch/shopify_auth.py`.

Repo: https://github.com/arhamtechnology3-beep/thepickleaffairblogAutopost

## Then run Actions

**Actions → The Pickle Affair Daily Blog Publisher → Run workflow → both**

