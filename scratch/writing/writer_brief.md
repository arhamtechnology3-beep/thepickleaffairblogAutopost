# Kitchen Tales topic writing brief (The Pickle Affair)

Repo: `/Users/apple/Documents/Shopify Theme VS code/The Pickle Affair/blog-autopost`
Brand: **The Pickle Affair** (a brand of Arham Foods) — traditional Gujarati / Kathiawadi pickles
(achar / athanu) made the "Baa's kitchen" way. Site: thepickleaffair.com, blog "Kitchen Tales".
Goal: genuinely useful, people-first articles that rank on Google for the topic's primary keyword
and gently lead readers to the products. Indian English. Warm, practical, specific.

## Data you must read first
- `scratch/topic_library.json` → `topics` list. Study these PUBLISHED, fully written examples
  closely and match their depth, structure and tone exactly:
  `jaggery-in-pickle`, `white-layer-on-pickle`, `should-pickle-be-refrigerated`,
  `achar-for-paratha`, `gunda-vs-katka-keri`.
- `scratch/product_registry.json` → the ONLY valid `product_handles` (7 products) and their real names.
- Valid `collection_handles` (live collection pages):
  all-mango-pickles, sweet-gujarati-pickles, spicy-traditional-keri-achar, gunda-keri-specialty-achar,
  methi-fenugreek-pickles, kathiawadi-homemade-pickles, pickles-for-thepla-tiffin,
  buy-gujarati-pickle-online, gujarati-achar, all-pickles, customer-favourites, festive-gifting-pickles,
  chhundo-pickles, gor-keri-jaggery-pickles, homemade-mango-pickle, pickle-with-khichdi-dal,
  saurashtra-kathiawadi-achar, meethi-keri-sweet-mango, katka-keri-pickles, fssai-handmade-pickles,
  gujarati-pickle-combo-pack, raw-tender-mango-pickle

## Topic object schema (all fields required)
```
id, primary_keyword, title (<= 70 chars, contains the keyword naturally), intent, cluster, category,
angle, keyword_pillar, product_handles (2-3), collection_handles (2), excerpt (<= 155 chars),
quick_answer (2-4 sentences, directly answers the search query),
sections: 9-12 items, each {"h2": str, and "p": [paragraphs] and/or "list": [items], optional "ordered": true},
faqs: 5-7 items, each [question, answer],
conclusion (2-3 sentences)
```
- `category` ∈ Heritage Recipes, Health & Spices, Buying Guides, Pickle Pairings, Artisanal Craft, Pickle Guides
- `angle` ∈ storage, shelf_life, ingredient, pairing, comparison, baa_story, buying, heritage_product
- `intent` ∈ Informational, Serving/pairing, Ingredient/spice education, Commercial investigation, Comparison, How-to, Heritage/story
- `keyword_pillar`: reuse a value already used in topic_library.json that fits.
- Do NOT include a `draft` key.

## Length / quality bar (hard requirements)
- **1,150–1,300 words of unique text per topic** counted across quick_answer + all section h2/p/list +
  faqs + conclusion (the published examples sit at ~1,200).
- Every section must add new, concrete, useful information (how-to steps, what to look for, serving
  ideas, regional context, mistakes to avoid, comparisons). No padding, no repeating the same point,
  no generic marketing fluff, no keyword stuffing (use the primary keyword ~3-5 times naturally).
- Mention specific relevant products by their real names where natural (1-3 mentions), never pushy.

## Accuracy rules (very important — this is a food business)
- Never invent numbers: no prices, discounts, shelf-life months, delivery days, calorie/sodium figures,
  percentages, years of history, customer counts. Say "follow the label" / "check the jar" instead.
- No medical or health-cure claims (no "boosts immunity", "cures", "good for diabetes", pregnancy advice).
  Keep any health mention general and cautious ("enjoy in small portions as part of a balanced meal").
- Allowed brand facts only: The Pickle Affair is a brand of Arham Foods; packed in Maharashtra under
  FSSAI licence 21521053000490; traditional Kathiawadi recipes; small batches; no synthetic colours.
  Do not claim international shipping, specific oils/ingredients for a product unless the product
  name/registry says so (e.g. don't assert a product uses groundnut oil).
- Write about traditions accurately and respectfully (Gujarati/Kathiawadi food culture).
- Use straight ASCII apostrophes or typographic ones consistently with the examples; the content is
  inserted as HTML text, so do not include HTML tags or markdown in strings.

## Output
Write a JSON **array** of the finished topic objects to the output file named in your task
(e.g. `scratch/_new_X.json`). Do NOT edit `scratch/topic_library.json` or any other repo file.

Then validate:
```
cd "/Users/apple/Documents/Shopify Theme VS code/The Pickle Affair/blog-autopost"
python3 scratch/writing/validate_topics.py scratch/_new_X.json
```
Fix and re-run until every topic prints OK. Final reply: one line per topic with id, unique words,
built words, and OK/FAIL.
