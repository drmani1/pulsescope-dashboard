#!/usr/bin/env python3
"""Merge a verified daily briefing into PulseScope without losing prior records."""
import json
import re
import sys
from pathlib import Path
from validate_sources import trusted_url, validate as validate_archive

ARCHIVE = Path(__file__).resolve().parents[1] / "data" / "briefings.json"
CATEGORIES = {"tech", "regulatory", "deals", "wellness"}

def load(path):
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict) or not isinstance(obj.get("items"), list):
        raise ValueError("Expected an object with an items array")
    return obj

def validate(x):
    for k in ("id", "date", "category", "title", "sourceUrl"):
        if not x.get(k):
            raise ValueError(f"Missing {k}")
    if x["category"] not in CATEGORIES or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x["date"]):
        raise ValueError("Invalid category or date")
    if not trusted_url(x["sourceUrl"]):
        raise ValueError("Source URL must use an approved, direct HTTPS publisher/regulator domain")
    if str(x["id"]).startswith("feed-"):
        raise ValueError("Unreviewed Google News feed records are blocked")

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/merge_daily.py briefing.json")
    old, new = load(ARCHIVE), load(sys.argv[1])
    by_id = {row["id"]: row for row in old["items"]}
    for row in new["items"]:
        validate(row)
        by_id[row["id"]] = row
    out = {"asOf": max(old["asOf"], new.get("asOf", old["asOf"])), "timezone": "Asia/Kolkata",
           "items": sorted(by_id.values(), key=lambda v:(v["date"],v["id"]), reverse=True)}
    # Verify every link before saving; never import redirected feed entries.
    for row in out["items"]:
        validate(row)
    ARCHIVE.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_archive(ARCHIVE)
    print(f"Merged {len(new['items'])} rows; total {len(out['items'])}")

if __name__ == "__main__":
    main()
