#!/usr/bin/env python3
"""
Create/update SEO collections from scratch/collection_library.json.

Competitor architecture (Homepick ~27 hubs, Pasand favourites/gifts) informs
which intents we cover — copy is original. SEO_AUTOPILOT §14 checklist enforced.

Env:
  DRY_RUN=1
  COLLECTION_BATCH=all|queued|live   (default: all)
  COLLECTION_LIMIT=N                 (optional cap for weekly runs)
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scratch"))
from shopify_auth import resolve_access_token, shop_url  # noqa: E402
from keyword_bank import enrich_collection, secondary_phrase  # noqa: E402

LIB = json.loads((ROOT / "scratch" / "collection_library.json").read_text())
PRODUCT_KEYS: dict[str, str] = LIB["product_keys"]
SHOP_URL = shop_url()
API = "2024-10"
CTX = ssl.create_default_context()
TOKEN = ""
DRY_RUN = os.environ.get("DRY_RUN", "").strip() in ("1", "true", "yes")
BATCH = os.environ.get("COLLECTION_BATCH", "all").strip().lower()
LIMIT = int(os.environ.get("COLLECTION_LIMIT", "0") or "0")
# Collection body floor (useful words). Google has no official minimum;
# 2025 Digitaloft study of #1 UK category pages averaged ~310 words.
# Our policy: 400–600 useful words (floor 400) — helpful buying copy, not stuffing.
MIN_COLLECTION_WORDS = int(os.environ.get("MIN_COLLECTION_WORDS", "400"))


def word_count(html: str) -> int:
    import re

    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split()) if text else 0


FLAVOUR_NOTES: dict[str, str] = {
    "mango": "Classic homemade mango / aam ka achar character — spice-forward keri pieces meant for everyday roti and dal plates.",
    "gor": "Jaggery-led Gor Keri leans sweet-savoury; pairs well when the thali is already salty or spicy.",
    "meethi": "Meethi Keri is the sweet mango achar lane — soft sweetness with traditional keri pieces for thepla and festive thalis.",
    "gunda": "Gunda / lasode achar is a specialty texture jar — choose it when you want a distinct Kathiawadi accent, not a basic mango pickle.",
    "chana": "Chana Keri Methi (methia keri) brings fenugreek depth; ideal when you want a savoury-bitter edge with mango.",
    "chhundo": "Chhundo is sweet shredded mango — different cut and sweetness profile from chunk-style Meethi Keri.",
    "katka": "Katka Keri sits in the traditional homemade mango achar lane for daily roti and khichdi plates.",
}


def intent_angle(spec: dict) -> tuple[str, str, str]:
    """Return (who_for, flavour_lane, choose_tip) unique to the collection intent."""
    kw = spec["primary_keyword"]
    keys = spec.get("products") or []
    handle = spec["handle"]

    who = (
        f"This hub is for shoppers comparing jars under the intent “{kw}” — "
        "people who want handmade Kathiawadi / Gujarati achar with clear labels, "
        "not a random mixed dump of every pickle on the site."
    )
    if "sweet" in kw or handle.startswith("meethi") or handle.startswith("chhundo") or handle.startswith("gor") or "sweet" in handle:
        lane = (
            "Flavour lane: sweet and sweet-tangy mango styles. Expect jaggery or natural sweetness "
            "that balances salty or spicy meals rather than competing with them."
        )
        tip = "If your plate is already chilli-forward, start sweet; if you want heat, jump to spicy / traditional keri hubs instead."
    elif "gunda" in kw or "gunda" in keys or "lasode" in kw:
        lane = (
            "Flavour lane: specialty gunda / lasode achar — texture and spice logic differ from everyday mango pickle."
        )
        tip = "Buy gunda when you specifically want that jar; do not treat it as a substitute for Meethi Keri or plain aam ka achar."
    elif "methi" in kw or "chana" in keys or "methia" in kw:
        lane = (
            "Flavour lane: methi-forward mango achar. Fenugreek adds aroma and a controlled bitter edge when the kitchen balances it well."
        )
        tip = "Choose methia keri when you like that depth with thepla; pick sweeter hubs if bitterness is not your preference."
    elif "thepla" in kw or "tiffin" in handle:
        lane = "Use case lane: jars that travel well beside thepla and tiffin plates — companions, not the whole meal."
        tip = "Pack a small portion, keep a dry spoon, and match sweet vs spicy to the day’s roti stuffing."
    elif "khichdi" in kw:
        lane = "Use case lane: brighter or spicier contrast for mild khichdi and dal-rice bowls."
        tip = "Start with one contrasting jar; sweet styles also work when the khichdi is already peppery."
    elif "gift" in kw or "gift" in handle:
        lane = "Gifting lane: curated jars for festive or family hampers — still real products, not empty gift SEO pages."
        tip = "Prefer a small set of distinct flavours over five near-identical sweet jars."
    elif "fssai" in kw or "handmade" in handle or "homemade" in kw:
        lane = (
            "Trust lane: handmade preparation context with FSSAI kitchen hygiene signals and transparent product pages."
        )
        tip = "Read ingredients you recognise, then confirm size and storage on each product page."
    elif "buy" in kw or "online" in kw:
        lane = (
            "Buying lane: help you compare styles online before you commit — intent first, then jar size."
        )
        tip = "Use collection hubs to shortlist, then open one product page for price, size, and ingredients."
    else:
        lane = (
            "Regional / traditional lane: Kathiawadi and Gujarati achar styles for everyday thalis, "
            "built around real jars we stock — not doorway keyword pages."
        )
        tip = "Match the meal first, then sweet vs spicy vs specialty, then confirm the product page."

    return who, lane, tip


def rich_body(spec: dict, all_handles: list[str]) -> str:
    """SEO_AUTOPILOT §14 + 400–600 useful words (floor MIN_COLLECTION_WORDS)."""
    spec = enrich_collection(spec)
    kw = spec["primary_keyword"]
    title = spec["title"]
    keys = spec.get("products") or []
    names = product_titles(keys)
    name_list = ", ".join(names[:-1]) + (f" and {names[-1]}" if len(names) > 1 else names[0] if names else "our jars")
    related = related_collection_links(spec["handle"], all_handles)
    who, lane, tip = intent_angle(spec)
    related_terms = secondary_phrase(spec, "secondary_keywords", limit=10)
    blog_links = [
        ("/blogs/kitchen-tales/how-to-buy-authentic-gujarati-pickle-online-without-guesswork", "How to buy Gujarati pickle online"),
        ("/blogs/kitchen-tales/how-to-store-indian-pickles-keep-gujarati-achar-fresh-for-months", "How to store Indian pickles"),
        ("/blogs/kitchen-tales/how-baa-s-kitchen-makes-traditional-gujarati-pickles", "Baa’s Kitchen tradition"),
        ("/blogs/kitchen-tales/how-long-does-mango-pickle-last-shelf-life-freshness-signs", "Mango pickle shelf life"),
        ("/blogs/kitchen-tales", "Kitchen Tales blog"),
    ]
    product_notes = "".join(
        f"<li><strong>{n}</strong> — {FLAVOUR_NOTES.get(k, 'See the product page for flavour profile, ingredients, and jar sizes.')} "
        f'<a href="/products/{PRODUCT_KEYS[k]}">Shop {n} →</a></li>'
        for k, n in zip(keys, names)
    )
    faqs = [
        (
            f"What is this {title} collection for?",
            f"It groups jars that match the shopping intent around “{kw}” so you can compare styles, read buying notes, and open the right product page — instead of scrolling an unfiltered catalogue.",
        ),
        (
            "How do I choose the right jar?",
            f"{tip} Then check ingredients you recognise, jar size, and storage notes on the product page before adding to cart.",
        ),
        (
            "Are these handmade?",
            "Yes. The Pickle Affair prepares pickles in a Kathiawadi kitchen style with hygienic FSSAI-certified preparation context. We do not use synthetic colours, and we do not invent medical claims or proprietary recipe quantities for SEO.",
        ),
        (
            "Do you ship across India?",
            "Yes — handmade jars ship across India from our Virar, Maharashtra kitchen context. Delivery timing depends on your pincode; confirm size options on each product page.",
        ),
        (
            "How should I store achar after opening?",
            "Keep the jar cool and dry, lid sealed, and always use a clean dry spoon. Follow the label’s best-before guidance. For deeper storage habits, read our Kitchen Tales storage guide linked below.",
        ),
        (
            f"Is “{kw}” the same as every mango pickle?",
            f"No. “{kw}” points to a specific shopping intent on this page. Sweet, spicy, methi-forward, shredded chhundo, and specialty gunda jars are different lanes — use related collections if you need another style.",
        ),
    ]
    faq_html = "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in faqs)
    rel_c = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in related)
    rel_b = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in blog_links)
    compare_rows = "".join(
        f"<tr><td>{n}</td><td>{FLAVOUR_NOTES.get(k, 'See product page for flavour profile and sizes')}</td>"
        f"<td><a href=\"/products/{PRODUCT_KEYS[k]}\">Shop →</a></td></tr>"
        for k, n in zip(keys, names)
    )

    body = f"""
<p class="dp-lead">Looking for <strong>{kw}</strong>? The <strong>{title}</strong> collection from The Pickle Affair gathers {name_list} — handmade Kathiawadi / Gujarati achar meant for everyday meals, not factory-flat flavour. Use this page to understand the flavour lane, compare jars, read buying guidance, and jump to the product that fits your thali. We ship handmade jars across India and keep product pages transparent about ingredients and sizes.</p>

<h2>What this category covers</h2>
<p>{who}</p>
<p>{lane}</p>
<p>Unlike a generic “all products” dump, this hub is built around one shopping intent: <em>{kw}</em>. Competitor catalogues often split pickle shops into taste, ingredient, regional, and gifting silos; we only publish hubs we can fill with real jars and useful guidance — no doorway pages and no copied competitor wording.</p>
<p>Shoppers also search related phrases such as <em>{related_terms or kw}</em>. We cover those naturally here and in Kitchen Tales — never as thin duplicate URLs.</p>
<p>Every jar here follows traditional spice logic, glass packaging suited to home storage, and clear product pages. We refuse fake awards, invented medical claims, and proprietary recipe quantities written only for search engines.</p>

<h2>Products in this collection</h2>
<ul class="dp-seo-product-list">{product_notes}</ul>

<h2>How to choose (buying guidance)</h2>
<p>{tip}</p>
<ol class="dp-seo-steps">
  <li>Start with the meal: thepla/tiffin, khichdi/dal-rice, or festive thali.</li>
  <li>Pick the flavour lane: sweet, spicy/traditional keri, methi-forward, shredded chhundo, or specialty gunda.</li>
  <li>Read ingredients you recognise on the product page — oil, spices, and sweetness source should make kitchen sense.</li>
  <li>Check storage notes — dry spoon and sealed jar matter after opening.</li>
  <li>Start with one jar before gifting a full set, especially if you are new to Kathiawadi achar styles.</li>
</ol>

<h2>Quick comparison</h2>
<table>
  <thead><tr><th>Jar</th><th>Notes</th><th>Shop</th></tr></thead>
  <tbody>{compare_rows}</tbody>
</table>

<h2>Serving ideas</h2>
<ul class="dp-seo-idea-list">
  <li>Spoon on the side of roti, rotla, or thepla — pickle is a companion, not the whole plate.</li>
  <li>Khichdi and dal-rice often want brighter or spicier contrast; sweet styles shine when the plate is already salty.</li>
  <li>Travel tiffins: pack a small dabba, keep spoons dry, and reseal the jar promptly.</li>
  <li>Festive thalis: offer one sweet and one traditional/spicy jar so guests can choose.</li>
</ul>

<h2>Why The Pickle Affair</h2>
<ul class="dp-seo-perk-list">
  <li>Kathiawadi / Gujarati kitchen sensibility (Baa’s Kitchen)</li>
  <li>FSSAI-certified kitchen context for hygienic preparation</li>
  <li>No synthetic colours</li>
  <li>Clear product pages plus Kitchen Tales guides for deeper education</li>
  <li>Ships across India from Virar, Maharashtra</li>
</ul>

<h2>Frequently asked questions</h2>
{faq_html}

<h2>Related collections</h2>
<ul class="dp-seo-chip-list">{rel_c}</ul>

<h2>Related Kitchen Tales guides</h2>
<ul class="dp-seo-chip-list">{rel_b}</ul>

<p><em>Collection SEO: unique intro · buying guidance · comparison · serving · FAQ · internal links · one primary keyword ({kw}). Target {MIN_COLLECTION_WORDS}+ useful words. Ships across India from Virar, Maharashtra.</em></p>
""".strip()

    # Soft expansion if under floor (useful blocks, not keyword spam)
    guard = 0
    while word_count(body) < MIN_COLLECTION_WORDS and guard < 2:
        guard += 1
        body = body.replace(
            "<h2>Related collections</h2>",
            f"""<h2>What “{kw}” shoppers usually decide next</h2>
<p>After shortlisting on this page, open the product card for price and jar size, then skim one Kitchen Tales guide if you still need storage or pairing context. If the flavour lane is wrong, use a related collection instead of forcing a mismatched jar into the cart. That keeps one primary intent per URL and avoids thin doorway pages.</p>
<p>We measure usefulness by whether a first-time online pickle buyer can answer: which meal, which sweetness/heat lane, which jar, and how to store it — not by stuffing the same sentence with every synonym for {kw}.</p>

<h2>Related collections</h2>""",
            1,
        )

    wc = word_count(body)
    print(f"  body words≈{wc} (floor {MIN_COLLECTION_WORDS}) [{spec['handle']}]")
    return body


def api(method: str, path: str, payload: dict | None = None) -> dict:
    global TOKEN
    if not TOKEN:
        TOKEN = resolve_access_token()
    data = None if payload is None else json.dumps(payload).encode()
    last_err = ""
    for attempt in range(8):
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
                time.sleep(0.55)
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            last_err = f"{e.code} {err}"
            if e.code == 429 or e.code >= 500:
                wait = 1.5 * (attempt + 1)
                print(f"  retry {attempt + 1} after {wait:.1f}s ({e.code})")
                time.sleep(wait)
                continue
            raise SystemExit(f"API {method} {path} failed: {last_err}") from e
    raise SystemExit(f"API {method} {path} failed after retries: {last_err}")


def map_product_ids() -> dict[str, int]:
    data = api("GET", "/products.json?limit=250&fields=id,handle,title")
    by_handle = {p["handle"]: p for p in data.get("products", [])}
    out: dict[str, int] = {}
    for key, handle in PRODUCT_KEYS.items():
        if handle not in by_handle:
            raise SystemExit(f"Missing product handle: {handle}")
        out[key] = by_handle[handle]["id"]
    return out


def product_titles(keys: list[str]) -> list[str]:
    titles = {
        "mango": "Homemade Mango Pickle (Aam ka Achar)",
        "gor": "Gor Keri (Jaggery Mango Achar)",
        "meethi": "Meethi Keri (Sweet Mango Achar)",
        "gunda": "Gunda Keri (Lasode ka Achar)",
        "chana": "Chana Keri Methi (Methia Keri)",
        "chhundo": "Chhundo (Sweet Shredded Mango)",
        "katka": "Katka Keri Pickle",
    }
    return [titles[k] for k in keys if k in titles]


def related_collection_links(current: str, all_handles: list[str]) -> list[tuple[str, str]]:
    titles = {c["handle"]: c["title"] for c in LIB["collections"]}
    picks = [h for h in all_handles if h != current][:5]
    return [(f"/collections/{h}", titles.get(h, h)) for h in picks]


def list_custom_by_handle() -> dict[str, dict]:
    data = api("GET", "/custom_collections.json?limit=250")
    rows = data.get("custom_collections") or data.get("collections") or []
    return {c["handle"]: c for c in rows}


def set_seo_metafields(collection_id: int, seo_title: str, seo_desc: str) -> None:
    for key, value in (
        ("title_tag", seo_title[:70]),
        ("description_tag", seo_desc[:320]),
    ):
        payload = {
            "metafield": {
                "namespace": "global",
                "key": key,
                "value": value,
                "type": "single_line_text_field",
            }
        }
        try:
            api("POST", f"/collections/{collection_id}/metafields.json", payload)
        except SystemExit as e:
            print(f"  SEO metafield note ({key}): {e}")


def sync_collects(collection_id: int, product_ids: list[int]) -> None:
    existing = api("GET", f"/collects.json?collection_id={collection_id}&limit=250").get("collects", [])
    have = {c["product_id"]: c["id"] for c in existing}
    want = set(product_ids)
    for pid in product_ids:
        if pid in have:
            continue
        if DRY_RUN:
            print(f"  DRY collect {pid}")
            continue
        api("POST", "/collects.json", {"collect": {"collection_id": collection_id, "product_id": pid}})
        print(f"  + product {pid}")
    for pid, collect_id in list(have.items()):
        if pid in want:
            continue
        if DRY_RUN:
            print(f"  DRY remove {pid}")
            continue
        api("DELETE", f"/collects/{collect_id}.json")
        print(f"  - removed {pid}")


def select_specs() -> list[dict]:
    specs = list(LIB["collections"])
    if BATCH == "queued":
        specs = [s for s in specs if s.get("status") == "queued"]
    elif BATCH == "live":
        specs = [s for s in specs if s.get("status") == "live"]
    # priority then handle
    specs.sort(key=lambda s: (int(s.get("priority", 99)), s["handle"]))
    if LIMIT > 0:
        specs = specs[:LIMIT]
    return specs


def upsert(spec: dict, product_ids_map: dict[str, int], existing: dict[str, dict], all_handles: list[str]) -> None:
    product_ids = [product_ids_map[k] for k in spec["products"]]
    body = rich_body(spec, all_handles)
    payload = {
        "custom_collection": {
            "title": spec["title"],
            "handle": spec["handle"],
            "body_html": body,
            "published": True,
            "sort_order": "manual",
            "metafields_global_title_tag": spec["seo_title"][:70],
            "metafields_global_description_tag": spec["seo_desc"][:320],
        }
    }
    handle = spec["handle"]
    if handle in existing:
        cid = existing[handle]["id"]
        payload["custom_collection"]["id"] = cid
        if DRY_RUN:
            print(f"DRY update {handle}")
            return
        api("PUT", f"/custom_collections/{cid}.json", payload)
        print(f"UPDATED /collections/{handle}")
        sync_collects(cid, product_ids)
        set_seo_metafields(cid, spec["seo_title"], spec["seo_desc"])
        return
    if DRY_RUN:
        print(f"DRY create {handle}")
        return
    created = api("POST", "/custom_collections.json", payload).get("custom_collection", {})
    cid = created.get("id")
    print(f"CREATED /collections/{handle} id={cid}")
    if cid:
        sync_collects(cid, product_ids)
        set_seo_metafields(cid, spec["seo_title"], spec["seo_desc"])


def mark_library_live(handles: list[str]) -> None:
    changed = False
    for c in LIB["collections"]:
        if c["handle"] in handles and c.get("status") != "live":
            c["status"] = "live"
            changed = True
    if changed and not DRY_RUN:
        (ROOT / "scratch" / "collection_library.json").write_text(json.dumps(LIB, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    print("=== SEO collections (competitor-informed library) ===")
    print(f"batch={BATCH} limit={LIMIT or 'none'} dry={DRY_RUN}")
    product_ids = map_product_ids()
    existing = list_custom_by_handle()
    specs = select_specs()
    all_handles = [c["handle"] for c in LIB["collections"]]
    print(f"Existing: {sorted(existing)}")
    print(f"Will process {len(specs)} collection(s)")
    done: list[str] = []
    for spec in specs:
        upsert(spec, product_ids, existing, all_handles)
        done.append(spec["handle"])
        # refresh existing map after creates
        if spec["handle"] not in existing and not DRY_RUN:
            existing = list_custom_by_handle()
    mark_library_live(done)
    print("Done.")
    for h in done:
        print(f"  https://thepickleaffair.com/collections/{h}")


if __name__ == "__main__":
    main()
