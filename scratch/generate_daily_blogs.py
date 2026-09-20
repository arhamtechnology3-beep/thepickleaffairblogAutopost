#!/usr/bin/env python3
"""
The Pickle Affair — generate & publish 5 SEO/GEO/AEO blog posts daily.
Each post targets a product + collection with FAQ schema and product CTA.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scratch"))
from shopify_auth import resolve_access_token, shop_url  # noqa: E402

REGISTRY = json.loads((ROOT / "scratch" / "product_registry.json").read_text())

SHOP_URL = shop_url()
TOKEN = ""
BLOG_ID = os.environ.get("SHOPIFY_BLOG_ID", "96853164183")
API = "2024-10"
CTX = ssl.create_default_context()

ANGLES = [
    "complete buying guide",
    "traditional Kathiawadi recipe secrets",
    "health benefits and daily use tips",
    "how to store and serve at home",
    "why homemade tastes better than store brands",
    "perfect food pairings for every meal",
    "seasonal tips for authentic flavour",
]


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


def pick_targets(day: dt.date, count: int = 5) -> list[dict]:
    seed = day_seed(day)
    picks = []
    n = len(REGISTRY)
    for i in range(count):
        product = REGISTRY[(seed + i * 3) % n]
        keyword = product["keywords"][(seed + i) % len(product["keywords"])]
        angle = ANGLES[(seed + i * 2) % len(ANGLES)]
        picks.append({**product, "focus_keyword": keyword, "angle": angle, "slot": i})
    return picks


def build_html(p: dict, day: dt.date) -> tuple[str, str, str]:
    kw = p["focus_keyword"]
    title = f"{kw.title()}: {p['angle'].title()} | The Pickle Affair"
    if len(title) > 70:
        title = f"{kw.title()} Guide | The Pickle Affair"
    excerpt = (
        f"Discover authentic {kw} from The Pickle Affair — FSSAI-certified Kathiawadi "
        f"homemade pickles crafted with traditional Baa nu Athanu methods. "
        f"Learn {p['angle']} and shop {p['title']} online."
    )[:158]

    product_url = f"/products/{p['handle']}"
    collection_url = f"/collections/{p['collection']}"
    faqs = [
        (
            f"What makes {p['title']} special?",
            f"{p['title']} from The Pickle Affair is handmade in small batches using traditional "
            f"Kathiawadi recipes, cold-pressed oils, and no artificial preservatives or synthetic colours.",
        ),
        (
            f"Where can I buy {kw} online?",
            f"You can buy authentic {kw} directly from The Pickle Affair at thepickleaffair.com"
            f"{product_url}, with shipping across India.",
        ),
        (
            f"How should I store {p['title']}?",
            "Store in a cool, dry place away from direct sunlight. Always use a clean, dry spoon. "
            "Shelf life is typically about 12 months from packaging when stored properly.",
        ),
        (
            f"Is {kw} FSSAI certified?",
            "Yes. The Pickle Affair products are prepared in an FSSAI-certified kitchen under hygienic conditions.",
        ),
    ]

    faq_json = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }

    faq_html = "".join(
        f'<div class="dp-faq-item"><h3 class="dp-faq-question">{q}</h3><p>{a}</p></div>'
        for q, a in faqs
    )

    body = f"""
<script type="application/ld+json">{json.dumps(faq_json, ensure_ascii=False)}</script>

<p class="dp-lead">Looking for <strong>{kw}</strong>? The Pickle Affair brings you authentic Kathiawadi homemade pickles under the Baa nu Athanu tradition — sun-kissed, small-batch, and FSSAI certified from Virar, Maharashtra. This guide covers {p['angle']} so you can buy with confidence and serve with nostalgia.</p>

<h2>What is {kw}?</h2>
<p>{p['title']} is a heritage Gujarati pickle crafted for everyday meals. Unlike mass-produced achar, our kitchen follows traditional curing methods, premium spices, and cold-pressed oils that protect flavour without artificial preservatives.</p>

<h2>Why choose The Pickle Affair for {kw}?</h2>
<ul>
  <li>Handmade under hygienic, FSSAI-certified conditions</li>
  <li>Traditional Kathiawadi / Baa nu Athanu recipes</li>
  <li>No synthetic colours or artificial preservatives</li>
  <li>Food-grade glass packaging for freshness</li>
  <li>Ships across India from Virar, Maharashtra</li>
</ul>

<div class="dp-product-card" style="background:#F5F7F0;border:1px solid #DDE5C8;border-radius:16px;padding:24px;margin:32px 0;text-align:center;">
  <img src="{p['image']}" alt="{p['title']} - The Pickle Affair" style="max-width:240px;width:100%;height:auto;border-radius:12px;margin-bottom:16px;">
  <h3 style="color:#4A6B29;margin:8px 0 12px;font-size:20px;">{p['title']}</h3>
  <p style="color:#1D2614;font-size:14px;margin-bottom:16px;">Authentic {kw} — handmade Kathiawadi pickle ready to ship across India.</p>
  <a href="{product_url}" style="background:#4A6B29;color:#fff;padding:12px 28px;border-radius:999px;font-weight:700;text-decoration:none;display:inline-block;">Shop {p['title']} →</a>
  <p style="margin-top:14px;font-size:13px;"><a href="{collection_url}" style="color:#4A6B29;">Browse all pickles & collections</a></p>
</div>

<h2>{p['angle'].title()}</h2>
<p>When families ask about {kw}, the answer always returns to patience and process: quality mangoes or seasonal produce, carefully balanced spices, and oil that seals flavour for months. At The Pickle Affair, every jar is prepared so the first spoon tastes like home.</p>

<h3>How to enjoy it daily</h3>
<p>Serve a spoon with roti, thepla, khichdi, dal-bhaat, or rice. For gifting, pair {p['title']} with other jars from our <a href="{collection_url}">all products collection</a>.</p>

<h2>Frequently asked questions</h2>
{faq_html}

<p><em>Published {day.isoformat()} · Tag: {p['tag']} · Focus keyword: {kw}</em></p>
""".strip()

    return title, excerpt, body


def existing_titles() -> set[str]:
    titles: set[str] = set()
    page_info = None
    # REST list
    data = api("GET", f"/blogs/{BLOG_ID}/articles.json?limit=250&fields=id,title,published_at")
    for art in data.get("articles", []):
        titles.add(art.get("title", "").strip().lower())
    return titles


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
    now = ist_now()
    day = now.date()
    count = int(os.environ.get("DAILY_BLOG_COUNT", "5"))
    publish = os.environ.get("PUBLISH_IMMEDIATELY", "1") == "1"

    print(f"=== The Pickle Affair daily blogs · {day.isoformat()} IST {now.strftime('%H:%M')} ===")
    titles = existing_titles()
    targets = pick_targets(day, count)
    slots = ["09:00:00+05:30", "11:00:00+05:30", "14:00:00+05:30", "17:00:00+05:30", "19:30:00+05:30"]

    created = 0
    for i, p in enumerate(targets):
        title, excerpt, body = build_html(p, day)
        if title.strip().lower() in titles:
            # uniqueness bump
            title = f"{title} ({day.strftime('%d %b')})"
            if title.strip().lower() in titles:
                print(f"skip duplicate: {title}")
                continue
        slot_time = slots[i % len(slots)]
        published_at = f"{day.isoformat()}T{slot_time}"
        # Avoid Shopify error: cannot publish with a future publish_at
        slot_dt = dt.datetime.fromisoformat(published_at)
        if slot_dt > now:
            published_at = now.isoformat()
        print(f"→ Creating: {title}")
        result = create_article(
            title=title,
            excerpt=excerpt,
            body=body,
            tags=f"{p['tag']}, {p['focus_keyword']}",
            image=p["image"],
            published_at=published_at,
        )
        art = result.get("article", {})
        print(f"   id={art.get('id')} handle={art.get('handle')} published_at={art.get('published_at')}")
        created += 1

    print(f"Done. Created {created}/{count} articles.")


if __name__ == "__main__":
    main()
