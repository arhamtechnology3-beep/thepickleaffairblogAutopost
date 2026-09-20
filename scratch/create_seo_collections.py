#!/usr/bin/env python3
"""
Create SEO collection pages from COLLECTIONS_SEO_PLAN.md.

- Custom collections (manual product membership — NOT Status=Active)
- Unique body_html + SEO title/meta (global title_tag / description_tag)
- Idempotent: update if handle already exists
- Requires app scopes: read_products, write_products (+ existing content scopes)

Usage:
  python3 scratch/create_seo_collections.py
  DRY_RUN=1 python3 scratch/create_seo_collections.py
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

SHOP_URL = shop_url()
API = "2024-10"
CTX = ssl.create_default_context()
TOKEN = ""
DRY_RUN = os.environ.get("DRY_RUN", "").strip() in ("1", "true", "yes")

# Product handles → resolved to IDs at runtime
PRODUCT_HANDLES = {
    "mango": "mango-pickle-traditional-keri-achar-gujarati",
    "gor": "gor-keri-pickle-jaggery-mango-achar-gujarati",
    "meethi": "sweet-mango-pickle-meethi-keri-achar-homemade",
    "gunda": "gunda-keri-pickle-lasode-ka-achar-gujarati",
    "chana": "chana-keri-methi-pickle-gujarati-methia-achar",
    "chhundo": "chhundo-pickle-sweet-shredded-mango-achar-gujarati",
    "katka": "katka-keri-pickle-homemade-gujarati-mango-achar",
}

ALL = ["mango", "gor", "meethi", "gunda", "chana", "chhundo", "katka"]


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
                time.sleep(0.55)  # stay under ~2 calls/sec
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


def related_block(links: list[tuple[str, str]]) -> str:
    items = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in links)
    return f"<h2>Related collections &amp; guides</h2><ul>{items}</ul>"


def faq_html(faqs: list[tuple[str, str]]) -> str:
    return "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in faqs)


def collection_body(
    intro: str,
    how_to_choose: str,
    serving: str,
    faqs: list[tuple[str, str]],
    related: list[tuple[str, str]],
) -> str:
    return f"""
<p class="dp-lead">{intro}</p>
<h2>How to choose from this collection</h2>
{how_to_choose}
<h2>Serving ideas</h2>
{serving}
<h2>Frequently asked questions</h2>
{faq_html(faqs)}
{related_block(related)}
<p><em>Policy: COLLECTIONS_SEO_PLAN.md + BLOG.md — one intent per URL, no doorway pages.</em></p>
""".strip()


COLLECTIONS = [
    {
        "title": "All Mango Pickles",
        "handle": "all-mango-pickles",
        "seo_title": "Mango Pickle Online | Homemade Aam Ka Achar & Keri Varieties",
        "seo_desc": (
            "Browse authentic mango pickle (aam ka achar) styles — spicy keri, methi, katka, "
            "sweet and shredded chhundo. FSSAI kitchen · The Pickle Affair · India shipping."
        ),
        "products": ALL,
        "body": collection_body(
            intro=(
                "Looking for <strong>mango pickle online</strong>? This collection gathers every "
                "keri / aam ka achar style from The Pickle Affair — spicy homemade mango pickle, "
                "Katka Keri, Chana Keri Methi, sweet Meethi Keri and Gor Keri, Chhundo, and specialty "
                "Gunda Keri. Each jar follows a Kathiawadi kitchen approach for everyday Gujarati meals."
            ),
            how_to_choose=(
                "<ul>"
                "<li><strong>Everyday spicy keri</strong> — Homemade Mango Pickle or Katka Keri</li>"
                "<li><strong>Methi-forward</strong> — Chana Keri Methi</li>"
                "<li><strong>Sweet</strong> — Meethi Keri, Gor Keri, or shredded Chhundo</li>"
                "<li><strong>Specialty</strong> — Gunda Keri (Lasode ka Achar)</li>"
                "</ul>"
            ),
            serving="<p>Serve a spoon with roti, thepla, khichdi, or dal-rice. Pickle is a companion — keep the plate the hero.</p>",
            faqs=[
                ("What is aam ka achar?", "Aam ka achar is mango pickle. In Gujarati kitchens it is often called keri achar — styles range from spicy to sweet."),
                ("Do you ship across India?", "Yes. The Pickle Affair ships handmade jars across India from our kitchen context."),
            ],
            related=[
                ("/collections/sweet-gujarati-pickles", "Sweet Gujarati Pickles"),
                ("/collections/spicy-traditional-keri-achar", "Spicy & Traditional Keri Achar"),
                ("/blogs/kitchen-tales/gujarati-keri-achar-guide-the-pickle-affair-20-sep", "Gujarati Keri Achar guide"),
            ],
        ),
    },
    {
        "title": "Sweet Gujarati Pickles",
        "handle": "sweet-gujarati-pickles",
        "seo_title": "Sweet Mango Pickle Online | Meethi Keri, Gor Keri & Chhundo",
        "seo_desc": (
            "Shop sweet Gujarati mango pickles — Meethi Keri, Gor Keri (jaggery) and Chhundo. "
            "Handmade Kathiawadi jars from The Pickle Affair. Ships across India."
        ),
        "products": ["meethi", "gor", "chhundo"],
        "body": collection_body(
            intro=(
                "Looking for <strong>sweet Gujarati mango pickle</strong>? This collection brings together "
                "Meethi Keri, Gor Keri (jaggery-sweet) and Chhundo (shredded sweet mango achar) — the jars "
                "Gujarati homes reach for with thepla, roti and festive thalis. Each pickle is prepared in "
                "The Pickle Affair’s Kathiawadi kitchen style for everyday meals, not factory-flat flavour."
            ),
            how_to_choose=(
                "<ul>"
                "<li><strong>Meethi Keri</strong> — classic sweet keri pieces</li>"
                "<li><strong>Gor Keri</strong> — jaggery depth</li>"
                "<li><strong>Chhundo</strong> — shredded relish texture</li>"
                "</ul>"
            ),
            serving="<p>Pair with thepla tiffins, rotla, or dal-bhaat when you want sweet contrast beside savoury breads.</p>",
            faqs=[
                ("Chhundo vs Meethi Keri?", "Chhundo is typically shredded; Meethi Keri centres on sweet keri pieces. Choose by texture."),
                ("Is Gor Keri very sweet?", "Gor Keri leans on jaggery character — read the product page for the jar profile."),
            ],
            related=[
                ("/collections/pickles-for-thepla-tiffin", "Pickles for Thepla & Tiffin"),
                ("/collections/all-mango-pickles", "All Mango Pickles"),
                ("/blogs/kitchen-tales/sweet-mango-pickle-homemade-guide-the-pickle-affair", "Meethi Keri guide"),
                ("/blogs/kitchen-tales/chhundo-traditional-gujarati-sweet-shredded-mango-achar", "Chhundo guide"),
            ],
        ),
    },
    {
        "title": "Spicy & Traditional Keri Achar",
        "handle": "spicy-traditional-keri-achar",
        "seo_title": "Gujarati Keri Achar | Spicy Homemade Mango Pickle",
        "seo_desc": (
            "Traditional spicy Gujarati keri achar — homemade mango pickle, Katka Keri and "
            "Chana Keri Methi. Small-batch Kathiawadi flavour from The Pickle Affair."
        ),
        "products": ["mango", "katka", "chana"],
        "body": collection_body(
            intro=(
                "This collection focuses on <strong>traditional spicy Gujarati keri achar</strong> — "
                "homemade mango pickle, Katka Keri, and methi-forward Chana Keri Methi. Built for "
                "everyday roti and khichdi plates that want heat and tang, not only sweetness."
            ),
            how_to_choose=(
                "<ul>"
                "<li><strong>Homemade Mango Pickle</strong> — classic everyday keri achar</li>"
                "<li><strong>Katka Keri</strong> — homemade katka-style mango achar</li>"
                "<li><strong>Chana Keri Methi</strong> — fenugreek-forward methia keri</li>"
                "</ul>"
            ),
            serving="<p>A spoon beside roti, rotla, or khichdi. For sweet contrast on the same thali, add a jar from Sweet Gujarati Pickles.</p>",
            faqs=[
                ("Is keri achar the same as Meethi Keri?", "No. These jars lean savoury/spicy; Meethi Keri is the sweet style."),
                ("How should I store spicy achar?", "Cool, dry, sealed jar and a clean dry spoon — see our storage guide."),
            ],
            related=[
                ("/collections/methi-fenugreek-pickles", "Methi / Fenugreek Pickles"),
                ("/collections/all-mango-pickles", "All Mango Pickles"),
                ("/blogs/kitchen-tales/katka-keri-pickle-how-to-store-and-serve-at-home-the-pickle-affair", "Katka storage guide"),
                ("/blogs/kitchen-tales/how-to-store-indian-pickles-keep-gujarati-achar-fresh-for-months", "How to store Indian pickles"),
            ],
        ),
    },
    {
        "title": "Gunda Keri & Specialty Achar",
        "handle": "gunda-keri-specialty-achar",
        "seo_title": "Gunda Keri Pickle Online | Lasode Ka Achar",
        "seo_desc": (
            "Buy Gunda Keri (lasode ka achar) — a specialty Gujarati pickle pairing gunda with "
            "keri spices. Handmade jars from The Pickle Affair."
        ),
        "products": ["gunda"],
        "body": collection_body(
            intro=(
                "<strong>Gunda Keri</strong> (Lasode ka Achar) is a specialty Gujarati pickle — "
                "for shoppers who want more than everyday mango-only achar. This collection keeps "
                "that intent focused so it does not compete with broad mango or sweet hubs."
            ),
            how_to_choose="<p>Choose Gunda Keri when you specifically want lasode / gunda character with keri spices.</p>",
            serving="<p>Serve with simple khichdi, roti, or dal-rice so the specialty flavour shows.</p>",
            faqs=[
                ("What is lasode ka achar?", "Another name shoppers use for gunda-based achar — check the product page for this jar’s exact profile."),
                ("Is this the same as mango pickle?", "Related tradition, different produce focus — that is why it has its own collection."),
            ],
            related=[
                ("/collections/buy-gujarati-pickle-online", "Buy Gujarati Pickle Online"),
                ("/collections/kathiawadi-homemade-pickles", "Kathiawadi Homemade Pickles"),
                ("/blogs/kitchen-tales/buy-gunda-keri-online-guide-the-pickle-affair-20-sep", "Buy Gunda Keri guide"),
            ],
        ),
    },
    {
        "title": "Methi / Fenugreek Pickles",
        "handle": "methi-fenugreek-pickles",
        "seo_title": "Methia Keri & Fenugreek Mango Pickle | Chana Keri Methi",
        "seo_desc": (
            "Shop methia / Chana Keri Methi — fenugreek-forward Gujarati mango pickle for "
            "everyday meals. Handmade by The Pickle Affair."
        ),
        "products": ["chana"],
        "body": collection_body(
            intro=(
                "This collection is for <strong>methia keri / fenugreek mango pickle</strong> shoppers. "
                "Chana Keri Methi leads with fenugreek character — culinary flavour education, not medical claims."
            ),
            how_to_choose="<p>Pick Chana Keri Methi when you want methi aroma and a savoury-bitter edge balanced inside Gujarati achar.</p>",
            serving="<p>Excellent with thepla and travel tiffins; also beside simple dal-rice.</p>",
            faqs=[
                ("Why does methi taste bitter?", "Fenugreek naturally carries bitterness; traditional kitchens balance it in the spice mix."),
                ("Do you make health claims about methi?", "No — Kitchen Tales and collections discuss culinary flavour only."),
            ],
            related=[
                ("/collections/spicy-traditional-keri-achar", "Spicy & Traditional Keri Achar"),
                ("/collections/pickles-for-thepla-tiffin", "Pickles for Thepla & Tiffin"),
                ("/blogs/kitchen-tales/fenugreek-methi-in-mango-pickle-flavour-bitterness-chana-keri", "Fenugreek in mango pickle"),
            ],
        ),
    },
    {
        "title": "Kathiawadi Homemade Pickles",
        "handle": "kathiawadi-homemade-pickles",
        "seo_title": "Kathiawadi Homemade Pickles | Traditional Gujarati Achar",
        "seo_desc": (
            "Explore Kathiawadi homemade pickles from The Pickle Affair — keri, chhundo, gunda, "
            "methi and more. Traditional taste, ships across India."
        ),
        "products": ALL,
        "body": collection_body(
            intro=(
                "Explore <strong>Kathiawadi homemade pickles</strong> from The Pickle Affair — the full "
                "range of traditional Gujarati achar styles we bottle for everyday meals. This hub is "
                "about regional kitchen character, not a second “all products” dump with empty SEO rules."
            ),
            how_to_choose=(
                "<p>Start from how you eat: sweet vs spicy, thepla vs khichdi, everyday keri vs specialty gunda. "
                "Then open the matching product card below.</p>"
            ),
            serving="<p>One spoon beside roti, thepla, khichdi, or dal-bhaat — classic Gujarati home habit.</p>",
            faqs=[
                ("What does Kathiawadi mean here?", "It names the regional pickle sensibility behind our jars — traditional spice logic for Gujarati meals."),
                ("Are jars handmade?", "Yes — small-batch Kathiawadi kitchen style with hygienic FSSAI-certified preparation context."),
            ],
            related=[
                ("/collections/buy-gujarati-pickle-online", "Buy Gujarati Pickle Online"),
                ("/collections/all-mango-pickles", "All Mango Pickles"),
                ("/blogs/kitchen-tales/how-baa-s-kitchen-makes-traditional-gujarati-pickles", "Baa’s Kitchen"),
            ],
        ),
    },
    {
        "title": "Pickles for Thepla & Tiffin",
        "handle": "pickles-for-thepla-tiffin",
        "seo_title": "Best Pickle for Thepla & Tiffin | Gujarati Achar Pairings",
        "seo_desc": (
            "Pickles that belong with thepla and tiffin — Chhundo, Meethi Keri, methi and katka "
            "styles from The Pickle Affair."
        ),
        "products": ["chhundo", "meethi", "chana", "katka"],
        "body": collection_body(
            intro=(
                "Looking for the <strong>best pickle for thepla and tiffin</strong>? These jars travel well "
                "beside soft Gujarati breads — sweet Chhundo and Meethi Keri, methi-forward Chana Keri Methi, "
                "and Katka Keri for a sharper spoon."
            ),
            how_to_choose=(
                "<ul>"
                "<li>Sweet tiffin contrast → Chhundo or Meethi Keri</li>"
                "<li>Methi lovers → Chana Keri Methi</li>"
                "<li>Sharper everyday → Katka Keri</li>"
                "</ul>"
            ),
            serving="<p>Pack a small dabba with thepla; keep spoons dry. Pickle stays on the side of the tiffin, not mixed into soft breads.</p>",
            faqs=[
                ("Can I take these jars while travelling?", "Yes for short trips if sealed and kept cool; always use a dry spoon."),
                ("Sweet or spicy with thepla?", "Both work — many homes keep one sweet and one spicy jar."),
            ],
            related=[
                ("/collections/sweet-gujarati-pickles", "Sweet Gujarati Pickles"),
                ("/collections/methi-fenugreek-pickles", "Methi / Fenugreek Pickles"),
                ("/blogs/kitchen-tales/pickle-with-khichdi-comfort-pairings-from-a-kathiawadi-kitchen", "Pickle with khichdi"),
            ],
        ),
    },
    {
        "title": "Buy Gujarati Pickle Online",
        "handle": "buy-gujarati-pickle-online",
        "seo_title": "Buy Gujarati Pickle Online India | Kathiawadi Homemade Achar",
        "seo_desc": (
            "Buy authentic Gujarati pickle online — chhundo, meethi keri, gunda keri, katka and "
            "aam ka achar. Handmade · pan-India shipping."
        ),
        "products": ALL,
        "body": collection_body(
            intro=(
                "Ready to <strong>buy Gujarati pickle online</strong>? This commercial hub lists every "
                "The Pickle Affair jar with clear style differences — so you match meals first, then "
                "checkout — instead of guessing from a single “all products” grid."
            ),
            how_to_choose=(
                "<ol>"
                "<li>Match style to meals (thepla vs khichdi vs dal-rice).</li>"
                "<li>Read ingredients you recognise on the product page.</li>"
                "<li>Prefer clear storage guidance on the label.</li>"
                "<li>Start with one jar before gifting a full set.</li>"
                "</ol>"
            ),
            serving="<p>After your order arrives: cool dry storage, sealed jar, clean dry spoon.</p>",
            faqs=[
                ("Do you ship pan-India?", "Yes — handmade jars ship across India."),
                ("How do I avoid buying the wrong style?", "Use the style guides in related collections (sweet vs spicy vs specialty) before adding to cart."),
            ],
            related=[
                ("/collections/sweet-gujarati-pickles", "Sweet Gujarati Pickles"),
                ("/collections/spicy-traditional-keri-achar", "Spicy & Traditional Keri Achar"),
                ("/collections/gunda-keri-specialty-achar", "Gunda Keri & Specialty"),
                ("/blogs/kitchen-tales/how-to-buy-authentic-gujarati-pickle-online-without-guesswork", "Buying guide"),
            ],
        ),
    },
]


def map_product_ids() -> dict[str, int]:
    data = api("GET", "/products.json?limit=250&fields=id,handle")
    by_handle = {p["handle"]: p["id"] for p in data.get("products", [])}
    out: dict[str, int] = {}
    for key, handle in PRODUCT_HANDLES.items():
        if handle not in by_handle:
            raise SystemExit(f"Missing product handle on shop: {handle}")
        out[key] = by_handle[handle]
    return out


def list_custom_by_handle() -> dict[str, dict]:
    data = api("GET", "/custom_collections.json?limit=250")
    rows = data.get("custom_collections") or data.get("collections") or []
    return {c["handle"]: c for c in rows}


def set_seo_metafields(collection_id: int, seo_title: str, seo_desc: str) -> None:
    # global.title_tag / description_tag power search engine listing
    for key, value, mtype in (
        ("title_tag", seo_title[:70], "single_line_text_field"),
        ("description_tag", seo_desc[:320], "single_line_text_field"),
    ):
        payload = {
            "metafield": {
                "namespace": "global",
                "key": key,
                "value": value,
                "type": mtype,
                "owner_id": collection_id,
                "owner_resource": "collection",
            }
        }
        # Prefer resource endpoint
        api("POST", f"/collections/{collection_id}/metafields.json", payload)


def sync_collects(collection_id: int, product_ids: list[int]) -> None:
    existing = api("GET", f"/collects.json?collection_id={collection_id}&limit=250").get("collects", [])
    have = {c["product_id"]: c["id"] for c in existing}
    want = set(product_ids)
    for pid in product_ids:
        if pid in have:
            continue
        if DRY_RUN:
            print(f"  DRY collect product {pid}")
            continue
        api("POST", "/collects.json", {"collect": {"collection_id": collection_id, "product_id": pid}})
        print(f"  + product {pid}")
    for pid, collect_id in have.items():
        if pid in want:
            continue
        if DRY_RUN:
            print(f"  DRY remove collect {collect_id}")
            continue
        api("DELETE", f"/collects/{collect_id}.json")
        print(f"  - removed product {pid}")


def upsert_collection(spec: dict, product_ids_map: dict[str, int], existing: dict[str, dict]) -> None:
    product_ids = [product_ids_map[k] for k in spec["products"]]
    payload = {
        "custom_collection": {
            "title": spec["title"],
            "handle": spec["handle"],
            "body_html": spec["body"],
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
            print(f"DRY update collection {handle} id={cid}")
        else:
            api("PUT", f"/custom_collections/{cid}.json", payload)
            print(f"UPDATED /collections/{handle} id={cid}")
        sync_collects(cid, product_ids)
        if not DRY_RUN:
            try:
                set_seo_metafields(cid, spec["seo_title"], spec["seo_desc"])
            except SystemExit as e:
                print(f"  SEO metafield note: {e}")
        return

    if DRY_RUN:
        print(f"DRY create collection {handle} products={product_ids}")
        return
    created = api("POST", "/custom_collections.json", payload).get("custom_collection", {})
    cid = created.get("id")
    print(f"CREATED /collections/{handle} id={cid}")
    if not cid:
        return
    sync_collects(cid, product_ids)
    try:
        set_seo_metafields(cid, spec["seo_title"], spec["seo_desc"])
    except SystemExit as e:
        print(f"  SEO metafield note: {e}")


def main() -> None:
    print("=== Create SEO collections (COLLECTIONS_SEO_PLAN.md) ===")
    if DRY_RUN:
        print("DRY_RUN=1")
    product_ids = map_product_ids()
    print(f"Products resolved: {product_ids}")
    existing = list_custom_by_handle()
    print(f"Existing custom collections: {list(existing)}")
    for spec in COLLECTIONS:
        upsert_collection(spec, product_ids, existing)
    print("Done.")
    print("Live URLs:")
    for spec in COLLECTIONS:
        print(f"  https://thepickleaffair.com/collections/{spec['handle']}")


if __name__ == "__main__":
    main()
