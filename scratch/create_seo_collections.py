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

LIB = json.loads((ROOT / "scratch" / "collection_library.json").read_text())
PRODUCT_KEYS: dict[str, str] = LIB["product_keys"]
SHOP_URL = shop_url()
API = "2024-10"
CTX = ssl.create_default_context()
TOKEN = ""
DRY_RUN = os.environ.get("DRY_RUN", "").strip() in ("1", "true", "yes")
BATCH = os.environ.get("COLLECTION_BATCH", "all").strip().lower()
LIMIT = int(os.environ.get("COLLECTION_LIMIT", "0") or "0")


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


def rich_body(spec: dict, all_handles: list[str]) -> str:
    """SEO_AUTOPILOT §14: intro, category, buying, comparison, serving, FAQ, related."""
    kw = spec["primary_keyword"]
    title = spec["title"]
    names = product_titles(spec["products"])
    name_list = ", ".join(names[:-1]) + (f" and {names[-1]}" if len(names) > 1 else names[0] if names else "our jars")
    related = related_collection_links(spec["handle"], all_handles)
    blog_links = [
        ("/blogs/kitchen-tales/how-to-buy-authentic-gujarati-pickle-online-without-guesswork", "How to buy Gujarati pickle online"),
        ("/blogs/kitchen-tales/how-to-store-indian-pickles-keep-gujarati-achar-fresh-for-months", "How to store Indian pickles"),
        ("/blogs/kitchen-tales/how-baa-s-kitchen-makes-traditional-gujarati-pickles", "Baa’s Kitchen tradition"),
        ("/blogs/kitchen-tales", "Kitchen Tales blog"),
    ]
    faqs = [
        (f"What is this {title} collection for?", f"It groups jars that match the search intent around “{kw}” so you can compare styles before buying."),
        ("How do I choose the right jar?", "Match the meal first (thepla, khichdi, dal-rice), then sweet vs spicy vs specialty — use the comparison notes below."),
        ("Are these handmade?", "Yes. The Pickle Affair prepares pickles in a Kathiawadi kitchen style with hygienic FSSAI-certified preparation context and no synthetic colours."),
        ("Do you ship across India?", "Yes — handmade jars ship across India. Check each product page for size options."),
        ("How should I store achar after opening?", "Cool, dry place; sealed jar; clean dry spoon every time. Follow the label’s best-before guidance."),
    ]
    faq_html = "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in faqs)
    rel_c = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in related)
    rel_b = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in blog_links)
    compare_rows = "".join(
        f"<tr><td>{n}</td><td>See product page for flavour profile and sizes</td><td><a href=\"/products/{PRODUCT_KEYS[k]}\">View jar</a></td></tr>"
        for k, n in zip(spec["products"], names)
    )
    return f"""
<p class="dp-lead">Looking for <strong>{kw}</strong>? The <strong>{title}</strong> collection from The Pickle Affair gathers {name_list} — handmade Kathiawadi / Gujarati achar meant for everyday meals, not factory-flat flavour. Use this page to compare styles, read buying guidance, and jump to the jar that fits your thali.</p>

<h2>What this category covers</h2>
<p>Unlike a generic “all products” dump, this hub is built around one shopping intent: <em>{kw}</em>. Competitors often split pickle catalogues into taste, ingredient, regional and gifting silos; we only publish silos we can fill with real jars and useful guidance — no doorway pages.</p>
<p>Every jar here follows traditional spice logic, glass packaging suited to home storage, and transparent product pages. We do not invent medical claims, fake awards, or proprietary recipe quantities for SEO.</p>

<h2>Products in this collection</h2>
<ul>{''.join(f'<li><strong>{n}</strong></li>' for n in names)}</ul>

<h2>How to choose (buying guidance)</h2>
<ol>
  <li>Start with the meal: thepla/tiffin, khichdi/dal, or festive thali.</li>
  <li>Pick the flavour lane: sweet, spicy/traditional keri, methi-forward, or specialty gunda.</li>
  <li>Read ingredients you recognise on the product page.</li>
  <li>Check storage notes — dry spoon and sealed jar matter after opening.</li>
  <li>Start with one jar before gifting a full set.</li>
</ol>

<h2>Quick comparison</h2>
<table>
  <thead><tr><th>Jar</th><th>Notes</th><th>Shop</th></tr></thead>
  <tbody>{compare_rows}</tbody>
</table>

<h2>Serving ideas</h2>
<ul>
  <li>Spoon on the side of roti, rotla, or thepla — pickle is a companion, not the whole plate.</li>
  <li>Khichdi and dal-rice often want brighter or spicier contrast.</li>
  <li>Sweet styles (Meethi Keri, Gor Keri, Chhundo) shine when the plate is already salty or spicy.</li>
  <li>Travel tiffins: pack a small dabba and keep spoons dry.</li>
</ul>

<h2>Why The Pickle Affair</h2>
<ul>
  <li>Kathiawadi / Gujarati kitchen sensibility (Baa’s Kitchen)</li>
  <li>FSSAI-certified kitchen context</li>
  <li>No synthetic colours</li>
  <li>Clear product pages and Kitchen Tales guides for deeper education</li>
</ul>

<h2>Frequently asked questions</h2>
{faq_html}

<h2>Related collections</h2>
<ul>{rel_c}</ul>

<h2>Related Kitchen Tales guides</h2>
<ul>{rel_b}</ul>

<p><em>Collection SEO checklist: unique intro · buying guidance · comparison · serving · FAQ · internal links · one primary keyword ({kw}). Policy: no keyword stuffing, no competitor copy.</em></p>
""".strip()


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
