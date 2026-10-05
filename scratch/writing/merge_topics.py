#!/usr/bin/env python3
"""Append validated writer batches (scratch/_new_*.json) to topic_library.json, then delete them.

Usage: python3 scratch/writing/merge_topics.py scratch/_new_H.json [more files...]
Run validate_topics.py on each file first; topics whose id already exists are replaced in place.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "scratch" / "topic_library.json"

lib = json.loads(LIB.read_text())
topics = lib["topics"] if isinstance(lib, dict) else lib
index = {t["id"]: i for i, t in enumerate(topics)}
added = replaced = 0
for name in sys.argv[1:]:
    path = Path(name)
    batch = json.loads(path.read_text())
    batch = batch["topics"] if isinstance(batch, dict) else batch
    for t in batch:
        t.pop("draft", None)
        if t["id"] in index:
            topics[index[t["id"]]] = t
            replaced += 1
        else:
            index[t["id"]] = len(topics)
            topics.append(t)
            added += 1
    path.unlink()
LIB.write_text(json.dumps(lib, indent=2, ensure_ascii=False) + "\n")
print(f"added {added} · replaced {replaced} · total {len(topics)}")
