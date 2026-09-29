#!/usr/bin/env python3
"""Long-form Kitchen Tales body builder (BLOG.md §9 + §28 standard guide length)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = {p["handle"]: p for p in json.loads((ROOT / "scratch" / "product_registry.json").read_text())}

MIN_WORDS = int(__import__("os").environ.get("MIN_BLOG_WORDS", "1500"))

try:
    from keyword_bank import enrich_topic  # type: ignore
except Exception:  # pragma: no cover
    def enrich_topic(topic, max_secondary=14):  # noqa: ARG001
        return topic


def word_count(html: str) -> int:
    import re
    visible = re.sub(r"<script[\s\S]*?</script>", " ", html)
    return len(re.sub(r"<[^>]+>", " ", visible).split())


def product_block(handle: str) -> str:
    p = PRODUCTS.get(handle)
    if not p:
        return ""
    return f"""
<div class="dp-product-card" style="background:#F5F7F0;border:1px solid #DDE5C8;border-radius:16px;padding:24px;margin:28px 0;text-align:center;">
  <img src="{p['image']}" alt="{p['title']} from The Pickle Affair" style="max-width:220px;width:100%;height:auto;border-radius:12px;margin-bottom:14px;">
  <h3 style="color:#4A6B29;margin:8px 0 10px;font-size:18px;">{p['title']}</h3>
  <p style="color:#1D2614;font-size:14px;margin-bottom:14px;">Handmade Kathiawadi pickle — ships across India.</p>
  <a href="/products/{p['handle']}" style="background:#4A6B29;color:#fff;padding:11px 24px;border-radius:999px;font-weight:700;text-decoration:none;display:inline-block;">View {p['title']} →</a>
</div>
""".strip()


def collection_cta(handles: list[str]) -> str:
    if not handles:
        return ""
    items = "".join(
        f'<li><a href="/collections/{h}">Explore /collections/{h}</a></li>' for h in handles[:3]
    )
    return f"<h2>Shop related collections</h2><p>These collection hubs match this guide’s intent — use them to compare jars before you buy:</p><ul>{items}</ul>"


def product_cta(handles: list[str]) -> str:
    blocks = [product_block(h) for h in handles[:3] if h in PRODUCTS]
    if not blocks:
        return ""
    return "<h2>Jars to consider from this guide</h2>\n" + "\n".join(blocks)


def angle_depth(angle: str, kw: str) -> str:
    """Substantial unique sections per angle — useful depth, not filler."""
    common_mistakes = f"""
<h2>Common mistakes to avoid</h2>
<ul>
  <li>Using a wet spoon — moisture spoils traditional achar faster than almost anything else.</li>
  <li>Storing jars next to the stove or in direct sun.</li>
  <li>Buying only on price without matching sweet vs spicy vs specialty to your meals.</li>
  <li>Expecting every “mango pickle” to taste the same — keri, methi, katka, chhundo and gunda styles differ.</li>
  <li>Ignoring the printed best-before on the label.</li>
</ul>
<h2>How this connects to The Pickle Affair kitchen</h2>
<p>We write Kitchen Tales from practices we actually follow: Kathiawadi spice logic, hygienic FSSAI-certified preparation context, no synthetic colours, and glass jars suited to home storage. We do not invent awards, medical claims, or proprietary recipe numbers for rankings.</p>
"""
    if angle == "storage":
        return f"""
<h2>Quick answer</h2>
<p>Store Indian pickles in a cool, dry place, always use a clean dry spoon, and keep the jar sealed. Oil-cured Gujarati achar usually keeps well for months when protected from moisture and direct sun.</p>
<h2>Why storage is part of flavour</h2>
<p>Traditional Kathiawadi pickles rely on salt, spices, and oil — not heavy artificial preservatives. That means home habits are part of shelf life. A beautiful jar can still go wrong if water enters on a wet spoon or if heat cooks the oil layer on a sunny sill.</p>
<p>When families ask about <strong>{kw}</strong>, the practical answer is less about a magic month number and more about repeating the same dry, cool, sealed routine every day.</p>
<h2>Step-by-step storage habits</h2>
<ol>
  <li>Close the jar tightly after every use.</li>
  <li>Use only a clean, completely dry spoon — never taste from the jar spoon and return it wet.</li>
  <li>Store away from stove heat and direct sunlight.</li>
  <li>In humid kitchens, choose a cupboard away from the sink and steam.</li>
  <li>Where the style uses oil curing, keep pieces under the oil layer as packed.</li>
  <li>Wipe the rim if needed so the lid seals cleanly.</li>
</ol>
<h2>After opening</h2>
<p>Continue the dry-spoon rule. Check the printed date. Unusual smell, mould, or unexpected fizzing means do not taste — discard. Trust your senses more than a generic “months” claim online.</p>
<h2>Travel and tiffin notes</h2>
<p>For short trips, a small sealed dabba works if spoons stay dry. Do not leave glass jars in a hot car. For longer storage at home, the cupboard routine beats the fridge-or-not debate — follow your jar label when it gives specific guidance.</p>
{common_mistakes}
"""
    if angle == "shelf_life":
        return f"""
<h2>Quick answer</h2>
<p>Unopened, well-made mango pickle typically lasts many months when stored correctly. After opening, quality depends on hygiene and storage — always follow the jar’s best-before guidance and trust your senses.</p>
<h2>What “shelf life” really means for achar</h2>
<p>Shoppers searching <strong>{kw}</strong> often want a single number. Honest kitchens will not invent one. Label dates are authoritative. Online articles that invent “exactly 12 months for every jar” are guessing.</p>
<h2>What shortens or protects freshness</h2>
<ul>
  <li>Moisture from wet spoons</li>
  <li>Heat and sunlight</li>
  <li>Poor seals</li>
  <li>Pickle style differences (oil-cured, sweet, shredded, methi-forward)</li>
  <li>How often the jar is opened in humid weather</li>
</ul>
<h2>Practical freshness checks</h2>
<p>Read the printed date, keep oil coverage consistent where applicable, and stop using the pickle if aroma or appearance changes unexpectedly. If you are unsure, do not taste a suspicious jar.</p>
<h2>Opened vs unopened</h2>
<p>Unopened jars are mostly about cool, dark storage. Opened jars are mostly about spoon hygiene. Families who finish a jar in a few weeks rarely fight shelf-life anxiety; families who leave a jar open for months must be stricter.</p>
{common_mistakes}
"""
    if angle == "ingredient":
        return f"""
<h2>Quick answer</h2>
<p>This guide explains how <strong>{kw}</strong> shapes traditional Gujarati and Kathiawadi pickle flavour — culinary education only, without medical or “superfood” claims.</p>
<h2>Why ingredients matter in achar</h2>
<p>In Baa-style kitchens, spices and oils are chosen for aroma, balance, and how they hold up over months in a jar. Understanding {kw} helps you choose between everyday keri achar, methi-forward jars, sweet styles, and specialty gunda pickles.</p>
<h2>Flavour role (culinary, not medical)</h2>
<p>We discuss taste, aroma, and meal pairing. We do not claim disease treatment, weight loss, or miracle nutrition. If a competitor page over-promises health outcomes, that is not our approach.</p>
<h2>How to taste and compare at home</h2>
<ol>
  <li>Try a small spoon beside plain roti or rice first.</li>
  <li>Notice whether heat, bitterness, sweetness, or aroma leads.</li>
  <li>Decide if your household wants that lead flavour every day or only sometimes.</li>
  <li>Then open the matching collection hub to compare jars in the same lane.</li>
</ol>
<h2>Label reading tips</h2>
<p>Prefer ingredients you recognise. Confirm storage guidance. Check FSSAI context on the brand’s product pages. Start with one jar before bulk buying.</p>
{common_mistakes}
"""
    if angle == "pairing":
        return f"""
<h2>Quick answer</h2>
<p>The best pickle pairing depends on the meal: soft breads like thepla love a punchy or sweet-tangy achar, while khichdi often wants something bright and spicy to cut the comfort.</p>
<h2>How Gujarati homes typically serve pickle</h2>
<p>A spoon on the side is enough. Pickle is a companion, not the whole plate — let dal, rice, or rotla stay the hero. Searching <strong>{kw}</strong> usually means you want that contrast without overpowering the meal.</p>
<h2>Pairing map</h2>
<ul>
  <li><strong>Thepla / travel tiffin</strong> — Chhundo, Meethi Keri, or methi-forward Chana Keri Methi</li>
  <li><strong>Khichdi / dal-rice</strong> — Katka Keri, Gunda Keri, or everyday spicy mango pickle</li>
  <li><strong>Festive thali</strong> — keep one sweet and one spicy jar on the table</li>
  <li><strong>Simple roti nights</strong> — classic homemade mango pickle or Katka Keri</li>
</ul>
<h2>Serving ideas that feel like home</h2>
<ul>
  <li>Train or office tiffin with thepla and a small pickle dabba</li>
  <li>Sunday khichdi with a sharper mango pickle</li>
  <li>Dal-bhaat with sweet pickle for contrast</li>
  <li>Gift a sweet + spicy pair instead of a single random jar</li>
</ul>
<h2>How to choose without overbuying</h2>
<p>Match one primary meal habit first. If your family eats thepla often, start in the thepla collection. If khichdi is weekly, start with sharper jars. Expand only after you finish the first jar.</p>
{common_mistakes}
"""
    if angle == "comparison":
        return f"""
<h2>Quick answer</h2>
<p>Chhundo and Meethi Keri are both sweet mango traditions, but they differ in cut, texture, and how they show up on the plate. Use this guide to choose the jar that matches your meal.</p>
<h2>Chhundo</h2>
<p>Typically associated with shredded mango and a sweet-leaning profile — bright with meals that want a relish-like spoon. Families often reach for it with thepla and festive spreads.</p>
<h2>Meethi Keri</h2>
<p>A sweet mango pickle style centred on keri pieces and a homemade sweet-tang balance familiar in Gujarati homes. Piece texture feels different from shredded chhundo on the tongue.</p>
<h2>Side-by-side choosing</h2>
<ul>
  <li>Want shredded relish texture → Chhundo</li>
  <li>Want classic sweet keri pieces → Meethi Keri</li>
  <li>Want jaggery depth instead → explore Gor Keri</li>
  <li>Want spicy contrast on the same thali → add a keri achar from the spicy collection</li>
</ul>
<p>Exact house recipes stay with the kitchen; this page explains differences at a useful level without inventing proprietary quantities. For shoppers comparing <strong>{kw}</strong>, texture is usually the deciding factor.</p>
<h2>When to buy both</h2>
<p>If you gift or host often, a sweet shredded jar plus a sweet piece-style jar covers more guests than two near-identical spicy jars.</p>
{common_mistakes}
"""
    if angle == "baa_story":
        return f"""
<h2>Quick answer</h2>
<p>The Pickle Affair’s kitchen follows a family Kathiawadi approach: careful produce, traditional spice logic, and small-batch attention — jars meant for everyday Gujarati meals.</p>
<h2>What “Baa’s Kitchen” means here</h2>
<p>It names the traditional cooking sensibility behind the brand. Searching <strong>{kw}</strong> should lead to honest process context — not a fictional biography or inflated heritage claims.</p>
<h2>What we emphasise</h2>
<ul>
  <li>Recognisable regional pickle styles</li>
  <li>Hygienic, FSSAI-certified preparation context</li>
  <li>No synthetic colours</li>
  <li>Glass jars suited to home storage habits</li>
  <li>Clear product pages and educational Kitchen Tales guides</li>
</ul>
<h2>What we refuse to fabricate</h2>
<p>Awards we did not win, medical benefits, invented years of marketing lore, or exact “secret” quantities published only to game search engines.</p>
<h2>How to explore the range</h2>
<p>Start with how you eat, open the matching collection, then pick one jar. Use storage and buying guides so the first online order feels confident.</p>
{common_mistakes}
"""
    if angle == "buying":
        return f"""
<h2>Quick answer</h2>
<p>When you buy Gujarati pickle online, check the style (sweet, spicy, shredded, methi), packaging, FSSAI markings, and whether the maker explains storage clearly — not just the lowest price.</p>
<h2>Why online pickle shopping feels confusing</h2>
<p>Many shops use overlapping names: aam ka achar, keri achar, chhundo, methia, gunda/lasode. Searching <strong>{kw}</strong> should land you on a checklist, then a collection hub, then a product page — not a random single SKU.</p>
<h2>Buying checklist</h2>
<ol>
  <li>Match pickle to meals (thepla vs khichdi vs dal-rice).</li>
  <li>Read ingredients you recognise.</li>
  <li>Prefer clear storage and shelf-life guidance.</li>
  <li>Confirm shipping expectations for glass jars.</li>
  <li>Start with one jar before gifting a full set.</li>
</ol>
<h2>How to use our collections while buying</h2>
<p>Open the sweet hub for Meethi/Gor/Chhundo, the spicy keri hub for everyday heat, specialty for Gunda Keri, and the buy-online hub when you want the full catalogue with commercial intent.</p>
{common_mistakes}
"""
    # pillar / heritage / default
    return f"""
<h2>Quick answer</h2>
<p><strong>{kw.title()}</strong> sits inside a wider Gujarati and Kathiawadi pickle tradition — from everyday keri achar to sweet styles and regional specialties. This guide orients you before you dive into individual jars and collections.</p>
<h2>What belongs in this tradition</h2>
<ul>
  <li>Mango (keri) pickles — spicy, sweet, methi-forward</li>
  <li>Specialty jars such as Gunda Keri and Katka styles</li>
  <li>Relish-like sweet shredded styles such as Chhundo</li>
  <li>Jaggery-leaning sweet styles such as Gor Keri</li>
</ul>
<h2>How to use this guide with our site structure</h2>
<p>Collection pages are shopping hubs. Product pages are jar decisions. Kitchen Tales articles (like this one) explain intent, pairing, storage, and differences so you do not buy blind. Competitors often publish many collection silos; we only publish silos we can fill with real products and useful copy.</p>
<h2>Choosing path</h2>
<ol>
  <li>Identify the meal habit.</li>
  <li>Open the matching collection.</li>
  <li>Compare two jars maximum on the first order.</li>
  <li>Read storage guidance before the jar arrives.</li>
</ol>
{common_mistakes}
"""


SUPPORT_SECTIONS: list[tuple[str, str]] = [
    ("Reading a pickle label before you buy", """
<p>A good achar label answers four questions quickly: which fruit or vegetable, which oil, whether the sweetness comes from sugar or jaggery, and how to store the jar after opening. If a label hides behind vague words like “special masala” with no oil or sweetener named, treat that as a reason to look elsewhere.</p>
<p>Also look for the FSSAI licence number and the name of the business that packs the jar. On The Pickle Affair jars and footer you will see Arham Foods with licence 21521053000490 — you can match that number against the FSSAI FoSCoS portal yourself.</p>
<ul>
  <li>Ingredients listed in plain words you recognise</li>
  <li>Net weight (our jars are 250 g and 500 g)</li>
  <li>Best-before guidance and storage note</li>
  <li>Packer name and FSSAI licence</li>
</ul>"""),
    ("Glossary: Gujarati pickle names in one place", """
<p>Online shops mix Hindi and Gujarati names, which makes searching harder than it should be. Here is how the words line up:</p>
<ul>
  <li><strong>Athanu</strong> — Gujarati for pickle; <em>achar</em> in Hindi.</li>
  <li><strong>Keri</strong> — raw mango; <em>aam</em> is the general Hindi word for mango.</li>
  <li><strong>Gor / Gol Keri</strong> — raw mango pickled with jaggery (gor/gol).</li>
  <li><strong>Chhundo</strong> — grated raw mango cooked or sun-set with sugar into a sweet relish.</li>
  <li><strong>Methia Keri</strong> — mango pickle led by split fenugreek (methi kuria).</li>
  <li><strong>Gunda / Lasoda</strong> — the sticky Cordia fruit used in Gunda Keri (lasode ka achar).</li>
  <li><strong>Katka Keri</strong> — mango cut into small pieces (katka) for a chunky everyday achar.</li>
</ul>"""),
    ("How much pickle to serve", """
<p>Traditional achar is strong by design. One level teaspoon beside a roti or a bowl of rice is usually enough for one person; a festive thali might carry two different teaspoons — one sweet and one spicy. Serving more than that tends to drown the meal rather than lift it.</p>
<p>For a family of four eating pickle at one meal a day, a 500 g jar typically lasts a few weeks. A household that only opens pickle on weekends is better served by a 250 g jar, which gets finished while the flavour is at its best.</p>"""),
    ("Keeping jars safe in humid weather", """
<p>Monsoon and coastal humidity are the hardest conditions for any oil-cured pickle. Moisture that condenses inside the lid can drip onto the surface, and a warm, damp cupboard speeds that up.</p>
<ol>
  <li>Keep the jar in the driest cupboard you have, away from the sink and stove steam.</li>
  <li>Wipe the inside of the lid with a dry cloth if you see droplets.</li>
  <li>Use a separate dry spoon kept only for pickle.</li>
  <li>Decant a week’s portion into a small dry bowl instead of opening the main jar at every meal.</li>
</ol>"""),
    ("What to check when a glass jar arrives", """
<p>Pickles travel in glass because glass does not react with oil, salt, or acid. When your parcel arrives, check the seal before anything else: the lid should be tight and there should be no oil seepage on the outer packing. A little oil on the rim is normal after transit and can be wiped away.</p>
<p>If a jar arrives cracked or the seal is broken, do not taste it — photograph it and contact us through the Contact page so it can be replaced. Once opened, move the jar straight to a cool cupboard rather than leaving it on the counter.</p>"""),
    ("Choosing between 250 g and 500 g jars", """
<p>Every Pickle Affair variety comes in 250 g and 500 g jars. The smaller jar is the right first order when you are trying a new style — you find out whether your family likes methi bitterness or jaggery sweetness without committing to a large jar.</p>
<p>Once a style becomes a household staple, the 500 g jar makes more sense per gram and means fewer re-orders. If you want more than 500 g of one style, two 500 g jars are better than one huge jar: one stays sealed and fresh while the other is in use.</p>"""),
    ("Pairing sweet and spicy on one table", """
<p>Gujarati meals balance sweet, sour, salty, and hot on the same plate, and pickles follow the same rule. When you serve two jars, choose one from each side: a sweet jar such as Chhundo, Meethi Keri, or Gor Keri, and a sharper jar such as Katka Keri, Gunda Keri, or Chana Keri Methi.</p>
<p>That pairing covers guests who prefer mild food and those who want heat, and it is also the easiest way to gift pickles to a family whose taste you do not know well.</p>"""),
]


MAX_SUPPORT_SECTIONS = 1


def _pick_support(topic_id: str, count: int) -> list[tuple[str, str]]:
    import hashlib

    start = int(hashlib.md5(topic_id.encode()).hexdigest(), 16) % len(SUPPORT_SECTIONS)
    return [SUPPORT_SECTIONS[(start + i) % len(SUPPORT_SECTIONS)] for i in range(count)]


def custom_depth(topic: dict) -> str:
    parts = [f"<h2>Quick answer</h2>\n<p>{topic['quick_answer']}</p>"]
    for s in topic.get("sections") or []:
        parts.append(f"<h2>{s['h2']}</h2>")
        parts.extend(f"<p>{p}</p>" for p in s.get("p") or [])
        if s.get("list"):
            tag = "ol" if s.get("ordered") else "ul"
            parts.append(f"<{tag}>" + "".join(f"<li>{i}</li>" for i in s["list"]) + f"</{tag}>")
    return "\n".join(parts)


def build_custom_article(topic: dict) -> tuple[str, str, str, str, str]:
    """Article from topic-specific content; support sections vary per topic to reach MIN_WORDS."""
    kw = topic["primary_keyword"]
    title = topic["title"]
    if len(title) > 70:
        title = title[:67].rstrip() + "…"
    excerpt = (topic.get("excerpt") or f"{title} — practical guidance from The Pickle Affair’s Kathiawadi kitchen.")[:155]
    products = topic.get("product_handles") or []
    collections = topic.get("collection_handles") or ["buy-gujarati-pickle-online"]
    faqs = [tuple(f) for f in topic.get("faqs") or []] + [
        ("Does The Pickle Affair use synthetic colours?", "No. Colour comes from the spices, turmeric, chilli, and mango themselves."),
        ("Who makes The Pickle Affair pickles?", "The Pickle Affair is a brand of Arham Foods, packed in Maharashtra under FSSAI licence 21521053000490."),
    ]
    faq_json = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs
        ],
    }
    faq_html = "".join(
        f'<div class="dp-faq-item"><h3 class="dp-faq-question">{q}</h3><p>{a}</p></div>' for q, a in faqs
    )
    toc_items = ["Quick answer"] + [s["h2"] for s in topic.get("sections") or []] + ["Jars to consider", "FAQs"]
    toc = "<h2>In this guide</h2>\n<ul>" + "".join(f"<li>{t}</li>" for t in toc_items) + "</ul>"

    def assemble(support: list[tuple[str, str]]) -> str:
        support_html = "".join(f"<h2>{h}</h2>{b}" for h, b in support)
        return f"""
<script type="application/ld+json">{json.dumps(faq_json, ensure_ascii=False)}</script>
<p class="dp-lead">{excerpt}</p>
{toc}
{custom_depth(topic)}
{support_html}
{collection_cta(collections)}
{product_cta(products)}
<h2>Frequently asked questions</h2>
{faq_html}
<h2>Conclusion</h2>
<p>{topic.get('conclusion') or f'Use the collections above to compare jars for {kw}, start with one 250 g jar if the style is new to you, and keep a dry spoon habit from the first day.'}</p>
<p><a href="/blogs/kitchen-tales">More Kitchen Tales guides →</a></p>
""".strip()

    support: list[tuple[str, str]] = []
    body = assemble(support)
    skip = set(topic.get("skip_support") or [])
    for extra in _pick_support(topic["id"], len(SUPPORT_SECTIONS)):
        if word_count(body) >= MIN_WORDS or len(support) >= MAX_SUPPORT_SECTIONS:
            break
        if extra[0] in skip:
            continue
        support.append(extra)
        body = assemble(support)

    tags = f"{topic.get('category', 'Heritage Recipes')}, {kw}"
    primary = products[0] if products else next(iter(PRODUCTS))
    image = PRODUCTS[primary]["image"] if primary in PRODUCTS else PRODUCTS[next(iter(PRODUCTS))]["image"]
    return title, excerpt, body, tags, image


def build_long_article(topic: dict) -> tuple[str, str, str, str, str]:
    topic = enrich_topic(topic)
    if topic.get("sections") and topic.get("quick_answer"):
        return build_custom_article(topic)
    kw = topic["primary_keyword"]
    title = topic["title"]
    if len(title) > 70:
        title = title[:67].rstrip() + "…"
    excerpt = (
        f"{title} — practical guidance from The Pickle Affair’s Kathiawadi kitchen. "
        f"Learn about {kw} with clear tips you can use at home."
    )[:155]
    products = topic.get("product_handles") or []
    collections = topic.get("collection_handles") or ["buy-gujarati-pickle-online"]
    angle = topic.get("angle", "")
    secondary = ", ".join(topic.get("secondary") or [])

    middle = angle_depth(angle, kw)
    toc = """
<h2>In this guide</h2>
<ul>
  <li>Quick answer</li>
  <li>Deep explanation</li>
  <li>Practical steps / choosing path</li>
  <li>Common mistakes</li>
  <li>Related collections and products</li>
  <li>FAQs</li>
</ul>
"""
    faqs = [
        (f"What is this guide about?", f"It explains {kw} for home cooks exploring Gujarati and Kathiawadi pickles, with links to the right collections and jars."),
        ("Does The Pickle Affair use synthetic colours?", "No. We focus on traditional spice character without synthetic colours."),
        ("Where are products prepared?", "The Pickle Affair prepares pickles in an FSSAI-certified kitchen context for hygienic production."),
        ("Should I read a collection page or a product page first?", "Use a collection page to compare styles, then a product page to choose size and confirm ingredients."),
        ("Can you share exact recipe quantities?", "House recipes stay with the kitchen. We share useful method and flavour context without inventing proprietary numbers."),
        ("How do I store jars after delivery?", "Cool, dry place; sealed jar; clean dry spoon. Follow the label for best-before guidance."),
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
    conclusion = f"""
<h2>Conclusion</h2>
<p>If you came here for <strong>{kw}</strong>, use the collections linked above to shop by intent, then pick an individual jar that matches your meals. Keep storage habits tight, ignore medical hype, and prefer clear labels over the cheapest listing.</p>
<p>Kitchen Tales exists to support those shopping hubs and product pages with honest education — quality over volume, one intent per URL.</p>
"""
    body = f"""
<script type="application/ld+json">{json.dumps(faq_json, ensure_ascii=False)}</script>
<p class="dp-lead">{excerpt}</p>
{toc}
{middle}
{collection_cta(collections)}
{product_cta(products)}
<h2>Related Kitchen Tales</h2>
<ul>
  <li><a href="/blogs/kitchen-tales">All Kitchen Tales guides</a></li>
  <li><a href="/collections/all-mango-pickles">All Mango Pickles collection</a></li>
  <li><a href="/collections/buy-gujarati-pickle-online">Buy Gujarati Pickle Online</a></li>
</ul>
<h2>Frequently asked questions</h2>
{faq_html}
{conclusion}
<p><em>Cluster: {topic.get('cluster')} · Intent: {topic.get('intent')} · Related terms: {secondary}</em></p>
<p><em>Policy: BLOG.md — target ~{MIN_WORDS}+ words for standard guides; link collections + products; no invented quantities.</em></p>
""".strip()

    # Ensure minimum length with useful expansion blocks (not keyword stuffing)
    guard = 0
    while word_count(body) < MIN_WORDS and guard < 3:
        guard += 1
        extra = f"""
<h2>How search intent maps to our pages (block {guard})</h2>
<p>People researching <strong>{kw}</strong> usually arrive with one of three jobs: learn, compare, or buy. Kitchen Tales handles learn/compare. Collections handle browse-by-intent. Product pages handle the final jar choice. Keeping those jobs on separate URLs prevents cannibalization and matches how strong D2C pickle brands structure their catalogues.</p>
<p>Competitor catalogues (for example Homepick’s many hubs across sweet, savoury, mango, regional and gifting) show that shoppers expect multiple entry points. We copy the <em>architecture idea</em>, not their sentences: only create a collection when we have real products and a distinct primary keyword.</p>
<p>When you finish this article, open the first collection link, skim the buying guidance and FAQ there, then open at most two product cards. That path converts better than bouncing between random blog posts with no shopping context.</p>
<h2>Practical weekly routine for pickle lovers</h2>
<ol>
  <li>Cook your most common meal (thepla, khichdi, or dal-rice).</li>
  <li>Note whether you wanted sweet contrast or spicy brightness.</li>
  <li>Buy one jar in that lane from the matching collection.</li>
  <li>Store it with a dry spoon habit from day one.</li>
  <li>Only then explore specialty jars like Gunda Keri or methi-forward styles.</li>
</ol>
<p>This routine keeps SEO content honest: every guide should make the next click obvious. If a paragraph does not help you choose a collection, a product, or a storage habit, it does not belong in Kitchen Tales.</p>
<p>Related secondary themes for this topic include: {secondary}. Use them as supporting language, not as excuses to publish near-duplicate URLs.</p>
"""
        body = body.replace(
            "<h2>Frequently asked questions</h2>",
            extra + "\n<h2>Frequently asked questions</h2>",
            1,
        )

    tags = f"{topic.get('category', 'Heritage Recipes')}, {kw}"
    primary = products[0] if products else next(iter(PRODUCTS))
    image = PRODUCTS[primary]["image"] if primary in PRODUCTS else PRODUCTS[next(iter(PRODUCTS))]["image"]
    return title, excerpt, body, tags, image
