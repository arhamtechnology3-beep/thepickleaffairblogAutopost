# Autopost — always-on

Kitchen Tales posts run on **GitHub Actions**. Your Mac can be offline.

## Keyword source (required)

Arham Foods keyword sheet is loaded as:

- `scratch/keyword_bank.json` (from *Arham Foods New Keywords with Comma*)
- Helper: `scratch/keyword_bank.py`

**Pillars:** Special Mango, Sweet Mango, Gor-Keri, Chana Keri, Gunda Keri, Aachar Masala, Sweet Lemon, Sweet Combo, Tangy Combo, 6 Combo.

Blogs (`topic_library.json`) and collections (`collection_library.json`) map to these pillars via `keyword_pillar` / `keyword_pillars`. Generators inject related phrases into copy — **one primary intent per URL**, no stuffing.

**Sweet Lemon:** demand keywords tracked for Kitchen Tales only until a lemon SKU exists (no empty lemon collection).

## Blogs (daily, random time)

Each day picks **3 random IST times** (~09:00–20:45). Default **3 posts/day** (staggered — one per slot).

- Body length gate: **≥1500 words**
- Each post targets **collection hubs + product pages** (`topic_library.json` + keyword bank)

## Collections (weekly, competitor-informed)

Homepick-style architecture without doorway spam:

- Library: `scratch/collection_library.json` (~25 intents including combo / achar-masala hubs)
- Action: **Weekly SEO Collections** (Mondays, up to 2 new queued hubs)
- Manual full sync: run with `batch=all` `limit=0`

Collection pages include intro, buying guidance, comparison, serving, FAQ, related collections + blogs + related keyword phrases from the bank.

## How to STOP blogs

```bash
gh workflow disable "The Pickle Affair Daily Blog Publisher" --repo arhamtechnology3-beep/thepickleaffairblogAutopost
```
