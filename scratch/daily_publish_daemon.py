#!/usr/bin/env python3
"""Publish queued drafts at today's random IST slots (never same-time batch)."""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import random
import ssl
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shopify_auth import resolve_access_token, shop_url  # noqa: E402

SHOP_URL = shop_url()
TOKEN = ""
BLOG_ID = os.environ.get("SHOPIFY_BLOG_ID", "96853164183")
DAILY_TARGET = int(os.environ.get("DAILY_BLOG_COUNT", "1"))
API = "2024-10"
CTX = ssl.create_default_context()
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def api(method: str, path: str, payload: dict | None = None) -> dict:
    global TOKEN
    if not TOKEN:
        TOKEN = resolve_access_token()
    data = None if payload is None else __import__("json").dumps(payload).encode()
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
    with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
        body = resp.read().decode()
        return __import__("json").loads(body) if body else {}


def ist_now() -> dt.datetime:
    return dt.datetime.now(IST)


def day_seed(day: dt.date) -> int:
    return int(hashlib.sha1(day.isoformat().encode()).hexdigest()[:8], 16)


def random_publish_slots(day: dt.date, count: int) -> list[dt.datetime]:
    rng = random.Random(day_seed(day) ^ 0xB106)
    candidates: list[dt.time] = []
    for hour in range(9, 21):
        for minute in (0, 15, 30, 45):
            candidates.append(dt.time(hour, minute))
    count = max(1, min(int(count), len(candidates)))
    picked = sorted(rng.sample(candidates, k=count))
    return [dt.datetime.combine(day, t, tzinfo=IST) for t in picked]


def main() -> None:
    now = ist_now()
    day = now.date()
    today = day.isoformat()
    slots = random_publish_slots(day, DAILY_TARGET)
    data = api("GET", f"/blogs/{BLOG_ID}/articles.json?limit=250")
    articles = data.get("articles", [])
    published = [a for a in articles if a.get("published_at")]
    drafts = sorted([a for a in articles if not a.get("published_at")], key=lambda a: a["id"])
    today_pub = [a for a in published if str(a.get("published_at", "")).startswith(today)]
    already = len(today_pub)

    print(
        f"IST {now:%Y-%m-%d %H:%M} · today={already} · target={DAILY_TARGET} · "
        f"slots={[s.strftime('%H:%M') for s in slots]} · drafts={len(drafts)}"
    )
    if already >= DAILY_TARGET:
        print("Target already met.")
        return
    if not drafts:
        print("No drafts. Run generate_daily_blogs.py first.")
        return

    next_idx = already
    due = slots[next_idx]
    if now < due:
        print(f"Waiting for random slot {due.strftime('%H:%M')} IST — no draft publish.")
        return

    art = drafts[0]
    payload = {
        "article": {
            "id": art["id"],
            "published": True,
            "published_at": now.isoformat(),
        }
    }
    api("PUT", f"/blogs/{BLOG_ID}/articles/{art['id']}.json", payload)
    print(f"Published draft {art['id']} at random slot {due.strftime('%H:%M')}: {art['title']}")


if __name__ == "__main__":
    main()
