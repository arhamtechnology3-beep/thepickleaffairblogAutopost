#!/usr/bin/env python3
"""Ensure up to 5 blog posts are live each IST day (publishes queued drafts if needed)."""
from __future__ import annotations

import datetime as dt
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shopify_auth import resolve_access_token, shop_url  # noqa: E402

SHOP_URL = shop_url()
TOKEN = ""
BLOG_ID = os.environ.get("SHOPIFY_BLOG_ID", "96853164183")
DAILY_TARGET = int(os.environ.get("DAILY_BLOG_COUNT", "5"))
API = "2024-10"
CTX = ssl.create_default_context()


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
    with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
        body = resp.read().decode()
        return json.loads(body) if body else {}


def ist_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))


def target_for_hour(hour: int) -> int:
    # Stagger: 1 by 10am, 2 by noon, 3 by 3pm, 4 by 6pm, 5 by 8pm
    if hour < 10:
        return 1
    if hour < 12:
        return 2
    if hour < 15:
        return 3
    if hour < 18:
        return 4
    return DAILY_TARGET


def main() -> None:
    now = ist_now()
    today = now.strftime("%Y-%m-%d")
    target = target_for_hour(now.hour)
    data = api("GET", f"/blogs/{BLOG_ID}/articles.json?limit=250")
    articles = data.get("articles", [])
    published = [a for a in articles if a.get("published_at")]
    drafts = sorted([a for a in articles if not a.get("published_at")], key=lambda a: a["id"])
    today_pub = [a for a in published if str(a.get("published_at", "")).startswith(today)]
    needed = max(0, target - len(today_pub))

    print(f"IST {now:%Y-%m-%d %H:%M} · today={len(today_pub)} · target={target} · needed={needed} · drafts={len(drafts)}")
    if needed == 0:
        print("Target already met.")
        return
    if not drafts:
        print("No drafts. Run generate_daily_blogs.py first.")
        return

    slots = ["09:00:00+05:30", "11:00:00+05:30", "14:00:00+05:30", "17:00:00+05:30", "19:30:00+05:30"]
    for idx, art in enumerate(drafts[:needed]):
        slot = slots[min(len(today_pub) + idx, len(slots) - 1)]
        payload = {
            "article": {
                "id": art["id"],
                "published": True,
                "published_at": f"{today}T{slot}",
            }
        }
        api("PUT", f"/blogs/{BLOG_ID}/articles/{art['id']}.json", payload)
        print(f"Published draft {art['id']}: {art['title']}")


if __name__ == "__main__":
    main()
