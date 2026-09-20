#!/usr/bin/env python3
"""
Rewrite all live Kitchen Tales articles to BLOG.md rules.

- UPDATE EXISTING in place (same Shopify ID / handle)
- Answer-first, unique H2s, FAQs, products, related guides
- No invented recipe quantities / no fabricated claims
- Clean titles (drop dated “20 Sep” / trailing brand pipes)
- Unpublish thin near-duplicates listed in BLOG_AUDIT

Run via GitHub Actions (secrets) or locally with SHOPIFY_CLIENT_ID/SECRET.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scratch"))
from shopify_auth import resolve_access_token, shop_url  # noqa: E402

PRODUCTS = {p["handle"]: p for p in json.loads((ROOT / "scratch" / "product_registry.json").read_text())}
BLOG_ID = os.environ.get("SHOPIFY_BLOG_ID", "96853164183")
API = "2024-10"
SHOP_URL = shop_url()
CTX = ssl.create_default_context()
TOKEN = ""
DRY_RUN = os.environ.get("DRY_RUN", "").strip() in ("1", "true", "yes")

# Thin near-duplicates to unpublish (handles). Canonical KEEP pages are updated instead.
UNPUBLISH_HANDLES = {
    "sweet-mango-pickle-homemade-guide-the-pickle-affair-20-sep",
    "katka-keri-pickle-guide-the-pickle-affair-20-sep",
    "buy-gunda-keri-online-guide-the-pickle-affair",  # prefer dated KEEP if that is live; see map
    "gujarati-keri-achar-guide-the-pickle-affair",
    "chana-keri-methi-pickle-guide-the-pickle-affair",
}


def api(method: str, path: str, payload: dict | None = None) -> dict:
    global TOKEN
    if not TOKEN:
        TOKEN = resolve_access_token()
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{SHOP_URL}/admin/api/{API}{path}",
        data=data,
        method=method,
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=90) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise SystemExit(f"API {method} {path} failed: {e.code} {err}") from e


def list_articles() -> list[dict]:
    out: list[dict] = []
    page_info = None
    # Simple limit=250 is enough for current blog
    data = api("GET", f"/blogs/{BLOG_ID}/articles.json?limit=250")
    out.extend(data.get("articles", []))
    return out


def product_card(handle: str) -> str:
    p = PRODUCTS.get(handle)
    if not p:
        return ""
    return f"""
<div class="dp-product-card" style="background:#F5F7F0;border:1px solid #DDE5C8;border-radius:16px;padding:24px;margin:28px 0;text-align:center;">
  <img src="{p['image']}" alt="{p['title']} from The Pickle Affair" style="max-width:220px;width:100%;height:auto;border-radius:12px;margin-bottom:14px;">
  <h3 style="color:#4A6B29;margin:8px 0 10px;font-size:18px;">{p['title']}</h3>
  <p style="color:#1D2614;font-size:14px;margin-bottom:14px;">Handmade Kathiawadi pickle from The Pickle Affair — ships across India.</p>
  <a href="/products/{p['handle']}" style="background:#4A6B29;color:#fff;padding:11px 24px;border-radius:999px;font-weight:700;text-decoration:none;display:inline-block;">View {p['title']} →</a>
</div>
""".strip()


def faq_block(faqs: list[tuple[str, str]]) -> tuple[str, str]:
    faq_json = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }
    html = "".join(
        f'<div class="dp-faq-item"><h3 class="dp-faq-question">{q}</h3><p>{a}</p></div>' for q, a in faqs
    )
    script = f'<script type="application/ld+json">{json.dumps(faq_json, ensure_ascii=False)}</script>'
    return script, html


def related_html(links: list[tuple[str, str]]) -> str:
    items = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in links)
    return f"<h2>Related Kitchen Tales guides</h2><ul>{items}</ul>"


def wrap_article(
    *,
    lead: str,
    middle: str,
    products: list[str],
    related: list[tuple[str, str]],
    faqs: list[tuple[str, str]],
    cluster: str,
    intent: str,
) -> str:
    script, faq_html = faq_block(faqs)
    cards = "\n".join(product_card(h) for h in products if h)
    return f"""
{script}

<p class="dp-lead">{lead}</p>

{middle}

{cards}

{related_html(related)}

<h2>Frequently asked questions</h2>
{faq_html}

<p><em>Written from The Pickle Affair’s Kathiawadi kitchen · Cluster: {cluster} · Intent: {intent}</em></p>
<p><em>Policy: BLOG.md — quality over volume. No invented recipe quantities.</em></p>
""".strip()


# Shared related anchors (relative)
R_STORE = ("/blogs/kitchen-tales/how-to-store-indian-pickles-keep-gujarati-achar-fresh-for-months", "How to store Indian pickles")
R_SHELF = ("/blogs/kitchen-tales/how-long-does-mango-pickle-last-shelf-life-freshness-signs", "Mango pickle shelf life")
R_BAA = ("/blogs/kitchen-tales/how-baa-s-kitchen-makes-traditional-gujarati-pickles", "How Baa’s Kitchen makes pickles")
R_BUY = ("/blogs/kitchen-tales/how-to-buy-authentic-gujarati-pickle-online-without-guesswork", "Buy Gujarati pickle online")
R_CHHUNDO = ("/blogs/kitchen-tales/chhundo-traditional-gujarati-sweet-shredded-mango-achar", "Chhundo guide")
R_MEETHI = ("/blogs/kitchen-tales/sweet-mango-pickle-homemade-guide-the-pickle-affair", "Sweet mango pickle / Meethi Keri")
R_MUSTARD = ("/blogs/kitchen-tales/why-mustard-oil-is-used-in-gujarati-and-kathiawadi-pickles", "Mustard oil in pickles")
R_METHI = ("/blogs/kitchen-tales/fenugreek-methi-in-mango-pickle-flavour-bitterness-chana-keri", "Fenugreek in mango pickle")
R_KHICHDI = ("/blogs/kitchen-tales/pickle-with-khichdi-comfort-pairings-from-a-kathiawadi-kitchen", "Pickle with khichdi")
R_KATKA = ("/blogs/kitchen-tales/katka-keri-pickle-how-to-store-and-serve-at-home-the-pickle-affair", "Katka Keri storage & serve")
R_GUNDA = ("/blogs/kitchen-tales/buy-gunda-keri-online-guide-the-pickle-affair-20-sep", "Buy Gunda Keri")
R_KERI = ("/blogs/kitchen-tales/gujarati-keri-achar-guide-the-pickle-affair-20-sep", "Gujarati Keri Achar")
R_CHANA = ("/blogs/kitchen-tales/chana-keri-methi-pickle-guide-the-pickle-affair-20-sep", "Chana Keri Methi")


def profiles() -> dict[str, dict]:
    """handle substring / exact handle → rewrite profile."""
    return {
        "sweet-mango-pickle-homemade-guide-the-pickle-affair": {
            "exact": True,
            "title": "Sweet Mango Pickle Recipe: Traditional Gujarati Meethi Keri Achar",
            "tags": "Heritage Recipes, sweet mango pickle, meethi keri",
            "image": "sweet-mango-pickle-meethi-keri-achar-homemade",
            "excerpt": (
                "What is sweet mango pickle? Meethi Keri is a traditional Gujarati sweet mango achar — "
                "taste, serve, store, and choose a jar with confidence from The Pickle Affair."
            )[:155],
            "cluster": "Heritage Recipes",
            "intent": "Informational + commercial",
            "products": ["sweet-mango-pickle-meethi-keri-achar-homemade", "chhundo-pickle-sweet-shredded-mango-achar-gujarati"],
            "related": [R_CHHUNDO, R_STORE, R_SHELF, R_BAA, R_KERI],
            "faqs": [
                ("What is sweet mango pickle?", "Sweet mango pickle (Meethi Keri) is a Gujarati-style achar that balances ripe or prepared mango with a sweet-leaning spice profile — served as a small spoon beside everyday meals."),
                ("What is Meethi Keri?", "Meethi Keri is The Pickle Affair’s sweet mango achar style: keri pieces in a homemade sweet-tang tradition, made for roti, thepla, and dal-rice plates."),
                ("What is the difference between Chhundo and Meethi Keri?", "Chhundo is typically shredded mango relish; Meethi Keri centres on sweet keri pieces. Texture and how you spoon them on the plate differ."),
                ("Can you share exact recipe quantities?", "Our house recipe stays with the kitchen. This guide covers traditional method and flavour without inventing proprietary quantities."),
                ("How should I store Meethi Keri?", "Cool, dry place; clean dry spoon; jar sealed. Follow the label’s best-before guidance."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p><strong>Sweet mango pickle</strong> — often called <strong>Meethi Keri</strong> in Gujarati homes — is a sweet-leaning mango achar meant for everyday meals. This guide explains what it is, how it differs from Chhundo, how families serve and store it, and how The Pickle Affair’s jar fits that tradition — without inventing proprietary recipe numbers.</p>

<h2>What is sweet mango pickle?</h2>
<p>In many Indian kitchens, “sweet mango pickle” means mango preserved with spices where sweetness leads (from sugar, jaggery, or a house sweet-spice mix), not only chilli heat. In Gujarati and Kathiawadi cooking, that idea is closely tied to <em>Meethi Keri</em> — sweet keri achar for thepla, rotla, khichdi, and dal-bhaat.</p>

<h2>What is Meethi Keri?</h2>
<p>Meethi Keri is the sweet mango pickle style we bottle as <strong>Meethi Keri | Sweet Mango Achar</strong>. It is built for a spoon-on-the-side habit: enough sweetness to contrast savoury breads, with spice that still tastes like achar — not jam.</p>

<h2>Traditional Gujarati / Kathiawadi background</h2>
<p>Kathiawadi pickle-making values patience, oil and spice balance, and jars meant to last through the season. Sweet styles sit beside spicier keri achar so one thali can move from sharp to sweet in the same meal.</p>

<h2>Baa’s Kitchen note</h2>
<p>At The Pickle Affair we describe only practices we follow: traditional spice logic, hygienic FSSAI-certified preparation, no synthetic colours, and glass jars suited to home storage. We do not invent years of awards or medical claims.</p>

<h2>Ingredients (what to expect)</h2>
<p>Look for recognisable pickle ingredients: mango/keri, spices, oil, and a sweetening approach appropriate to Meethi Keri. Always read the product label for the authoritative ingredient list for the jar you buy.</p>

<h2>How traditional sweet mango pickle is prepared (method overview)</h2>
<p>Traditional method (high level, not a proprietary formula):</p>
<ol>
  <li>Select and prepare mango suitable for the sweet style.</li>
  <li>Balance spices so sweetness leads without losing pickle character.</li>
  <li>Cure/rest so flavours settle in the jar.</li>
  <li>Pack in clean glass with clear storage guidance.</li>
</ol>
<p><em>Exact quantities and proprietary steps stay in the kitchen. We do not publish invented numbers.</em></p>

<h2>Taste profile</h2>
<p>Expect sweet-first mango with spice warmth and achar depth — a relish for savoury breads rather than a dessert.</p>

<h2>Sweet vs spicy mango pickle</h2>
<ul>
  <li><strong>Sweet (Meethi Keri)</strong> — pairs well when the plate wants contrast against salty/spicy mains.</li>
  <li><strong>Spicy keri achar</strong> — leads with heat and tang for everyday roti meals.</li>
</ul>

<h2>Meethi Keri vs Chhundo</h2>
<p>Both are sweet mango traditions. Chhundo is usually shredded; Meethi Keri keeps keri-piece character. Choose by texture preference and how you like to spoon pickle beside thepla or dal-rice.</p>

<h2>Storage &amp; shelf life</h2>
<p>Store sealed, cool, and dry; use a clean dry spoon. Unopened shelf life follows the jar label. After opening, hygiene matters more than any generic “months” claim — if aroma or appearance changes unexpectedly, do not use it.</p>

<h2>Serving ideas</h2>
<ul>
  <li>Thepla or rotla in a tiffin with a small spoon of Meethi Keri</li>
  <li>Dal-bhaat when you want sweet contrast</li>
  <li>Gift sets paired with a spicier keri achar</li>
</ul>

<h2>Where to buy</h2>
<p>Buy Meethi Keri from The Pickle Affair online when you want a handmade sweet mango jar with clear product details and India-wide shipping.</p>
""",
        },
        "katka-keri-pickle-how-to-store-and-serve-at-home-the-pickle-affair": {
            "exact": True,
            "title": "Katka Keri Pickle: How to Store and Serve at Home",
            "tags": "Buying Guides, katka keri, pickle storage",
            "image": "katka-keri-pickle-homemade-gujarati-mango-achar",
            "excerpt": (
                "How to store and serve Katka Keri pickle at home — dry-spoon habits, pairing ideas, "
                "and what makes this Gujarati mango achar style distinct."
            )[:155],
            "cluster": "How-to",
            "intent": "How-to + commercial",
            "products": ["katka-keri-pickle-homemade-gujarati-mango-achar"],
            "related": [R_STORE, R_SHELF, R_KHICHDI, R_MUSTARD, R_KERI],
            "faqs": [
                ("What is Katka Keri pickle?", "Katka Keri is a homemade Gujarati mango achar style from The Pickle Affair — made for everyday meals and careful home storage."),
                ("How do I store Katka Keri?", "Cool dry place, sealed jar, clean dry spoon every time. Keep away from stove heat and direct sun."),
                ("What should I eat with Katka Keri?", "Roti, thepla, khichdi, and dal-rice are natural companions — a spoon on the side is enough."),
                ("Does opening shorten shelf life?", "Hygiene after opening matters. Follow the label and stop using the jar if smell or look changes unexpectedly."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p><strong>Katka Keri</strong> keeps best when you treat it like traditional oil-cured achar: sealed jar, cool dry cupboard, and a <em>clean dry spoon</em> every time. Serve a small spoon beside roti, thepla, or khichdi — pickle is a companion, not the whole plate.</p>

<h2>What Katka Keri is</h2>
<p>Katka Keri pickle is The Pickle Affair’s homemade Gujarati mango achar style — built for everyday Kathiawadi-style meals. This page focuses on <strong>storage and serving</strong> (how-to intent), not a second generic product brochure.</p>

<h2>Step-by-step storage habits</h2>
<ol>
  <li>Close the jar tightly after every use.</li>
  <li>Use only a clean, completely dry spoon.</li>
  <li>Store away from the stove and direct sunlight.</li>
  <li>In humid kitchens, prefer a cupboard away from the sink.</li>
  <li>Where the style uses oil curing, keep pieces under the oil layer as packed.</li>
</ol>

<h2>After opening</h2>
<p>Continue the dry-spoon rule. Check the printed best-before on the label. Unusual smell, mould, or unexpected fizzing means do not taste — discard.</p>

<h2>How to serve Katka Keri</h2>
<ul>
  <li>Weekday roti or rotla with a sharp spoon of pickle</li>
  <li>Khichdi nights when the plate wants brightness</li>
  <li>Travel tiffin with thepla and a small dabba</li>
</ul>

<h2>Why mustard oil &amp; spice logic matter</h2>
<p>Traditional Kathiawadi jars rely on spice and oil character rather than heavy artificial preservatives. That is why moisture control at home matters as much as the recipe in the kitchen.</p>
""",
        },
        "buy-gunda-keri-online-guide-the-pickle-affair-20-sep": {
            "exact": True,
            "title": "Buy Gunda Keri Online: How to Choose Lasode ka Achar",
            "tags": "Buying Guides, gunda keri, lasode ka achar",
            "image": "gunda-keri-pickle-lasode-ka-achar-gujarati",
            "excerpt": (
                "Buying Gunda Keri (Lasode ka Achar) online? Check style, ingredients, FSSAI context, "
                "storage guidance, and how it fits Gujarati meals — then choose with confidence."
            )[:155],
            "cluster": "Buying Guides",
            "intent": "Transactional / commercial investigation",
            "products": ["gunda-keri-pickle-lasode-ka-achar-gujarati"],
            "related": [R_BUY, R_STORE, R_KHICHDI, R_BAA, R_KERI],
            "faqs": [
                ("What is Gunda Keri?", "Gunda Keri (Lasode ka Achar) is a Gujarati specialty pickle pairing gunda with keri character — a regional jar beyond everyday mango-only achar."),
                ("What should I check before buying online?", "Style match for your meals, recognisable ingredients, clear storage/shelf guidance, and hygienic production context (e.g. FSSAI-certified kitchen)."),
                ("Is cheapest always best?", "No. Match the jar to how you eat, then compare transparency of ingredients and storage advice."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p>When you <strong>buy Gunda Keri online</strong>, prioritise clear style description (Lasode ka Achar), ingredients you recognise, storage guidance, and a maker who explains the jar honestly — not only the lowest price.</p>

<h2>What Gunda Keri / Lasode ka Achar is</h2>
<p>Gunda Keri is a Gujarati specialty achar. Families often seek it when they want something beyond standard mango pickle — a regional flavour for everyday thalis and comfort meals like khichdi.</p>

<h2>Buying checklist</h2>
<ol>
  <li>Confirm you want the gunda + keri style (not a generic “mixed pickle” label).</li>
  <li>Read ingredients you recognise.</li>
  <li>Prefer clear storage and shelf-life guidance on the product page/label.</li>
  <li>Start with one jar before gifting a full set.</li>
  <li>Check shipping and packaging expectations for glass jars.</li>
</ol>

<h2>How it fits meals</h2>
<p>Serve a spoon with roti, khichdi, or dal-rice. Specialty jars shine when the rest of the plate is simple.</p>

<h2>What The Pickle Affair emphasises</h2>
<p>Handmade Kathiawadi character, no synthetic colours, FSSAI-certified kitchen context, and glass packaging suited to home storage habits.</p>
""",
        },
        "gujarati-keri-achar-guide-the-pickle-affair-20-sep": {
            "exact": True,
            "title": "Gujarati Keri Achar: Traditional Homemade Mango Pickle Guide",
            "tags": "Heritage Recipes, gujarati keri achar, homemade mango pickle",
            "image": "mango-pickle-traditional-keri-achar-gujarati",
            "excerpt": (
                "Gujarati Keri Achar explained — what traditional homemade mango pickle is, how it fits "
                "Kathiawadi meals, and how to choose a jar without keyword stuffing."
            )[:155],
            "cluster": "Heritage Recipes",
            "intent": "Heritage + commercial",
            "products": ["mango-pickle-traditional-keri-achar-gujarati", "katka-keri-pickle-homemade-gujarati-mango-achar"],
            "related": [R_MEETHI, R_STORE, R_MUSTARD, R_BAA, R_BUY],
            "faqs": [
                ("What is Gujarati Keri Achar?", "It is traditional Gujarati mango pickle — keri cured with spices and oil for everyday meals like roti and thepla."),
                ("Is it the same as Meethi Keri?", "No. Keri achar often leans savoury/spicy; Meethi Keri is the sweet mango style."),
                ("Where is The Pickle Affair based?", "We ship handmade pickles from our kitchen context in Virar, Maharashtra, across India."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p><strong>Gujarati Keri Achar</strong> is traditional homemade mango pickle from Gujarati and Kathiawadi kitchens — the everyday jar beside roti, thepla, and dal-rice. This guide orients you to the style before you pick a product.</p>

<h2>What “keri achar” means</h2>
<p>Keri is mango in Gujarati cooking language. Achar is the preserved pickle. Together they signal a mango pickle tradition with regional spice logic — not a single identical recipe across every home.</p>

<h2>Where it sits among other jars</h2>
<ul>
  <li>Everyday spicy/tangy keri achar for roti meals</li>
  <li>Sweet styles such as Meethi Keri and Chhundo</li>
  <li>Specialty jars such as Gunda Keri and Katka Keri</li>
  <li>Methi-forward styles such as Chana Keri Methi</li>
</ul>

<h2>How families typically serve it</h2>
<p>A spoon on the side. Let dal, rice, or rotla stay the hero; pickle adds contrast.</p>

<h2>Choosing a jar</h2>
<p>Match heat and tang to your meals, read ingredients, and keep storage habits tight (dry spoon, sealed jar). For buying tips, see our online buying guide.</p>
""",
        },
        "chana-keri-methi-pickle-guide-the-pickle-affair-20-sep": {
            "exact": True,
            "title": "Chana Keri Methi Pickle: Methia Keri Flavour Guide",
            "tags": "Health & Spices, chana keri methi, fenugreek mango pickle",
            "image": "chana-keri-methi-pickle-gujarati-methia-achar",
            "excerpt": (
                "Chana Keri Methi (Methia Keri) explained — how fenugreek shapes mango pickle flavour, "
                "bitterness balance, and how to serve it with Gujarati meals."
            )[:155],
            "cluster": "Health & Spices",
            "intent": "Ingredient + commercial",
            "products": ["chana-keri-methi-pickle-gujarati-methia-achar"],
            "related": [R_METHI, R_MUSTARD, R_KERI, R_STORE, R_BUY],
            "faqs": [
                ("What is Chana Keri Methi?", "A Gujarati methi-forward mango pickle style (Methia Keri) where fenugreek character sits with keri and spices."),
                ("Why can methi taste bitter?", "Fenugreek naturally carries bitterness; traditional kitchens balance it so the jar stays savoury and aromatic, not harsh."),
                ("Do you make medical claims about methi?", "No. We discuss culinary flavour only — not medical or nutritional promises."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p><strong>Chana Keri Methi</strong> (Methia Keri) is a fenugreek-forward Gujarati mango pickle style. This guide explains the flavour role of methi — without medical claims — and how to serve the jar at home.</p>

<h2>Role of fenugreek in the pickle</h2>
<p>Methi brings aroma and a distinctive bitter-savoury edge. In Baa-style kitchens, the goal is balance: methi should be present, not punishing.</p>

<h2>How it differs from plain keri achar</h2>
<p>Standard keri achar emphasises mango + chilli/tang. Methia styles push fenugreek into the foreground, which some families prefer with thepla and travel tiffins.</p>

<h2>Serving ideas</h2>
<ul>
  <li>Thepla breakfasts and train snacks</li>
  <li>Simple dal-rice when you want a punchier spoon</li>
  <li>Pairing beside a sweeter jar (Meethi Keri) for contrast on the same thali</li>
</ul>

<h2>Storage</h2>
<p>Same achar rules: sealed, cool, dry, clean dry spoon. Label dates win over guesswork.</p>
""",
        },
        "why-mustard-oil-is-used-in-gujarati-and-kathiawadi-pickles": {
            "exact": True,
            "title": "Why Mustard Oil Is Used in Gujarati and Kathiawadi Pickles",
            "tags": "Health & Spices, mustard oil in pickle",
            "image": "mango-pickle-traditional-keri-achar-gujarati",
            "excerpt": (
                "Why mustard oil shows up in Gujarati and Kathiawadi pickles — flavour, tradition, "
                "and practical jar care — without medical or ‘superfood’ claims."
            )[:155],
            "cluster": "Health & Spices",
            "intent": "Ingredient education",
            "products": ["mango-pickle-traditional-keri-achar-gujarati", "katka-keri-pickle-homemade-gujarati-mango-achar"],
            "related": [R_STORE, R_KERI, R_KATKA, R_BAA, R_METHI],
            "faqs": [
                ("Why use mustard oil in pickle?", "In many Gujarati/Kathiawadi traditions, mustard oil contributes aroma and is part of how jars are cured and kept — culinary tradition, not a medical prescription."),
                ("Is every pickle identical in oil choice?", "No. Houses and styles vary. Always read the label for the jar you buy."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p>Mustard oil is common in many Gujarati and Kathiawadi pickle traditions because of its aroma and how it works with spice-cured jars — a culinary choice, not a medical claim.</p>

<h2>Flavour role</h2>
<p>Mustard oil has a distinctive pungency that sits well with mango, chilli, and methi-forward profiles. It is one reason regional achar smells “like home” to many families.</p>

<h2>Practical jar habits</h2>
<p>Oil-cured styles still need dry spoons and sealed storage. Oil does not forgive wet utensils or hot stove-top storage.</p>

<h2>How we talk about it at The Pickle Affair</h2>
<p>We stick to traditional cooking character and label transparency. We do not invent health miracles or certifications we do not hold beyond our stated FSSAI-certified kitchen context.</p>
""",
        },
        "pickle-with-khichdi-comfort-pairings-from-a-kathiawadi-kitchen": {
            "exact": True,
            "title": "Pickle with Khichdi: Comfort Pairings from a Kathiawadi Kitchen",
            "tags": "Pickle Pairings, pickle with khichdi",
            "image": "katka-keri-pickle-homemade-gujarati-mango-achar",
            "excerpt": (
                "What pickle goes with khichdi? Bright, spicy, or specialty Gujarati jars that cut "
                "through comfort — serving ideas from a Kathiawadi kitchen."
            )[:155],
            "cluster": "Pickle Pairings",
            "intent": "Serving/pairing",
            "products": ["katka-keri-pickle-homemade-gujarati-mango-achar", "gunda-keri-pickle-lasode-ka-achar-gujarati"],
            "related": [R_KATKA, R_GUNDA, R_MEETHI, R_STORE, R_BUY],
            "faqs": [
                ("What pickle goes with khichdi?", "Many homes prefer a brighter or spicier achar to cut the softness of khichdi — Katka Keri or specialty jars like Gunda Keri are natural starting points."),
                ("Should pickle be mixed into khichdi?", "Usually no — serve a spoon on the side so each bite can choose the contrast."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p>Khichdi loves contrast. A spoon of Gujarati achar on the side — spicy keri, Katka Keri, or a specialty jar like Gunda Keri — brightens a soft, comforting plate without taking it over.</p>

<h2>How Gujarati homes typically serve pickle</h2>
<p>Pickle is a companion. Keep dal/rice/khichdi as the hero; add achar in small spoons.</p>

<h2>Pairing ideas</h2>
<ul>
  <li>Weeknight khichdi + Katka Keri for sharpness</li>
  <li>Simple moong khichdi + Gunda Keri for a specialty note</li>
  <li>When you want sweet contrast, add Meethi Keri on the same thali</li>
</ul>
""",
        },
        "how-baa-s-kitchen-makes-traditional-gujarati-pickles": {
            "exact": True,
            "title": "How Baa’s Kitchen Makes Traditional Gujarati Pickles",
            "tags": "Artisanal Craft, traditional gujarati pickle making",
            "image": "mango-pickle-traditional-keri-achar-gujarati",
            "excerpt": (
                "What “Baa’s Kitchen” means at The Pickle Affair — traditional Kathiawadi pickle sense, "
                "hygienic preparation, and what we do (and don’t) claim."
            )[:155],
            "cluster": "Artisanal Craft",
            "intent": "Heritage/story",
            "products": ["mango-pickle-traditional-keri-achar-gujarati"],
            "related": [R_KERI, R_MUSTARD, R_STORE, R_BUY, R_MEETHI],
            "faqs": [
                ("What does Baa’s Kitchen mean?", "It names the traditional cooking sensibility behind The Pickle Affair — family Kathiawadi pickle logic, not a fictional biography."),
                ("Do you disclose exact recipes?", "House quantities stay proprietary. We share useful tradition and process context without inventing numbers."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p>The Pickle Affair’s kitchen follows a family Kathiawadi approach: careful produce, traditional spice logic, and small-batch attention — jars meant for everyday Gujarati meals.</p>

<h2>What we emphasise</h2>
<ul>
  <li>Recognisable regional pickle styles</li>
  <li>Hygienic, FSSAI-certified preparation context</li>
  <li>No synthetic colours</li>
  <li>Glass jars suited to home storage habits</li>
</ul>

<h2>What we do not fabricate</h2>
<p>We do not invent awards, medical benefits, or exact “secret” quantities for content marketing. If it is not true for the business, it does not go on Kitchen Tales.</p>
""",
        },
        "how-to-buy-authentic-gujarati-pickle-online-without-guesswork": {
            "exact": True,
            "title": "How to Buy Authentic Gujarati Pickle Online (Without Guesswork)",
            "tags": "Buying Guides, buy gujarati pickle online",
            "image": "mango-pickle-traditional-keri-achar-gujarati",
            "excerpt": (
                "A practical checklist for buying authentic Gujarati pickle online — style match, "
                "ingredients, FSSAI context, storage clarity, and starting with one jar."
            )[:155],
            "cluster": "Buying Guides",
            "intent": "Commercial investigation",
            "products": ["mango-pickle-traditional-keri-achar-gujarati", "gunda-keri-pickle-lasode-ka-achar-gujarati"],
            "related": [R_GUNDA, R_KERI, R_STORE, R_BAA, R_MEETHI],
            "faqs": [
                ("How do I avoid guesswork online?", "Match pickle style to your meals first, then read ingredients and storage guidance — price alone is a weak signal."),
                ("Should I buy a full gift set first?", "Often better to start with one jar you know you will finish."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p>Buy Gujarati pickle online by matching <strong>style to meals</strong>, reading ingredients you recognise, and preferring makers who explain storage clearly — including FSSAI-certified kitchen context when claimed.</p>

<h2>Checklist</h2>
<ol>
  <li>Thepla vs khichdi vs dal-rice — pick the flavour lane.</li>
  <li>Ingredients you recognise.</li>
  <li>Storage and shelf-life guidance on page/label.</li>
  <li>Packaging suited to shipping glass jars.</li>
  <li>Start with one jar before bulk gifting.</li>
</ol>
""",
        },
        "chhundo-traditional-gujarati-sweet-shredded-mango-achar": {
            "exact": True,
            "title": "Chhundo: Traditional Gujarati Sweet Shredded Mango Achar",
            "tags": "Heritage Recipes, chhundo pickle",
            "image": "chhundo-pickle-sweet-shredded-mango-achar-gujarati",
            "excerpt": (
                "What is Chhundo? A traditional Gujarati sweet shredded mango achar — texture, "
                "serving ideas, and how it differs from Meethi Keri."
            )[:155],
            "cluster": "Heritage Recipes",
            "intent": "Informational",
            "products": ["chhundo-pickle-sweet-shredded-mango-achar-gujarati", "sweet-mango-pickle-meethi-keri-achar-homemade"],
            "related": [R_MEETHI, R_STORE, R_BAA, R_BUY, R_KERI],
            "faqs": [
                ("What is Chhundo?", "Chhundo is a Gujarati sweet shredded mango achar — relish-like texture for everyday meals and festive thalis."),
                ("Chhundo vs Meethi Keri?", "Chhundo is typically shredded; Meethi Keri centres on sweet keri pieces. Choose by texture."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p><strong>Chhundo</strong> is traditional Gujarati sweet shredded mango achar — bright, relish-like, and meant for a spoon beside savoury breads and dal-rice.</p>

<h2>Texture &amp; taste</h2>
<p>Shredded mango gives a different mouthfeel from piece-style Meethi Keri. Sweetness leads; spice keeps it in the achar family.</p>

<h2>Serving ideas</h2>
<ul>
  <li>Thepla and rotla</li>
  <li>Dal-bhaat contrast</li>
  <li>Gift baskets with a spicier keri jar</li>
</ul>

<h2>Storage</h2>
<p>Sealed, cool, dry, clean dry spoon. Label dates are authoritative.</p>
""",
        },
        "how-to-store-indian-pickles-keep-gujarati-achar-fresh-for-months": {
            "exact": True,
            "title": "How to Store Indian Pickles: Keep Gujarati Achar Fresh for Months",
            "tags": "Buying Guides, how to store indian pickles",
            "image": "mango-pickle-traditional-keri-achar-gujarati",
            "excerpt": (
                "How to store Indian and Gujarati pickles at home — dry spoons, cool cupboards, "
                "oil coverage, and when to stop using a jar."
            )[:155],
            "cluster": "Pickle Guides",
            "intent": "How-to",
            "products": ["mango-pickle-traditional-keri-achar-gujarati"],
            "related": [R_SHELF, R_KATKA, R_MEETHI, R_MUSTARD, R_BUY],
            "faqs": [
                ("What is the #1 storage mistake?", "A wet spoon — moisture is one of the fastest ways to spoil traditional achar."),
                ("Fridge or cupboard?", "Follow your jar label. Many oil-cured Gujarati pickles are stored cool and dry in a cupboard when sealed properly."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p>Store Indian pickles in a cool, dry place, always use a clean dry spoon, and keep the jar sealed. Oil-cured Gujarati achar usually keeps well when protected from moisture and direct sun.</p>

<h2>Why storage matters</h2>
<p>Traditional Kathiawadi pickles rely on salt, spices, and oil — not heavy artificial preservatives. Home hygiene is part of shelf life.</p>

<h2>Step-by-step habits</h2>
<ol>
  <li>Seal after every use.</li>
  <li>Clean dry spoon only.</li>
  <li>Away from stove heat and sun.</li>
  <li>Humid kitchen → cupboard away from the sink.</li>
  <li>Keep pieces under oil where the style uses oil curing.</li>
</ol>
""",
        },
        "how-long-does-mango-pickle-last-shelf-life-freshness-signs": {
            "exact": True,
            "title": "How Long Does Mango Pickle Last? Shelf Life & Freshness Signs",
            "tags": "Buying Guides, how long does mango pickle last",
            "image": "sweet-mango-pickle-meethi-keri-achar-homemade",
            "excerpt": (
                "How long does mango pickle last? Follow the jar label, control moisture after opening, "
                "and use sensory checks — we do not invent exact month counts."
            )[:155],
            "cluster": "Pickle Guides",
            "intent": "Informational",
            "products": ["mango-pickle-traditional-keri-achar-gujarati", "sweet-mango-pickle-meethi-keri-achar-homemade"],
            "related": [R_STORE, R_MEETHI, R_KERI, R_KATKA, R_BUY],
            "faqs": [
                ("How long does mango pickle last?", "Unopened shelf life is what the jar label states. After opening, hygiene and storage decide quality more than a generic number."),
                ("When should I discard a jar?", "Unusual smell, mould, or unexpected fizzing — do not taste; discard."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p>Unopened, well-made mango pickle typically lasts many months when stored correctly. After opening, quality depends on hygiene and storage — always follow the jar’s best-before guidance and trust your senses.</p>

<h2>What affects shelf life</h2>
<ul>
  <li>Moisture from wet spoons</li>
  <li>Heat and sunlight</li>
  <li>Seal quality</li>
  <li>Pickle style (oil-cured, sweet, shredded, methi-forward)</li>
</ul>

<h2>Practical freshness checks</h2>
<p>Read the printed date, keep oil coverage consistent where applicable, and stop using the pickle if aroma or appearance changes unexpectedly.</p>
<p><em>We do not invent exact month counts beyond packaging. The label is authoritative.</em></p>
""",
        },
        "fenugreek-methi-in-mango-pickle-flavour-bitterness-chana-keri": {
            "exact": True,
            "title": "Fenugreek (Methi) in Mango Pickle: Flavour, Bitterness & Chana Keri Methi",
            "tags": "Health & Spices, fenugreek in mango pickle",
            "image": "chana-keri-methi-pickle-gujarati-methia-achar",
            "excerpt": (
                "Why fenugreek (methi) is used in mango pickle — flavour, bitterness balance, and "
                "how Chana Keri Methi fits Gujarati kitchens (culinary only)."
            )[:155],
            "cluster": "Health & Spices",
            "intent": "Ingredient education",
            "products": ["chana-keri-methi-pickle-gujarati-methia-achar"],
            "related": [R_CHANA, R_MUSTARD, R_KERI, R_STORE, R_BUY],
            "faqs": [
                ("Why is methi bitter?", "Fenugreek naturally carries bitterness; traditional pickle-making balances it inside the spice mix."),
                ("Is this a health article?", "No — culinary flavour education only. No medical claims."),
            ],
            "middle": """
<h2>Quick answer</h2>
<p>Fenugreek (methi) shapes aroma and a savoury-bitter edge in many Gujarati mango pickles. In jars like Chana Keri Methi, that character is intentional — balanced, not harsh — and discussed here as food, not medicine.</p>

<h2>Flavour role</h2>
<p>Methi supports depth beside mango and chilli. Some families specifically seek methia keri for thepla and travel meals.</p>

<h2>Bitterness balance</h2>
<p>If methi dominates unpleasantly, the jar is poorly balanced for that eater’s preference. Choose styles accordingly; do not assume every mango pickle is methi-forward.</p>
""",
        },
    }


def clean_title(title: str) -> str:
    t = re.sub(r"\s*\|\s*The Pickle Affair.*$", "", title, flags=re.I)
    t = re.sub(r"\s*\(20 Sep\)\s*$", "", t, flags=re.I)
    return t.strip()


def match_profile(handle: str, catalog: dict[str, dict]) -> dict | None:
    if handle in catalog:
        return catalog[handle]
    # fuzzy: longest matching key contained in handle
    best = None
    best_len = 0
    for key, prof in catalog.items():
        if key in handle and len(key) > best_len:
            best = prof
            best_len = len(key)
    return best


def unpublish(article_id: int, title: str) -> None:
    payload = {"article": {"id": article_id, "published": False}}
    if DRY_RUN:
        print(f"DRY unpublish {article_id}: {title}")
        return
    api("PUT", f"/blogs/{BLOG_ID}/articles/{article_id}.json", payload)
    print(f"UNPUBLISHED {article_id}: {title}")


def update_article(art: dict, prof: dict) -> None:
    image_handle = prof["image"]
    image = PRODUCTS[image_handle]["image"] if image_handle in PRODUCTS else PRODUCTS[next(iter(PRODUCTS))]["image"]
    body = wrap_article(
        lead=prof["excerpt"],
        middle=prof["middle"],
        products=prof["products"],
        related=prof["related"],
        faqs=prof["faqs"],
        cluster=prof["cluster"],
        intent=prof["intent"],
    )
    title = prof["title"]
    payload = {
        "article": {
            "id": art["id"],
            "title": title,
            "author": "Baa & The Pickle Affair Kitchen",
            "tags": prof["tags"],
            "summary_html": f"<p>{prof['excerpt']}</p>",
            "body_html": body,
            "published": True,
            "image": {"src": image, "alt": title},
        }
    }
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    if DRY_RUN:
        print(f"DRY update {art['id']} {art.get('handle')} → {title!r} (~{words} words)")
        return
    api("PUT", f"/blogs/{BLOG_ID}/articles/{art['id']}.json", payload)
    print(f"UPDATED {art['id']} /{art.get('handle')} → {title} (~{words} words)")


def main() -> None:
    print("=== Rewrite live Kitchen Tales to BLOG.md ===")
    if DRY_RUN:
        print("DRY_RUN=1 — no writes")
    articles = list_articles()
    published = [a for a in articles if a.get("published_at")]
    print(f"Fetched {len(articles)} articles · {len(published)} published")

    catalog = profiles()
    updated = unpublished = skipped = 0

    for art in articles:
        handle = art.get("handle") or ""
        title = art.get("title") or ""
        is_live = bool(art.get("published_at"))

        if handle in UNPUBLISH_HANDLES and is_live:
            # Only unpublish if a better canonical exists live
            unpublish(art["id"], title)
            unpublished += 1
            continue

        if not is_live:
            skipped += 1
            continue

        prof = match_profile(handle, catalog)
        if not prof:
            print(f"SKIP no profile: {handle} | {title}")
            skipped += 1
            continue

        # Prefer exact-handle profiles; if profile is for another canonical, still update this live URL
        update_article(art, prof)
        updated += 1

    print(f"Done. updated={updated} unpublished={unpublished} skipped={skipped}")


if __name__ == "__main__":
    main()
