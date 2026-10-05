#!/usr/bin/env python3
"""Validate writer output: schema, handles, unique word count, and built article length."""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/Users/apple/Documents/Shopify Theme VS code/The Pickle Affair/blog-autopost")
sys.path.insert(0, str(ROOT / "scratch"))
import blog_content as bc  # noqa: E402

PRODUCTS = {p["handle"] for p in json.loads((ROOT / "scratch/product_registry.json").read_text())}
COLLECTIONS = {
    c["handle"]
    for c in json.loads((ROOT / "scratch/collection_library.json").read_text())
    if c.get("status") == "live"
} if isinstance(json.loads((ROOT / "scratch/collection_library.json").read_text()), list) else {
    c["handle"]
    for c in json.loads((ROOT / "scratch/collection_library.json").read_text())["collections"]
    if c.get("status") == "live"
}
CATS = {"Heritage Recipes", "Health & Spices", "Buying Guides", "Pickle Pairings", "Artisanal Craft", "Pickle Guides"}
ANGLES = {"storage", "shelf_life", "ingredient", "pairing", "comparison", "baa_story", "buying", "heritage_product"}
REQ = ["id", "primary_keyword", "title", "intent", "cluster", "category", "angle", "keyword_pillar",
       "product_handles", "collection_handles", "excerpt", "quick_answer", "sections", "faqs", "conclusion"]
BANNED = ["cures ", "immunity", "diabet", "pregnan", "₹", "% off", "discount"]


def unique_words(t: dict) -> int:
    txt = [t.get("quick_answer", ""), t.get("conclusion", "")]
    for s in t.get("sections", []):
        txt += [s.get("h2", "")] + list(s.get("p") or []) + list(s.get("list") or [])
    txt += [f"{a} {b}" for a, b in t.get("faqs", [])]
    return len(" ".join(txt).split())


def check(t: dict) -> list[str]:
    errs = [f"missing {k}" for k in REQ if k not in t]
    if errs:
        return errs
    if "draft" in t:
        errs.append("remove draft key")
    if t["category"] not in CATS:
        errs.append(f"bad category {t['category']}")
    if t["angle"] not in ANGLES:
        errs.append(f"bad angle {t['angle']}")
    errs += [f"bad product {h}" for h in t["product_handles"] if h not in PRODUCTS]
    errs += [f"bad collection {h}" for h in t["collection_handles"] if h not in COLLECTIONS]
    if len(t["title"]) > 70:
        errs.append("title > 70 chars")
    if len(t["excerpt"]) > 155:
        errs.append("excerpt > 155 chars")
    if not 9 <= len(t["sections"]) <= 12:
        errs.append(f"{len(t['sections'])} sections (want 9-12)")
    if not 5 <= len(t["faqs"]) <= 8:
        errs.append(f"{len(t['faqs'])} faqs (want 5-8)")
    for s in t["sections"]:
        if "h2" not in s or not (s.get("p") or s.get("list")):
            errs.append(f"section needs h2 + p/list: {s.get('h2')}")
    blob = json.dumps(t, ensure_ascii=False).lower()
    errs += [f"check wording: '{w}'" for w in BANNED if w in blob]
    if re.search(r"\brs\.?\s?\d", blob):
        errs.append("contains a price")
    if any(tag in blob for tag in ("<p", "<br", "<a ", "<li", "<div", "<h")):
        errs.append("contains HTML tags (only <strong> is allowed)")
    uw = unique_words(t)
    if uw < 1150:
        errs.append(f"only {uw} unique words (need >= 1150)")
    return errs


def main() -> None:
    data = json.loads(Path(sys.argv[1]).read_text())
    lib_ids = {t["id"] for t in json.loads((ROOT / "scratch/topic_library.json").read_text())["topics"]}
    seen = set()
    bad = 0
    for t in data:
        errs = check(t)
        if t.get("id") in seen:
            errs.append("duplicate id in file")
        seen.add(t.get("id"))
        built = 0
        if not any(e.startswith("missing") for e in errs):
            _, _, body, _, _ = bc.build_long_article(t)
            built = bc.word_count(body)
            if built < bc.MIN_WORDS:
                errs.append(f"built article {built} < {bc.MIN_WORDS} words")
        status = "OK" if not errs else "FAIL: " + "; ".join(errs)
        new = "" if t.get("id") in lib_ids else " (new id)"
        print(f"{t.get('id')}{new} | unique={unique_words(t)} | built={built} | {status}")
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
