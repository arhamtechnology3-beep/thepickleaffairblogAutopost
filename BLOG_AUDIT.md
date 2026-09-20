# BLOG_AUDIT.md — Kitchen Tales content audit

Audit date: 2026-09-20  
Source: Shopify Admin API · Blog ID `96853164183` · Policy: `BLOG.md`

## Duplicate / Overlapping Pages

| URL | Title | Primary Topic | Intent | Words | Status |
|---|---|---|---|---|---|
| /blogs/kitchen-tales/sweet-mango-pickle-homemade-guide-the-pickle-affair | Sweet Mango Pickle Homemade Guide \| The Pickle Affair | sweet mango pickle / Meethi Keri | Commercial + informational | ~545 | **KEEP → UPDATE** into comprehensive Meethi Keri resource (BLOG.md §50) |
| /blogs/kitchen-tales/sweet-mango-pickle-homemade-guide-the-pickle-affair-20-sep | Sweet Mango Pickle Homemade Guide \| The Pickle Affair (20 Sep) | same | same | ~218 | **MERGE** into KEEP URL · unpublish |
| /blogs/kitchen-tales/katka-keri-pickle-how-to-store-and-serve-at-home-the-pickle-affair | Katka Keri Pickle: How To Store And Serve At Home | katka keri + storage | How-to / commercial | ~555 | **KEEP → UPDATE** (split intent: storage guide vs product guide) |
| /blogs/kitchen-tales/katka-keri-pickle-guide-the-pickle-affair-20-sep | Katka Keri Pickle Guide \| The Pickle Affair (20 Sep) | katka keri | Commercial | ~231 | **MERGE** · unpublish |
| /blogs/kitchen-tales/buy-gunda-keri-online-guide-the-pickle-affair | Buy Gunda Keri Online Guide \| The Pickle Affair | buy gunda keri | Transactional | ~541 | **KEEP → UPDATE** |
| /blogs/kitchen-tales/buy-gunda-keri-online-guide-the-pickle-affair-20-sep | Buy Gunda Keri Online Guide \| The Pickle Affair (20 Sep) | same | same | ~541 | **MERGE** · unpublish (dated duplicate from same-day republish) |
| /blogs/kitchen-tales/gujarati-keri-achar-guide-the-pickle-affair | Gujarati Keri Achar Guide \| The Pickle Affair | gujarati keri achar | Heritage / commercial | ~294 | **KEEP → UPDATE** (thin) |
| /blogs/kitchen-tales/gujarati-keri-achar-guide-the-pickle-affair-20-sep | Gujarati Keri Achar Guide \| The Pickle Affair (20 Sep) | same | same | ~541 | **MERGE** into undated URL or keep longer dated as canonical — prefer undated slug; merge body → undated · unpublish dated |
| /blogs/kitchen-tales/chana-keri-methi-pickle-guide-the-pickle-affair | Chana Keri Methi Pickle Guide \| The Pickle Affair | chana keri methi | Ingredient / commercial | ~302 | **KEEP → UPDATE** |
| /blogs/kitchen-tales/chana-keri-methi-pickle-guide-the-pickle-affair-20-sep | Chana Keri Methi Pickle Guide \| The Pickle Affair (20 Sep) | same | same | ~558 | **MERGE** into undated · unpublish dated |

## Canonical Recommendations

| Topic | Canonical URL | Action |
|---|---|---|
| Sweet mango pickle / Meethi Keri | `/blogs/kitchen-tales/sweet-mango-pickle-homemade-guide-the-pickle-affair` | Expand to §50 structure; later consider slug `sweet-mango-pickle-recipe-gujarati-meethi-keri` only with redirect |
| Katka Keri | `/blogs/kitchen-tales/katka-keri-pickle-how-to-store-and-serve-at-home-the-pickle-affair` | Keep as storage/serve; create separate product heritage page later if needed |
| Gunda Keri buying | `/blogs/kitchen-tales/buy-gunda-keri-online-guide-the-pickle-affair` | Strengthen buying-guide intent |
| Gujarati Keri Achar | `/blogs/kitchen-tales/gujarati-keri-achar-guide-the-pickle-affair` | Expand; merge dated duplicate |
| Chana Keri Methi | `/blogs/kitchen-tales/chana-keri-methi-pickle-guide-the-pickle-affair` | Expand; merge dated duplicate |

## Redirect Candidates

Shopify Online Store may not support free URL redirects on all plans. Prefer:
1. Unpublish thin duplicates
2. Add “This guide moved” note + link on unpublished pages if still crawlable
3. Use Shopify URL redirects admin when available for dated handles → undated handles

## Missing Topics (priority)

1. Ultimate Guide to Gujarati Pickles (pillar)
2. Chhundo vs Meethi Keri (comparison)
3. How to Store Indian / Gujarati Pickles
4. How Long Does Mango Pickle Last?
5. Traditional Kathiawadi Pickle-Making / Baa’s Kitchen
6. Pickle & Thepla / Khichdi pairings (dedicated)
7. Mustard oil / fenugreek / jaggery ingredient pages
8. Dedicated Chhundo guide (not only product card)

## Keyword Map

See `BLOG_REGISTRY.md`.

## Internal Linking Opportunities

- Every product guide → pillar (once published)
- Sweet mango ↔ Chhundo comparison ↔ Meethi Keri product
- Storage guide ↔ all product guides
- Pairing articles ↔ Heritage Recipes

## Thin Content

All current articles are template-like (~200–550 words), missing: answer-first block, genuine process depth, unique H1 in body, related articles, distinct intents across the daily mix.

## Metadata Issues

- Titles share pattern `… Guide | The Pickle Affair`
- Dated titles create near-duplicates
- Meta/summaries are formulaic
- No unique OG differentiation verified in this audit pass

## Schema Issues

- FAQPage JSON-LD present in bodies (OK if FAQs are genuine)
- Recipe schema must NOT be added until real recipe content exists
- Article/BlogPosting via theme `article-json-ld` — keep aligned with visible content

## Image Issues

- Product images reused as article images
- Need descriptive filenames/alt for editorial shots when available
- Do not invent AI packaging imagery

## Priority Fixes

1. Unpublish 5 dated near-duplicates (same-day cannibalization)
2. Expand Sweet Mango / Meethi Keri KEEP URL per §50
3. Publish pillar: Ultimate Guide to Gujarati Pickles
4. Replace daily generator with intent-mix + registry gate (`BLOG.md`)
5. Stop publishing 5 product-angle clones per day
