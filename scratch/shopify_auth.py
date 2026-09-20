#!/usr/bin/env python3
"""Resolve Shopify Admin API access token for Blog Autopost.

Dev Dashboard apps do not show a permanent shpat_ token.
Use Client Credentials grant (same as Postman):

  POST https://{shop}.myshopify.com/admin/oauth/access_token
  grant_type=client_credentials
  client_id=...
  client_secret=...

Tokens expire ~24h — request a fresh one each workflow run.
"""
from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()


def shop_url() -> str:
    return os.environ.get("SHOPIFY_SHOP_URL", "https://the-pickle-affair.myshopify.com").rstrip("/")


def fetch_client_credentials_token() -> str:
    client_id = os.environ.get("SHOPIFY_CLIENT_ID", "").strip()
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return ""

    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode()
    req = urllib.request.Request(
        f"{shop_url()}/admin/oauth/access_token",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise SystemExit(f"Client credentials token request failed: {e.code} {err}") from e

    token = data.get("access_token") or ""
    if not token:
        raise SystemExit(f"No access_token in response: {data}")
    return token


def resolve_access_token() -> str:
    """Prefer Client ID/Secret (Postman-style); fall back to static SHOPIFY_ACCESS_TOKEN."""
    static = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
    if os.environ.get("SHOPIFY_CLIENT_ID") and os.environ.get("SHOPIFY_CLIENT_SECRET"):
        return fetch_client_credentials_token()
    if static:
        return static
    raise SystemExit(
        "Set SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET (Postman client_credentials), "
        "or SHOPIFY_ACCESS_TOKEN"
    )


if __name__ == "__main__":
    tok = resolve_access_token()
    print(tok[:12] + "…" if len(tok) > 12 else tok)
    print("OK — token acquired")
