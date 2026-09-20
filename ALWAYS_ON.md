# Autopost — always-on daily publishing

Kitchen Tales posts run on **GitHub Actions** (cloud). Your Mac does not need to be on.

## Status
- Workflow: **The Pickle Affair Daily Blog Publisher**
- Schedule: **every day ~09:05 IST** (max 5 quality posts; fewer if gates block)
- Secrets required: `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET`

## How to STOP (manual)

1. Open https://github.com/arhamtechnology3-beep/thepickleaffairblogAutopost/actions  
2. Click **The Pickle Affair Daily Blog Publisher**  
3. Click **⋯** → **Disable workflow**

Or pause via CLI:
```bash
gh workflow disable "The Pickle Affair Daily Blog Publisher" --repo arhamtechnology3-beep/thepickleaffairblogAutopost
```

Re-enable:
```bash
gh workflow enable "The Pickle Affair Daily Blog Publisher" --repo arhamtechnology3-beep/thepickleaffairblogAutopost
```

## Manual run anytime
Actions → Daily Blog Publisher → **Run workflow** → mode `both`

## Policy
See `BLOG.md` — quality over volume; no duplicate intents.
