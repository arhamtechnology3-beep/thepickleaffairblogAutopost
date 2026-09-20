# Get access token with Postman (Dev Dashboard app)

Your grant/install URL already has the Client ID:

`client_id=e47ce2d8e254ca7eaf7a59dee082fd71`

Dev Dashboard apps **do not show a permanent `shpat_`**. You create a short-lived Admin API token with **client_credentials** (Postman or curl). Tokens last ~**24 hours**.

## Prerequisites

1. App **installed** on the store (you already did Install on the grant page).
2. Scopes include `read_content,write_content` (released version).
3. **Client secret** from Dev Dashboard → **Blog Autopost** → **Settings / Credentials**.

## Postman steps

1. Import `postman/Blog_Autopost.postman_collection.json`
2. Collection variables:
   - `client_id` = `e47ce2d8e254ca7eaf7a59dee082fd71`
   - `client_secret` = paste from Dev Dashboard
   - `shop` = `the-pickle-affair.myshopify.com`
3. Run **1. Get Admin API access token**
4. Response looks like:
   ```json
   {
     "access_token": "shpat_… or shp…",
     "scope": "read_content,write_content",
     "expires_in": 86399
   }
   ```
5. Run **2. Smoke test** — should list Kitchen Tales articles.

## Equivalent curl

```bash
curl -s -X POST "https://the-pickle-affair.myshopify.com/admin/oauth/access_token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=e47ce2d8e254ca7eaf7a59dee082fd71" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

## GitHub Actions (recommended — no manual token copy)

Do **not** paste the short-lived Postman token into GitHub.

Add these **secrets** instead (Actions refreshes the token every run):

| Secret | Value |
|--------|--------|
| `SHOPIFY_CLIENT_ID` | `e47ce2d8e254ca7eaf7a59dee082fd71` |
| `SHOPIFY_CLIENT_SECRET` | from Dev Dashboard Credentials |

Workflow already uses them via `scratch/shopify_auth.py`.

## If Postman returns `shop_not_permitted`

Store and app must be in the **same Shopify organization**, and the app must be **installed**. Re-open the grant URL and click Install, then retry.
