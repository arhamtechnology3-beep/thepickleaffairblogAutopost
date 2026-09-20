# Collections + Keyword + Blog Plan — The Pickle Affair

Policy: `BLOG.md` · `seo/SEO_AUTOPILOT.md` §14 · Do not create doorway pages. One primary intent per URL.

## Competitor study (2026-09-20)

| Competitor | Approx. collections | Patterns we learned |
|---|---|---|
| **Homepick** | ~27 | Broad hub, sweet/savoury silos, mango/ingredient silos, regional silos, festive/seasonal, bestsellers, combos |
| **Pasand** | ~7 | Pickles hub, customer favourites, combo packs, gift box |
| **Adani Spices** | thin pickle set | Single Pickles hub among spices — less educational depth |

**Market cadence:** Collections are SEO landing pages — expand **weekly (1–2 new intents)** after uniqueness checks, not 5 empty collections/day. Daily energy stays on **Kitchen Tales blogs** that target live collections + PDPs.

**We skip** competitor silos we cannot honestly fill (oil-free, Jain-only, lemon, Bengali, Punjabi, podi, murabba, etc.).

## Collection page mandatory content (from SEO_AUTOPILOT + competitor norms)

1. SEO title + meta  
2. H1 / clear title  
3. Unique body copy **400–600 useful words** target (floor **400** via `MIN_COLLECTION_WORDS`; single-product hubs may land ~700–900 with FAQs/links)  
4. Category explanation  
5. Buying guidance  
6. Product comparison  
7. Serving ideas  
8. FAQ (5–6+)  
9. Related collections  
10. Related blog links  
11. Real product membership (not Status=Active only)

### Word-count evidence (not Google law)

- Google has **no official minimum** word count for category pages (John Mueller: “very little” text can be enough).  
- Digitaloft 2025 study of 300 #1 UK ecommerce category pages: **average ~310 unique words**; most under 400.  
- Our floor **400** sits above that average with useful buying guidance — not blog-length stuffing (blogs stay ≥1500).

Source of truth: `blog-autopost/scratch/collection_library.json`

## Live + queued collections

See `collection_library.json` (20 planned intents). First 8 are live; remaining queue rolls out via **Weekly SEO Collections** Action (`COLLECTION_LIMIT=2` each Monday).

## Blog rules (aligned)

- Standard guide length: **≥1500 words** (`MIN_BLOG_WORDS`)
- Each post must link **collection hubs + product pages**
- Topics declare `collection_handles` + `product_handles` in `topic_library.json`
- Quality over quota — fewer posts OK if gates fail

## Footer

SHOP column points at primary SEO collections (not `/collections/all` stubs).
