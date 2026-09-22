"""Load Arham Foods keyword sheet bank and enrich topics/collections at runtime."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "scratch" / "keyword_bank.json"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower().replace("-", " ")).strip()


@lru_cache(maxsize=1)
def load_bank() -> dict:
    if not BANK_PATH.exists():
        return {"pillars": {}, "all_keywords": []}
    return json.loads(BANK_PATH.read_text())


def pillar_keywords(pillar_id: str) -> list[str]:
    return list(load_bank().get("pillars", {}).get(pillar_id, {}).get("keywords") or [])


def merge_keywords(existing: list[str] | None, pillar_ids: list[str], max_n: int = 16) -> list[str]:
    """Dedupe-preserving merge of existing + bank keywords for given pillars."""
    out: list[str] = []
    seen: set[str] = set()
    for k in list(existing or []):
        nk = _norm(k)
        if not nk or nk in seen:
            continue
        seen.add(nk)
        out.append(k)
    for pid in pillar_ids:
        for k in pillar_keywords(pid):
            nk = _norm(k)
            if not nk or nk in seen:
                continue
            seen.add(nk)
            out.append(k)
            if len(out) >= max_n:
                return out
    return out


def enrich_topic(topic: dict, max_secondary: int = 14) -> dict:
    """Return a shallow-copied topic with secondary keywords filled from the bank."""
    t = dict(topic)
    pillar = t.get("keyword_pillar")
    pillars = [pillar] if pillar else list(t.get("keyword_pillars") or [])
    if pillars:
        t["secondary"] = merge_keywords(t.get("secondary"), pillars, max_secondary)
    return t


def enrich_collection(spec: dict, max_secondary: int = 16) -> dict:
    """Return a shallow-copied collection spec with secondary_keywords from the bank."""
    c = dict(spec)
    pillars = list(c.get("keyword_pillars") or [])
    if pillars:
        c["secondary_keywords"] = merge_keywords(c.get("secondary_keywords"), pillars, max_secondary)
    return c


def secondary_phrase(topic_or_spec: dict, field: str = "secondary", limit: int = 8) -> str:
    vals = list(topic_or_spec.get(field) or topic_or_spec.get("secondary_keywords") or [])
    return ", ".join(vals[:limit])
