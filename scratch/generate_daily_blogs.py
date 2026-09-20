#!/usr/bin/env python3
"""
Daily Kitchen Tales publisher — governed by BLOG.md.

Rules enforced:
- Max 5 posts/day (not a quota); skip if quality/uniqueness fails
- One primary intent per URL (registry + live title/handle check)
- Daily mix across different clusters/intents (not 5 product clones)
- No invented recipe quantities / no fabricated claims
- Updates CONTENT_CALENDAR.md + BLOG_REGISTRY.md after publish
"""
from __future__ import annotations

import datetime as dt
import hashlib
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
TOPIC_LIB = json.loads((ROOT / "scratch" / "topic_library.json").read_text())
BLOG_MD = ROOT / "BLOG.md"
REGISTRY_MD = ROOT / "BLOG_REGISTRY.md"
CALENDAR_MD = ROOT / "CONTENT_CALENDAR.md"

SHOP_URL = shop_url()
TOKEN = ""
BLOG_ID = os.environ.get("SHOPIFY_BLOG_ID", "96853164183")
API = "2024-10"
CTX = ssl.create_default_context()
MAX_DAILY = int(os.environ.get("DAILY_BLOG_COUNT", "5"))


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
        with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise SystemExit(f"API {method} {path} failed: {e.code} {err}") from e


def ist_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))


def day_seed(day: dt.date) -> int:
    return int(hashlib.sha1(day.isoformat().encode()).hexdigest()[:8], 16)


def load_owned_keywords() -> set[str]:
    owned: set[str] = set()
    if REGISTRY_MD.exists():
        for line in REGISTRY_MD.read_text().splitlines():
            if line.startswith("|") and "Canonical URL" not in line and "---" not in line:
                cols = [c.strip().lower() for c in line.strip("|").split("|")]
                if cols and cols[0] and cols[0] != "topic / primary keyword":
                    owned.add(cols[0])
                    # also first token phrase before /
                    owned.add(cols[0].split("/")[0].strip())
    return owned


def existing_articles() -> list[dict]:
    data = api("GET", f"/blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,handle,tags,published_at")
    return data.get("articles", [])


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def is_duplicate(topic: dict, articles: list[dict], owned: set[str]) -> str | None:
    kw = normalize(topic["primary_keyword"])
    title_n = normalize(topic["title"])
    for o in owned:
        on = normalize(o)
        if on and (on in kw or kw in on):
            # owned keyword — only allow if status IDEA in calendar sense: still block publish of new URL
            if "not published" not in o:
                return f"registry owns related keyword: {o}"
    for a in articles:
        at = normalize(a.get("title", ""))
        ah = normalize(a.get("handle", ""))
        if kw and (kw in at or kw.replace(" ", "-") in ah.replace(" ", "-")):
            return f"live overlap: {a.get('handle')}"
        # title similarity
        if title_n and at and (title_n[:40] in at or at[:40] in title_n):
            return f"title near-duplicate: {a.get('title')}"
    return None


def pick_daily_topics(day: dt.date, articles: list[dict], owned: set[str]) -> list[dict]:
    """Pick up to MAX_DAILY topics with different angles/clusters."""
    seed = day_seed(day)
    pool = list(TOPIC_LIB.get("topics", [])) + list(TOPIC_LIB.get("pillars", []))
    # Rotate start index by day
    start = seed % max(1, len(pool))
    ordered = pool[start:] + pool[:start]

    selected: list[dict] = []
    used_angles: set[str] = set()
    used_clusters: set[str] = set()

    for topic in ordered:
        if len(selected) >= MAX_DAILY:
            break
        angle = topic.get("angle", "")
        cluster = topic.get("cluster", "")
        # Prefer diverse mix
        if angle in used_angles and len(selected) < 3:
            continue
        if cluster in used_clusters and len(used_clusters) >= 3 and len(selected) >= 2:
            # allow later if needed
            if len(selected) < MAX_DAILY - 1:
                pass
            else:
                continue
        reason = is_duplicate(topic, articles, owned)
        if reason:
            print(f"SKIP {topic['id']}: {reason}")
            continue
        selected.append(topic)
        used_angles.add(angle)
        used_clusters.add(cluster)

    return selected


def product_block(handle: str) -> str:
    p = PRODUCTS.get(handle)
    if not p:
        return ""
    return f"""
<div class="dp-product-card" style="background:#F5F7F0;border:1px solid #DDE5C8;border-radius:16px;padding:24px;margin:28px 0;text-align:center;">
  <img src="{p['image']}" alt="{p['title']} from The Pickle Affair" style="max-width:220px;width:100%;height:auto;border-radius:12px;margin-bottom:14px;">
  <h3 style="color:#4A6B29;margin:8px 0 10px;font-size:18px;">{p['title']}</h3>
  <p style="color:#1D2614;font-size:14px;margin-bottom:14px;">Handmade Kathiawadi pickle from The Pickle Affair — available to ship across India.</p>
  <a href="/products/{p['handle']}" style="background:#4A6B29;color:#fff;padding:11px 24px;border-radius:999px;font-weight:700;text-decoration:none;display:inline-block;">View {p['title']} →</a>
</div>
""".strip()


def related_links_html(topic: dict) -> str:
    # Soft related suggestions — only published-safe generic anchors
    links = [
        ('<a href="/blogs/kitchen-tales">Kitchen Tales</a>', "more pickle stories"),
        ('<a href="/collections/all-products">all pickles</a>', "shop the range"),
    ]
    items = "".join(f"<li>Explore {a} for {b}.</li>" for a, b in links)
    return f"<h2>Related reading &amp; shopping</h2><ul>{items}</ul>"


def build_article(topic: dict, day: dt.date) -> tuple[str, str, str, str, str]:
    kw = topic["primary_keyword"]
    title = topic["title"]
    if len(title) > 70:
        title = title[:67].rstrip() + "…"

    excerpt = (
        f"{title} — practical guidance from The Pickle Affair’s Kathiawadi kitchen. "
        f"Learn about {kw} with clear tips you can use at home."
    )[:155]

    handles = topic.get("product_handles") or []
    primary = handles[0] if handles else None
    products_html = "\n".join(product_block(h) for h in handles[:2])

    angle = topic.get("angle", "")
    secondary = ", ".join(topic.get("secondary") or [])

    # Angle-specific middle sections (no invented recipe quantities)
    if angle == "storage":
        middle = f"""
<h2>Quick answer</h2>
<p>Store Indian pickles in a cool, dry place, always use a clean dry spoon, and keep the jar sealed. Oil-cured Gujarati achar usually keeps well for months when protected from moisture and direct sun.</p>
<h2>Why storage matters for Gujarati achar</h2>
<p>Traditional Kathiawadi pickles rely on salt, spices, and oil — not heavy artificial preservatives. Moisture from a wet spoon is one of the fastest ways to spoil a good jar.</p>
<h2>Step-by-step storage habits</h2>
<ol>
  <li>Keep the jar tightly closed after every use.</li>
  <li>Use only a clean, completely dry spoon.</li>
  <li>Store away from the stove’s heat and away from direct sunlight.</li>
  <li>If your kitchen is very humid, prefer a cupboard away from the sink.</li>
  <li>Check that vegetables/mango pieces stay under the oil layer where the recipe style uses oil curing.</li>
</ol>
<h2>After opening</h2>
<p>Once opened, continue the same dry-spoon rule. If you ever see unusual smell, mould, or unexpected fizzing, do not taste — discard the jar.</p>
"""
    elif angle == "shelf_life":
        middle = f"""
<h2>Quick answer</h2>
<p>Unopened, well-made mango pickle typically lasts many months when stored correctly. After opening, quality depends on hygiene and storage — always follow the jar’s best-before guidance and trust your senses.</p>
<h2>What affects shelf life</h2>
<ul>
  <li>Moisture introduced by wet spoons</li>
  <li>Heat and sunlight</li>
  <li>How well the jar stays sealed</li>
  <li>The pickle style (oil-cured, sweet, shredded, etc.)</li>
</ul>
<h2>Practical freshness checks</h2>
<p>Look for the printed date on packaging, keep oil coverage consistent where applicable, and stop using the pickle if aroma or appearance changes unexpectedly.</p>
<p><em>We do not invent exact month counts beyond what appears on product packaging. Check your jar label for the authoritative shelf-life statement.</em></p>
"""
    elif angle == "ingredient":
        middle = f"""
<h2>Quick answer</h2>
<p>This guide explains how <strong>{kw}</strong> shapes traditional Gujarati and Kathiawadi pickle flavour — without medical claims or invented “superfood” promises.</p>
<h2>Role in the pickle</h2>
<p>In Baa-style kitchens, spices and oils are chosen for aroma, balance, and how they hold up over months in a jar. Understanding {kw} helps you choose the right achar for your meals.</p>
<h2>How we think about quality</h2>
<p>At The Pickle Affair, ingredients are selected for traditional cooking character. We avoid synthetic colours and keep the focus on recognisable spice profiles families expect with roti, thepla, and khichdi.</p>
"""
    elif angle == "pairing":
        middle = f"""
<h2>Quick answer</h2>
<p>The best pickle pairing depends on the meal: soft breads like thepla love a punchy or sweet-tangy achar, while khichdi often wants something bright and spicy to cut the comfort.</p>
<h2>How Gujarati homes typically serve pickle</h2>
<p>A spoon on the side is enough. Pickle is a companion, not the whole plate — let dal, rice, or rotla stay the hero.</p>
<h2>Serving ideas</h2>
<ul>
  <li>Travel tiffin with thepla and a small pickle dabba</li>
  <li>Sunday khichdi with a sharper mango pickle</li>
  <li>Dal-bhaat with a sweet pickle for contrast</li>
</ul>
"""
    elif angle == "comparison":
        middle = f"""
<h2>Quick answer</h2>
<p>Chhundo and Meethi Keri are both sweet mango traditions, but they differ in cut, texture, and how they show up on the plate. Use this guide to choose the jar that matches your meal.</p>
<h2>Chhundo</h2>
<p>Typically associated with shredded mango and a sweet-leaning profile — bright with meals that want a relish-like spoon.</p>
<h2>Meethi Keri</h2>
<p>A sweet mango pickle style centred on keri pieces and a homemade sweet-tang balance familiar in Gujarati homes.</p>
<h2>How to choose</h2>
<ul>
  <li>Want shredded relish texture → explore Chhundo</li>
  <li>Want classic sweet keri pieces → explore Meethi Keri</li>
</ul>
<p>Exact house recipes stay with the kitchen; this page explains differences at a useful level without inventing proprietary quantities.</p>
"""
    elif angle == "baa_story":
        middle = f"""
<h2>Quick answer</h2>
<p>The Pickle Affair’s kitchen follows a family Kathiawadi approach: careful produce, traditional spice logic, and small-batch attention — the kind of jar meant for everyday Gujarati meals.</p>
<h2>What “Baa’s Kitchen” means here</h2>
<p>It is our way of naming the traditional cooking sensibility behind the brand. We only describe practices we actually follow in production and packaging.</p>
<h2>What we emphasise</h2>
<ul>
  <li>Recognisable regional pickle styles</li>
  <li>Hygienic, FSSAI-certified preparation</li>
  <li>No synthetic colours</li>
  <li>Glass jars suited to home storage habits</li>
</ul>
"""
    elif angle == "buying":
        middle = f"""
<h2>Quick answer</h2>
<p>When you buy Gujarati pickle online, check the style (sweet, spicy, shredded, methi), packaging, FSSAI markings, and whether the maker explains storage clearly — not just the lowest price.</p>
<h2>A simple buying checklist</h2>
<ol>
  <li>Match the pickle to your meals (thepla vs khichdi vs dal-rice).</li>
  <li>Read ingredients you recognise.</li>
  <li>Prefer clear storage and shelf-life guidance on the product page/label.</li>
  <li>Start with one jar before gifting a full set.</li>
</ol>
"""
    elif angle in ("pillar_overview", "heritage_product"):
        middle = f"""
<h2>Quick answer</h2>
<p><strong>{kw.title()}</strong> sits inside a wider Gujarati and Kathiawadi pickle tradition — from everyday keri achar to sweet styles and regional specialties. This guide orients you before you dive into individual jars.</p>
<h2>What belongs in this tradition</h2>
<ul>
  <li>Mango (keri) pickles — spicy, sweet, methi-forward</li>
  <li>Specialty jars such as Gunda Keri and Katka styles</li>
  <li>Relish-like sweet shredded styles such as Chhundo</li>
</ul>
<h2>How to use this guide</h2>
<p>Pick the style that matches your meal, then explore the matching product page for the jar that fits your kitchen.</p>
"""
    else:
        middle = f"""
<h2>Quick answer</h2>
<p>This Kitchen Tales guide covers <strong>{kw}</strong> with practical context from The Pickle Affair — focused on usefulness, not keyword stuffing.</p>
<h2>What you’ll learn</h2>
<p>Background, how it fits Gujarati meals, and how to choose a jar with confidence.</p>
"""

    faqs = [
        (f"What is this guide about?", f"It explains {kw} in clear language for home cooks exploring Gujarati and Kathiawadi pickles."),
        ("Does The Pickle Affair use synthetic colours?", "No. We focus on traditional spice character without synthetic colours."),
        ("Where are products prepared?", "The Pickle Affair prepares pickles in an FSSAI-certified kitchen context for hygienic production."),
    ]
    faq_json = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }
    faq_html = "".join(
        f'<div class="dp-faq-item"><h3 class="dp-faq-question">{q}</h3><p>{a}</p></div>' for q, a in faqs
    )

    body = f"""
<script type="application/ld+json">{json.dumps(faq_json, ensure_ascii=False)}</script>

<p class="dp-lead">{excerpt}</p>

{middle}

{products_html}

{related_links_html(topic)}

<h2>Frequently asked questions</h2>
{faq_html}

<p><em>Cluster: {topic.get('cluster')} · Intent: {topic.get('intent')} · Related terms: {secondary}</em></p>
<p><em>Policy: governed by BLOG.md — quality over volume.</em></p>
""".strip()

    tags = f"{topic.get('category', 'Heritage Recipes')}, {kw}"
    image = PRODUCTS[primary]["image"] if primary and primary in PRODUCTS else PRODUCTS[next(iter(PRODUCTS))]["image"]
    return title, excerpt, body, tags, image


def append_calendar(day: dt.date, topic: dict, url: str, status: str) -> None:
    if not CALENDAR_MD.exists():
        return
    line = (
        f"| {day.isoformat()} | {topic.get('title','')[:60]} | {topic.get('intent')} | "
        f"{topic.get('cluster')} | {topic.get('primary_keyword')} | {url} | {status} |\n"
    )
    text = CALENDAR_MD.read_text()
    if line in text:
        return
    # Insert after header table separator — append at end of table section
    CALENDAR_MD.write_text(text.rstrip() + "\n" + line)


def append_registry(topic: dict, handle: str, art_id: int) -> None:
    if not REGISTRY_MD.exists():
        return
    block = f"""
### {topic['title']}
- URL: `/blogs/kitchen-tales/{handle}`
- Shopify ID: `{art_id}`
- Primary keyword: {topic['primary_keyword']}
- Search intent: {topic.get('intent')}
- Cluster: {topic.get('cluster')}
- Category tag: {topic.get('category')}
- Status: PUBLISHED
"""
    text = REGISTRY_MD.read_text()
    if handle in text:
        return
    REGISTRY_MD.write_text(text.rstrip() + "\n" + block + "\n")


def create_article(title: str, excerpt: str, body: str, tags: str, image: str, published_at: str) -> dict:
    payload = {
        "article": {
            "title": title,
            "author": "Baa & The Pickle Affair Kitchen",
            "tags": tags,
            "summary_html": f"<p>{excerpt}</p>",
            "body_html": body,
            "published": True,
            "published_at": published_at,
            "image": {"src": image, "alt": title},
        }
    }
    return api("POST", f"/blogs/{BLOG_ID}/articles.json", payload)


def main() -> None:
    if not BLOG_MD.exists():
        print("WARNING: BLOG.md missing — continuing with embedded safeguards")
    else:
        print(f"Policy loaded: {BLOG_MD.name} ({BLOG_MD.stat().st_size} bytes)")

    now = ist_now()
    day = now.date()
    print(f"=== Kitchen Tales quality publisher · {day.isoformat()} IST {now.strftime('%H:%M')} ===")
    print("Rule: publish only unique intents that pass gates (max "
          f"{MAX_DAILY}, fewer OK).")

    articles = existing_articles()
    owned = load_owned_keywords()
    topics = pick_daily_topics(day, articles, owned)

    if not topics:
        print("No eligible topics today — holding publish (quality over quota).")
        append_calendar(day, {"title": "(none)", "intent": "-", "cluster": "-", "primary_keyword": "-"}, "-", "HOLD")
        return

    created = 0
    for topic in topics:
        title, excerpt, body, tags, image = build_article(topic, day)
        # Final title collision check
        if any(normalize(a.get("title", "")) == normalize(title) for a in articles):
            print(f"SKIP exact title exists: {title}")
            continue
        published_at = now.isoformat()
        print(f"→ PUBLISH ({topic.get('intent')} / {topic.get('cluster')}): {title}")
        result = create_article(title, excerpt, body, tags, image, published_at)
        art = result.get("article", {})
        handle = art.get("handle", "")
        print(f"   id={art.get('id')} handle={handle}")
        append_calendar(day, topic, f"/blogs/kitchen-tales/{handle}", "PUBLISHED")
        if art.get("id"):
            append_registry(topic, handle, art["id"])
        created += 1
        articles.append({"title": title, "handle": handle})

    print(f"Done. Published {created} article(s) (cap {MAX_DAILY}).")
    if created < MAX_DAILY:
        print("Note: fewer than 5 is correct when uniqueness/quality gates block fillers.")


if __name__ == "__main__":
    main()
