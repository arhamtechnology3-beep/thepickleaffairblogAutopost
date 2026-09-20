# Autopost — always-on (random time each day)

Kitchen Tales posts run on **GitHub Actions**. Your Mac can be offline.

## Schedule

Each calendar day picks a **random IST time** between ~09:00 and ~20:45.
The workflow checks every 30 minutes and publishes **only when that slot is due** — so posts are not batched at the same timestamp.

- Default: **1 post/day** at that random time
- Quality gates may skip the day (0 posts) if no unique topic

## How to STOP

Actions → **The Pickle Affair Daily Blog Publisher** → **⋯** → **Disable workflow**

```bash
gh workflow disable "The Pickle Affair Daily Blog Publisher" --repo arhamtechnology3-beep/thepickleaffairblogAutopost
```

## Manual run

Use `force=1` to publish immediately (ignore waiting for the random slot).
