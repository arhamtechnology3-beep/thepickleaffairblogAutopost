# THE PICKLE AFFAIR — SEO COLLECTION + PRODUCT + BLOG AUTOPILOT
## Master execution plan for Cursor

> Goal: Build a scalable, people-first SEO system for The Pickle Affair that creates useful collection pages, product SEO, and supporting blog content around the actual products. The system must avoid keyword stuffing, duplicate pages, fake search-volume claims, copied competitor content, and low-value mass-generated articles.

---

# 1. BUSINESS / SEO OBJECTIVE

Primary website:
- https://thepickleaffair.com/

Business:
- Traditional / Gujarati / Saurashtra-style Indian pickles
- Ecommerce / Shopify
- Core product themes visible in the current Shopify catalog:
  1. Chhundo / Sweet Shredded Mango Pickle
  2. Gunda Keri / Lasoda ka Achar
  3. Meethi Keri / Sweet Mango Achar
  4. Chana Keri Methi Achaar
  5. Homemade Mango Pickle / Aam ka Achar
  6. Gor Keri / Jaggery Mango Achar
  7. Katka Keri Pickle / Homemade Gujarati Pickle

Important:
- Before publishing anything, Cursor MUST read the live Shopify product/catalog data and use the exact current product names, handles, prices, sizes, ingredients, claims, availability and images.
- Never invent ingredients, health benefits, origin stories, awards, certifications, shelf life, manufacturing processes or customer claims.
- Never alter product/brand identity.

---

# 2. IMPORTANT GOOGLE SEO RULE

This project is NOT "publish thousands of pages for keywords."

Google currently warns against:
- scaled content created primarily to manipulate rankings
- keyword stuffing
- doorway pages
- substantially similar pages created only for search variations
- copied/scraped competitor content

Therefore:

Every collection/product/blog page must have a distinct user purpose and genuinely useful information.

Reference:
- Google Search Essentials: https://developers.google.com/search/docs/essentials
- Google Spam Policies: https://developers.google.com/search/docs/essentials/spam-policies
- Google Ecommerce Site Structure: https://developers.google.com/search/docs/specialty/ecommerce/help-google-understand-your-ecommerce-site-structure
- Google Product Structured Data: https://developers.google.com/search/docs/appearance/structured-data/product

Do NOT create pages such as:
- /mango-pickle-mumbai
- /mango-pickle-delhi
- /mango-pickle-pune
- /mango-pickle-ahmedabad

unless each page has a real, unique customer purpose and substantially different useful content.

---

# 3. KEYWORD DEMAND MODEL

Do NOT fabricate monthly search volume.

Public web research indicates strong recurring search themes around:
- mango pickle
- aam ka achar
- homemade mango pickle
- Gujarati pickle
- sweet mango pickle
- Chhundo / Chhunda / Chundo
- Gunda Keri / Gunda pickle / Lasoda ka achar
- jaggery mango pickle / Gor Keri
- Methia / Methi mango pickle

Examples of the current SERP landscape show competitors and publishers using variants such as:
- "Gunda Keri Pickle"
- "Lasode ka Achar"
- "Chhundo"
- "Sweet Mango Pickle"
- "Gorkeri"
- "Gujarati Mango Pickle"

The system must calculate actual demand from available data sources instead of inventing numbers.

## Demand priority

### Tier A — broad/high-demand commercial topics
Use carefully because competition is high:
- mango pickle
- aam ka achar
- homemade mango pickle
- mango achar
- Indian mango pickle
- Gujarati pickle
- sweet mango pickle
- buy mango pickle online

### Tier B — product/category-specific demand
High opportunity because intent is more specific:
- Gujarati mango pickle
- traditional Gujarati pickle
- sweet mango pickle
- jaggery mango pickle
- Chhundo pickle
- Chhunda pickle
- Gunda Keri pickle
- Gunda pickle
- Lasoda ka achar
- Katka Keri pickle
- Methia mango pickle
- Methi mango pickle
- Gor Keri pickle

### Tier C — long-tail / educational / conversion-supporting
Use for blogs and FAQs:
- what is Chhundo
- Chhundo vs mango pickle
- how to eat Chhundo
- what is Gunda Keri
- Gunda Keri vs regular mango pickle
- what is Lasoda
- what is Gor Keri
- Gujarati jaggery mango pickle
- sweet mango pickle with jaggery
- best pickle with thepla
- pickle with dal rice
- traditional Gujarati achar
- Saurashtra pickle
- homemade style Gujarati achar

---

# 4. HOW CURSOR MUST MEASURE KEYWORD DEMAND

Create a file:

/seo/data/keyword-research.json

Schema:

{
  "keyword": "",
  "country": "IN",
  "language": "en",
  "intent": "commercial|transactional|informational|navigational",
  "search_volume": null,
  "volume_source": "",
  "competition": null,
  "cpc": null,
  "trend": null,
  "serp_features": [],
  "current_ranking_url": "",
  "priority": "A|B|C",
  "target_page": "",
  "notes": ""
}

Preferred data sources in this order:
1. Google Search Console actual queries/impressions/clicks
2. Google Ads Keyword Planner, if credentials/API are available
3. Existing SEO tool/API connected to the project
4. Google autocomplete / related searches / SERP analysis
5. Competitor SERP research

Never write a fake search volume such as "10,000 searches/month" without a source.

If no volume is available:
- use a demand tier
- record "volume unavailable"
- explain the evidence used

---

# 5. COLLECTION ARCHITECTURE

Create only collections that have a meaningful product grouping.

## Collection 1 — All Pickles

Suggested handle:
`all-pickles`

Primary keyword:
- pickles
- Indian pickles
- traditional Indian pickles

Secondary:
- homemade pickles
- Gujarati pickles
- mango pickles
- buy pickles online

Purpose:
Broad discovery page.

SEO title:
`Traditional Indian Pickles Online | The Pickle Affair`

Meta description:
`Explore traditional Indian and Gujarati-style pickles made for everyday meals. Discover mango, sweet, spicy and regional pickle favourites from The Pickle Affair.`

H1:
`Traditional Indian Pickles`

Content sections:
- Introduction
- Explore our pickle range
- Mango pickle varieties
- Sweet & tangy pickles
- Gujarati traditional favourites
- How to choose a pickle
- Serving ideas
- FAQ
- Links to every important collection/product

---

## Collection 2 — Mango Pickles

Suggested handle:
`mango-pickles`

Primary:
- mango pickle
- aam ka achar

Secondary:
- homemade mango pickle
- Indian mango pickle
- Gujarati mango pickle
- raw mango pickle
- mango achar online

SEO title:
`Mango Pickles & Aam Ka Achar Online | The Pickle Affair`

Meta:
`Shop traditional mango pickles and aam ka achar with Gujarati-inspired flavours, from sweet and tangy to spicy and savoury varieties.`

H1:
`Traditional Mango Pickles`

Products:
- Homemade Mango Pickle
- Katka Keri
- Gor Keri
- Chhundo
- Gunda Keri
- other mango-based products actually present in Shopify

Blog cluster:
1. Mango Pickle Guide: Sweet, Spicy and Traditional Varieties
2. Aam Ka Achar: What Makes Traditional Mango Pickle Different?
3. How to Choose a Mango Pickle for Roti, Dal-Rice and Paratha
4. Raw Mango Pickle: Traditional Indian Flavours Explained

---

## Collection 3 — Gujarati Pickles

Suggested handle:
`gujarati-pickles`

Primary:
- Gujarati pickle
- Gujarati pickles

Secondary:
- Gujarati achar
- traditional Gujarati pickle
- homemade Gujarati pickle
- Gujarati mango pickle
- Saurashtra pickle

SEO title:
`Authentic Gujarati Pickles Online | Traditional Achar`

Meta:
`Explore traditional Gujarati-style pickles inspired by regional recipes and classic Indian meal pairings. Discover sweet, tangy and spicy favourites.`

H1:
`Traditional Gujarati Pickles`

Content:
- What Gujarati pickle means
- Sweet vs spicy Gujarati pickle styles
- Mango-based Gujarati favourites
- Saurashtra-inspired flavours
- Serving suggestions
- Product comparison
- FAQs

---

## Collection 4 — Sweet Pickles

Suggested handle:
`sweet-pickles`

Primary:
- sweet pickle
- sweet mango pickle

Secondary:
- sweet mango achar
- Gujarati sweet pickle
- jaggery mango pickle
- sweet and tangy pickle

Products:
- Chhundo
- Gor Keri
- Meethi Keri
- other genuinely sweet products

SEO title:
`Sweet Mango Pickles Online | Gujarati Sweet Achar`

Meta:
`Discover sweet and tangy Gujarati-style pickles including Chhundo, Gor Keri and other traditional mango favourites.`

H1:
`Sweet & Tangy Pickles`

---

## Collection 5 — Spicy & Tangy Pickles

Suggested handle:
`spicy-tangy-pickles`

Primary:
- spicy pickle
- tangy pickle
- spicy mango pickle

Secondary:
- spicy mango achar
- Indian spicy pickle
- Gujarati spicy pickle

Products:
- Katka Keri
- Homemade Mango Pickle
- Gunda Keri
- Chana Keri Methi
- other verified products

SEO title:
`Spicy & Tangy Pickles Online | Indian Achar`

Meta:
`Shop spicy and tangy Indian pickles made to pair with roti, paratha, dal-rice and everyday meals.`

---

## Collection 6 — Gujarati Mango Pickles

Suggested handle:
`gujarati-mango-pickles`

Primary:
- Gujarati mango pickle
- Gujarati mango achar

Secondary:
- traditional Gujarati mango pickle
- homemade Gujarati mango pickle
- keri achar
- raw mango Gujarati pickle

Products:
- Katka Keri
- Gor Keri
- Chhundo
- Homemade Mango Pickle
- Meethi Keri
- Gunda Keri where relevant

This is a high-value commercial category but MUST NOT duplicate the Mango Pickles page.
Difference:
- Mango Pickles = ingredient/product family
- Gujarati Mango Pickles = regional cuisine intent

---

## Collection 7 — Traditional Saurashtra Pickles

Suggested handle:
`saurashtra-pickles`

Primary:
- Saurashtra pickle
- traditional Saurashtra pickle

Secondary:
- Kathiawadi pickle
- traditional Gujarati achar
- Gujarati village style pickle

Only publish if the brand can substantiate its Saurashtra/Kathiawadi connection.

Content:
- Regional food context
- recipe traditions
- ingredients actually used
- product range
- serving culture

Do NOT make unsupported historical claims.

---

## Collection 8 — Homemade Style Pickles

Suggested handle:
`homemade-pickles`

Primary:
- homemade pickle
- homemade pickles online

Secondary:
- homemade mango pickle
- traditional homemade achar
- homemade Gujarati pickle

Only use "homemade" where the actual brand/product positioning supports it.

---

# 6. PRODUCT SEO KEYWORD MAP

Each product gets ONE primary intent and a controlled secondary cluster.

## Product: Chhundo

Primary:
`chhundo`

Secondary:
- chhunda
- chundo
- Gujarati chhundo
- sweet mango pickle
- sweet shredded mango pickle
- aam chhunda
- sweet mango achar

Search intent:
Transactional + informational.

Product page content must answer:
- What is Chhundo?
- What does Chhundo taste like?
- How is it traditionally served?
- What foods pair with it?
- Chhundo vs ordinary mango pickle
- Storage information from actual label
- Ingredients from actual label
- Sizes/prices from Shopify

Blog cluster:
1. What Is Chhundo? A Guide to Gujarati Sweet Mango Pickle
2. Chhundo vs Sweet Mango Pickle: Are They the Same?
3. 7 Foods That Pair Well With Chhundo
4. How Gujarati Families Traditionally Enjoy Chhundo

---

## Product: Gunda Keri

Primary:
`gunda keri pickle`

Secondary:
- gunda pickle
- gunda nu athanu
- lasoda ka achar
- lasode ka achar
- gunda mango pickle
- Gujarati gunda pickle
- Indian cherry pickle

Blog cluster:
1. What Is Gunda Keri Pickle?
2. Gunda Keri vs Regular Mango Pickle
3. What Is Gunda / Lasoda? Ingredient Guide
4. How to Serve Gunda Keri with Indian Meals
5. Gunda Keri Pickle: Gujarati Traditional Style Explained

---

## Product: Gor Keri

Primary:
`gor keri`

Secondary:
- gorkeri
- gor keri pickle
- jaggery mango pickle
- sweet jaggery mango pickle
- Gujarati jaggery mango pickle
- sweet mango achar

Blog cluster:
1. What Is Gor Keri?
2. Gor Keri: How Jaggery Changes Mango Pickle
3. Sweet Mango Pickle vs Jaggery Mango Pickle
4. Gujarati Meal Pairings for Gor Keri

---

## Product: Katka Keri

Primary:
`katka keri pickle`

Secondary:
- katka keri
- Gujarati mango pickle
- raw mango pickle
- homemade Gujarati mango pickle
- keri achar

Blog cluster:
1. What Is Katka Keri Pickle?
2. Katka Keri vs Other Gujarati Mango Pickles
3. How to Serve Katka Keri
4. Raw Mango Pickle Guide: Understanding Keri Achar

---

## Product: Homemade Mango Pickle

Primary:
`homemade mango pickle`

Secondary:
- aam ka achar
- mango achar
- homemade aam ka achar
- Indian mango pickle
- traditional mango pickle
- Gujarati mango pickle

Blog cluster:
1. Homemade Mango Pickle Guide
2. Aam Ka Achar: A Traditional Indian Pickle Explained
3. What to Look for When Buying Mango Pickle Online
4. Mango Pickle Pairings for Everyday Indian Meals

---

## Product: Meethi Keri

Primary:
`meethi keri pickle`

Secondary:
- sweet mango pickle
- meethi keri achar
- sweet keri achar
- Gujarati sweet mango pickle
- sweet mango achar

Blog cluster:
1. What Is Meethi Keri?
2. Meethi Keri vs Gor Keri
3. Sweet Mango Pickle Pairing Guide
4. Gujarati Sweet Pickle Varieties

---

## Product: Chana Keri Methi

Primary:
`chana keri methi pickle`

Secondary:
- chana keri pickle
- methi mango pickle
- methia mango pickle
- Gujarati methi pickle
- mango methi achar

Blog cluster:
1. What Is Chana Keri Methi Pickle?
2. Methi Mango Pickle: What Makes the Flavour Different?
3. Chana Keri Methi Serving Guide
4. Gujarati Pickle Masala and Methi: A Flavour Guide

---

# 7. BLOG SYSTEM

Do NOT create five near-identical blogs every day.

Instead use a controlled editorial queue.

Recommended launch:
- 2–3 high-quality supporting articles per week
- Increase only if quality remains high
- Every article must have a unique search intent
- Every article must support a collection/product
- Every article must contain original brand/product information where relevant

If the user specifically enables daily automation, the system may create daily drafts, but MUST publish only when all quality gates pass.

## Blog minimum requirements

Each article:
- 1,200–2,000 words for substantial informational topics
- Shorter only when the query genuinely requires a short answer
- Unique title
- Unique H1
- Strong introduction
- Answer-first section
- 5–8 useful sections
- FAQ section where useful
- 3–8 contextual internal links
- 1–3 product links
- 1 relevant collection link
- Original serving/pairing information
- Product facts verified against Shopify
- No invented facts
- No keyword stuffing
- No copied competitor wording
- No generic AI filler
- Clear CTA
- Image with descriptive ALT text
- Meta title
- Meta description
- SEO-friendly handle
- Article schema where appropriate
- BreadcrumbList where supported
- Author/publisher information where available

---

# 8. CONTENT TEMPLATE FOR EVERY BLOG

Use this structure:

# H1

Short direct answer / introduction.

## Quick Answer
2–4 paragraphs answering the search intent immediately.

## What Is [Topic]?
Clear explanation.

## What Makes It Different?
Actual product/cuisine differences.

## Ingredients / Flavour / Texture
Only verified facts.

## How to Enjoy It
Real meal pairings:
- roti
- paratha
- thepla
- dal-rice
- khichdi
- puri
etc. only where appropriate.

## [Product/Collection] Recommendation
Explain when this product fits the reader's need.

## Related Pickle Varieties
Internal links to relevant collections/products.

## Frequently Asked Questions
4–7 useful questions.

## Final Takeaway
Short useful summary + CTA.

---

# 9. INTERNAL LINKING SYSTEM

Every product page should link to:
- its main collection
- one related collection
- 2–4 relevant blogs
- 2–3 related products

Every collection should link to:
- all products in that collection
- 4–8 relevant blogs
- closely related collections

Every blog should link to:
- 1 primary product
- 1 primary collection
- 2–4 related products/collections
- 2 related blogs

Create contextual anchors.

GOOD:
"traditional Gujarati mango pickle"
"our Gunda Keri pickle"
"learn more about Chhundo"

BAD:
"click here"
"best pickle best pickle best pickle"

Google recommends crawlable links and a logical ecommerce hierarchy.

---

# 10. SILO / SITE ARCHITECTURE

Recommended:

Home
|
+-- All Pickles
|
+-- Mango Pickles
|   +-- Homemade Mango Pickle
|   +-- Katka Keri
|   +-- Gor Keri
|   +-- Chhundo
|   +-- Gunda Keri
|
+-- Gujarati Pickles
|
+-- Sweet Pickles
|   +-- Chhundo
|   +-- Gor Keri
|   +-- Meethi Keri
|
+-- Spicy & Tangy Pickles
|
+-- Gujarati Mango Pickles
|
+-- Traditional Saurashtra Pickles
|
+-- Blog / Kitchen Tales
    +-- Chhundo cluster
    +-- Gunda Keri cluster
    +-- Mango Pickle cluster
    +-- Gujarati Pickle cluster
    +-- Serving / recipe cluster

Do not create unnecessary nested categories.

---

# 11. COMPETITOR KEYWORD STRATEGY — IMPORTANT

Competitor research is allowed for market discovery.

Do NOT:
- copy competitor pages
- scrape competitor descriptions
- create fake "official" pages
- use competitor brand names repeatedly just to capture their traffic
- create misleading titles such as "FarmDidi Pickle Official"
- create pages with no genuine comparison purpose

Instead use competitor terms ONLY when the page genuinely serves comparison intent.

Examples of legitimate content:
- "Traditional Gunda Keri Pickle: What to Compare Before Buying"
- "Gunda Keri Pickle Buying Guide: Ingredients, Taste & Serving"
- "Traditional Gujarati Pickles: What Makes Different Brands Unique?"

If mentioning a competitor:
- use the exact factual brand name only where relevant
- provide factual comparison
- do not make unsupported negative claims
- do not claim superiority without evidence
- do not create hundreds of competitor-brand pages

Create a competitor research file:

/seo/data/competitors.json

Fields:
- competitor
- URL
- products
- ranking_keywords
- content_topics
- strengths
- gaps
- price_positioning
- unique_terms
- opportunity_keywords
- last_checked

Known research targets can include:
- FarmDidi
- JhaJi Store
- Goosebumps
- other actual SERP competitors discovered for each query

Competitor research should produce CONTENT OPPORTUNITIES, not copied content.

---

# 12. COMPETITOR GAP PROCESS

For each important keyword:

1. Search Google.
2. Collect top 10 organic URLs.
3. Classify:
   - ecommerce product
   - collection/category
   - recipe
   - informational article
   - marketplace
   - video
4. Extract:
   - title pattern
   - H1
   - subtopics
   - FAQs
   - product attributes
   - serving ideas
   - internal links
5. Identify what users still need.
6. Create a better, original page around that missing value.

Never rewrite the competitor article.

---

# 13. PRODUCT PAGE SEO CHECKLIST

Every product page must have:

- SEO title
- meta description
- one H1
- concise product summary
- detailed product description
- ingredients
- flavour profile
- texture
- serving suggestions
- storage information
- shelf life only if verified
- pack sizes
- price
- availability
- shipping information where relevant
- customer reviews
- FAQs
- related products
- related collection
- optimized images
- descriptive ALT text
- Product structured data
- Offer data
- AggregateRating only from genuine reviews
- BreadcrumbList
- canonical URL

Do not fabricate reviews, ratings or structured-data values.

Google specifically recommends Product structured data for ecommerce product pages and Merchant Center product data.

---

# 14. COLLECTION PAGE SEO CHECKLIST

Each collection must contain:

1. SEO title
2. Meta description
3. H1
4. 150–300 word unique introduction
5. Product grid
6. Category explanation
7. Buying guidance
8. Product comparison section
9. Serving ideas
10. FAQ
11. Related collection links
12. Relevant blog links
13. Breadcrumbs
14. Collection-level canonical
15. Clean URL
16. Unique image/collection banner if available
17. Descriptive image ALT text

Do not create a collection only to rank for a keyword variation.

---

# 15. FAQ KEYWORD EXPANSION

For every collection/product, generate FAQ candidates from:
- Google autocomplete
- People Also Ask
- Search Console
- customer questions
- product reviews
- competitor FAQs
- actual customer support questions

Examples:

Chhundo:
- What is Chhundo?
- Is Chhundo sweet or spicy?
- What is Chhundo made from?
- What do you eat Chhundo with?
- Is Chhundo the same as sweet mango pickle?

Gunda Keri:
- What is Gunda Keri?
- What is Gunda called in Hindi?
- Is Gunda the same as Lasoda?
- What does Gunda Keri taste like?
- What foods go with Gunda Keri?

Mango Pickle:
- What is Aam Ka Achar?
- What is mango pickle made from?
- What is the difference between sweet and spicy mango pickle?
- What should you eat with mango pickle?
- How should mango pickle be stored?

---

# 16. IMAGE SEO

For every collection/product/blog:

Filename:
`gujarati-mango-pickle-the-pickle-affair.webp`

ALT:
`Traditional Gujarati mango pickle from The Pickle Affair`

Rules:
- Describe the actual image.
- Do not stuff keywords.
- Do not use competitor brand names in image ALT.
- Compress images.
- Use WebP/AVIF where supported.
- Preserve actual packaging and logo.

---

# 17. SHOPIFY IMPLEMENTATION

Cursor must inspect the existing Shopify theme before changing anything.

Do NOT blindly replace:
- theme files
- product templates
- collection templates
- navigation
- metafields
- app integrations

Create reusable Shopify sections/snippets where appropriate.

Recommended metafields:

### Product metafields
- custom.primary_keyword
- custom.secondary_keywords
- custom.short_intro
- custom.flavour_profile
- custom.texture
- custom.serving_suggestions
- custom.storage
- custom.faq
- custom.related_blog_handles
- custom.related_collection_handles
- custom.seo_notes

### Collection metafields
- custom.primary_keyword
- custom.secondary_keywords
- custom.introduction
- custom.buying_guide
- custom.serving_ideas
- custom.faq
- custom.related_blog_handles

Do not expose technical keyword lists visibly to customers.

---

# 18. AUTOMATED CONTENT QUEUE

Create:

`/seo/content-queue.json`

Example:

{
  "queue": [
    {
      "type": "collection",
      "target": "mango-pickles",
      "primary_keyword": "mango pickle",
      "status": "pending"
    },
    {
      "type": "product",
      "target": "chhundo",
      "primary_keyword": "chhundo",
      "status": "pending"
    },
    {
      "type": "blog",
      "target": "what-is-chhundo",
      "primary_keyword": "what is chhundo",
      "status": "pending"
    }
  ]
}

Allowed statuses:
- pending
- research
- draft
- quality-check
- approved
- published
- needs-review
- failed

---

# 19. AUTO-PUBLISH WORKFLOW

Cursor automation:

STEP 1
Read current Shopify catalog.

STEP 2
Read existing collections.

STEP 3
Read all published blog articles.

STEP 4
Build keyword inventory.

STEP 5
Check duplicate search intent.

STEP 6
Research SERP competitors.

STEP 7
Assign keywords to exactly one primary page.

STEP 8
Generate content brief.

STEP 9
Generate content.

STEP 10
Run quality checks.

STEP 11
Update Shopify.

STEP 12
Create internal links.

STEP 13
Generate/update sitemap automatically through Shopify's native mechanism.

STEP 14
Record publication in `/seo/logs/published-content.json`.

STEP 15
Run post-publish validation.

---

# 20. QUALITY GATE — MUST PASS ALL

Before publication:

[ ] Keyword has a defined search intent
[ ] No existing page already targets the same intent
[ ] Page has unique value
[ ] Product facts verified
[ ] No invented claims
[ ] No competitor copying
[ ] No keyword stuffing
[ ] No doorway-page pattern
[ ] Title is unique
[ ] Meta description is unique
[ ] H1 is unique
[ ] Content is readable
[ ] Internal links work
[ ] Product links work
[ ] Collection links work
[ ] Canonical is correct
[ ] Images exist
[ ] ALT text is descriptive
[ ] Structured data is valid where applicable
[ ] No broken HTML
[ ] No accidental noindex
[ ] Mobile layout is acceptable
[ ] Page loads efficiently
[ ] CTA is relevant
[ ] Article actually answers the query

If any critical item fails:
- DO NOT publish
- set status to `needs-review`

---

# 21. DUPLICATE / CANNIBALIZATION DETECTOR

Before creating a new page calculate:

`intent_similarity`

Compare:
- primary keyword
- title
- H1
- URL
- first 300 words
- section headings
- product targets

If similarity > 0.75 with an existing page:
- do not publish automatically
- merge, redirect or change intent

One primary keyword intent should have one canonical destination.

---

# 22. CONTENT CALENDAR

Initial 30-day sequence:

### Week 1
1. Collection: Mango Pickles
2. Product: Chhundo
3. Blog: What Is Chhundo?

### Week 2
4. Collection: Gujarati Pickles
5. Product: Gunda Keri
6. Blog: What Is Gunda Keri Pickle?

### Week 3
7. Collection: Sweet Pickles
8. Product: Gor Keri
9. Blog: What Is Gor Keri?

### Week 4
10. Collection: Spicy & Tangy Pickles
11. Product: Katka Keri
12. Blog: Traditional Gujarati Mango Pickle Guide

Then:
13. Meethi Keri product SEO
14. Chana Keri Methi product SEO
15. Homemade Mango Pickle product SEO
16. Gujarati Mango Pickles collection
17. Saurashtra Pickles collection
18. Homemade Pickles collection

Then continue with informational/supporting clusters.

---

# 23. BLOG-TO-PRODUCT MATRIX

### Chhundo
Blogs -> Chhundo product -> Sweet Pickles -> Mango Pickles -> Gujarati Pickles

### Gunda Keri
Blogs -> Gunda Keri -> Mango Pickles -> Gujarati Pickles -> Spicy & Tangy

### Gor Keri
Blogs -> Gor Keri -> Sweet Pickles -> Mango Pickles -> Gujarati Mango Pickles

### Katka Keri
Blogs -> Katka Keri -> Spicy & Tangy -> Gujarati Mango Pickles -> Mango Pickles

### Meethi Keri
Blogs -> Meethi Keri -> Sweet Pickles -> Mango Pickles

### Chana Keri Methi
Blogs -> Chana Keri Methi -> Spicy & Tangy -> Gujarati Pickles

### Homemade Mango Pickle
Blogs -> Homemade Mango Pickle -> Mango Pickles -> Homemade Pickles -> Gujarati Mango Pickles

---

# 24. CONTENT TYPES TO BUILD

Do not rely only on "What is X?" posts.

Build these formats:

### Educational
- What is X?
- History/tradition of X where verifiable
- Ingredient guide
- flavour guide

### Commercial investigation
- How to choose X
- X buying guide
- X vs Y
- sweet vs spicy pickle guide

### Serving
- What to eat with X
- X with thepla
- X with dal rice
- X with paratha
- Indian meal pairing guides

### Recipe/support
Only create recipes where the recipe is genuinely useful and tested/verified.

### Comparison
- Chhundo vs sweet mango pickle
- Gor Keri vs Chhundo
- Gunda Keri vs regular mango pickle
- sweet vs spicy mango pickle

### Seasonal
- raw mango pickle season
- mango pickle preservation
- summer pickle traditions

---

# 25. INTERNAL LINK ANCHOR VARIATION

Use natural anchors.

Examples:
- traditional mango pickle
- Gujarati mango achar
- sweet mango pickle
- our Chhundo
- Gunda Keri pickle
- jaggery mango pickle
- homemade mango pickle

Do NOT repeatedly use:
"best mango pickle buy mango pickle online homemade mango pickle India"

---

# 26. SEARCH CONSOLE LOOP

Create a weekly SEO job.

For every indexed URL:
- impressions
- clicks
- CTR
- average position
- top queries
- query/page mismatch
- pages with high impressions but low CTR
- pages ranking positions 5–20
- pages losing impressions
- pages gaining impressions

Actions:

High impressions + low CTR:
- test title/meta

Position 5–20:
- improve content depth
- add internal links
- improve matching search intent

High impressions + wrong query:
- improve topical clarity

No impressions after reasonable indexing period:
- inspect indexing, internal links and intent

Never automatically change a successful page every day.

---

# 27. PRODUCT + BLOG SYNCHRONIZATION

Whenever a product is added:

AUTOMATICALLY:
1. Detect product.
2. Generate keyword research.
3. Assign primary keyword.
4. Update product SEO.
5. Add to relevant collection.
6. Create 3–5 blog ideas.
7. Add content queue.
8. Add internal linking opportunities.
9. Generate FAQ candidates.
10. Log all actions.

Whenever a collection is added:

AUTOMATICALLY:
1. Detect product group.
2. Generate collection keyword map.
3. Check cannibalization.
4. Create collection content.
5. Create 5–10 supporting blog ideas.
6. Link products.
7. Link related collections.
8. Add to navigation only if strategically useful.

---

# 28. CHANGE MANAGEMENT

Before modifying Shopify:

Create backup/export where possible.

Log:
- date/time
- file/theme changed
- collection
- product
- old title
- new title
- old description
- new description
- old URL
- new URL
- redirect created?
- reason
- keyword target

Never change a URL without checking whether a 301 redirect is needed.

---

# 29. TECHNICAL SEO CHECKS

Automate checks for:

- HTTP status
- canonical
- robots meta
- sitemap inclusion
- indexability
- title length
- meta description length
- H1 count
- broken links
- image ALT
- image dimensions
- image file size
- structured data
- breadcrumb
- mobile rendering
- page speed signals
- duplicate titles
- duplicate meta descriptions
- duplicate H1
- orphan pages

---

# 30. SCHEMA RULES

Product pages:
- Product
- Offer
- AggregateRating only from genuine review data
- BreadcrumbList

Blog pages:
- Article/BlogPosting where appropriate
- BreadcrumbList
- Author/Publisher information when available

Do not create fake:
- ratings
- reviews
- prices
- availability
- author identities
- dates

---

# 31. "COMPETITOR TRAFFIC" STRATEGY — SAFE VERSION

The objective is to capture users who are researching the category, not to impersonate competitors.

Build:
- "Gunda Keri Pickle Buying Guide"
- "Gujarati Mango Pickle Guide"
- "Traditional Indian Pickle Comparison Guide"
- "How to Choose a Traditional Pickle Online"
- "Sweet Mango Pickle Guide"

If there is legitimate demand for a specific brand comparison:
- create one high-quality comparison page
- mention only factual, verifiable differences
- disclose that The Pickle Affair is the seller/brand being compared
- do not use deceptive titles
- do not create a page for every competitor

Do not create:
- competitor-name doorway pages
- "competitor alternative" pages at scale
- fake review pages
- pages designed only to intercept branded searches

---

# 32. AI CONTENT RULES

AI may assist research and drafting.

AI MUST NOT:
- invent facts
- invent customer experiences
- invent heritage stories
- invent ingredients
- invent health claims
- copy competitor wording
- rewrite competitor pages sentence-by-sentence
- generate thousands of thin pages

Every AI article must contain real information specific to The Pickle Affair.

---

# 33. CURSOR AGENT TASK

Create a reusable Cursor task/agent named:

`SEO_AUTOPILOT`

Instruction:

"You are the SEO and ecommerce content automation agent for The Pickle Affair.

Before taking action:
1. inspect the current Shopify theme and catalog;
2. inspect all current collections, products and blog articles;
3. inspect SEO metadata;
4. inspect existing URLs and internal links;
5. inspect keyword inventory;
6. inspect content queue;
7. identify search-intent gaps;
8. research current SERPs;
9. create only pages with distinct user value;
10. verify every product fact against Shopify;
11. never fabricate search volume;
12. never copy competitor content;
13. never create keyword-stuffed or doorway pages;
14. run the complete quality gate;
15. publish only when all critical checks pass;
16. log every change.

When the queue contains a task:
- research
- draft
- validate
- publish
- link
- log
- verify

If the task conflicts with an existing page:
- stop
- mark needs-review
- explain the conflict in the log.

If data is missing:
- do not guess
- mark needs-review.

If a competitor is involved:
- use competitor data only for research and legitimate comparison intent.
- never impersonate, copy or misrepresent another brand."

---

# 34. FILE STRUCTURE TO CREATE

/seo/
  /data/
    keyword-research.json
    competitors.json
    content-inventory.json
    internal-links.json

  /content/
    /collections/
    /products/
    /blogs/

  /logs/
    published-content.json
    changes.json
    seo-errors.json

  content-queue.json
  SEO_AUTOPILOT.md
  SEO_RULES.md
  KEYWORD_MAP.md

---

# 35. REQUIRED REPORT AFTER EACH RUN

Cursor must output:

## SEO RUN REPORT

Date:
Run ID:

### Research
- Keywords researched:
- New opportunities:
- Cannibalization detected:
- Competitor gaps:

### Published
- Collections:
- Products:
- Blogs:

### Internal Linking
- Links added:
- Links changed:

### Technical
- Errors:
- Structured-data errors:
- Broken links:

### SEO
- Primary keywords assigned:
- Search intent:
- Demand evidence:

### Next Queue
1.
2.
3.
4.
5.

---

# 36. FIRST IMPLEMENTATION PRIORITY

Do NOT immediately generate hundreds of articles.

First build:

PHASE 1
- keyword database
- content inventory
- competitor database
- cannibalization detector
- collection architecture
- product keyword map
- internal-link engine

PHASE 2
- optimize 7 core products
- create 4–6 important collections
- create first 12 supporting blogs

PHASE 3
- Search Console feedback loop
- keyword expansion
- content refresh
- competitor gap analysis

PHASE 4
- continuous publishing based on actual demand

---

# 37. SUCCESS METRICS

Track monthly:

### Google Search
- impressions
- clicks
- CTR
- average position
- indexed pages
- non-brand clicks
- product-query clicks
- collection-query clicks
- blog-query clicks

### Ecommerce
- collection visits
- product visits
- add-to-cart rate
- conversion rate
- revenue by landing page
- revenue by keyword where available

### Content
- pages published
- pages indexed
- pages with impressions
- pages generating clicks
- pages generating sales

Do not use "number of blogs published" as the main SEO success metric.

---

# 38. FINAL RULE

The system should optimize for:

USER INTENT
+
ORIGINAL INFORMATION
+
PRODUCT RELEVANCE
+
STRONG INTERNAL LINKING
+
TECHNICAL SEO
+
REAL SEARCH DATA
+
CONTINUOUS IMPROVEMENT

Not:

MORE PAGES
+
MORE KEYWORDS
+
MORE AI TEXT

The goal is to make The Pickle Affair the useful destination for people researching and buying traditional Gujarati, mango, sweet, spicy and regional Indian pickles.
