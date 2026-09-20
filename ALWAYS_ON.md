# Autopost — always-on

Kitchen Tales posts run on **GitHub Actions**. Your Mac can be offline.

## Blogs (daily, random time)

Each day picks a **random IST time** (~09:00–20:45). Default **1 post/day**.

- Body length gate: **≥1500 words**
- Each post targets **collection hubs + product pages** (`topic_library.json`)

## Collections (weekly, competitor-informed)

Homepick-style architecture without doorway spam:

- Library: `scratch/collection_library.json` (~20 intents)
- Action: **Weekly SEO Collections** (Mondays, up to 2 new queued hubs)
- Manual full sync: run with `batch=all` `limit=0`

Collection pages include intro, buying guidance, comparison, serving, FAQ, related collections + blogs.

## How to STOP blogs

```bash
gh workflow disable "The Pickle Affair Daily Blog Publisher" --repo arhamtechnology3-beep/thepickleaffairblogAutopost
```
