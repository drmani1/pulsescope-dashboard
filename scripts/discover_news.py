#!/usr/bin/env python3
"""Daily public-news discovery for PulseScope.
Titles from third-party feeds are NOT verified regulatory decisions.
Never delete previous stories; do not infer FDA approval or CE certification.
"""
import datetime as dt
import email.utils
import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ARCHIVE = BASE / "data" / "briefings.json"
TOPICS = [
    ("medical wearable sensors ECG remote patient monitoring when:2d", "tech", "Global"),
    ("new noninvasive glucose sensor wearable medical technology when:2d", "tech", "Global"),
    ("FDA wearable device clearance 510k digital health when:2d", "regulatory", "US"),
    ("CDSCO wearable medical device approval India when:2d", "regulatory", "India"),
    ("EU MDR CE mark wearable health medical device when:2d", "regulatory", "EU"),
    ("medtech wearable acquisition merger bought company when:2d", "deals", "Global"),
    ("smart ring sleep health tracking wellness wearable launch when:2d", "wellness", "Global"),
]
HEADERS = {"User-Agent": "PulseScopeResearch/1.0 (+https://github.com/drmani1/pulsescope-dashboard)"}
TODAY = dt.datetime.now(dt.timezone.utc).date()
LIMIT_PER_TOPIC = 4
MAX_NEW = 18

def load():
    with ARCHIVE.open(encoding="utf-8") as f:
        return json.load(f)

def fetch(query):
    q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=22) as response:
        xml = response.read(800000)
    root = ET.fromstring(xml)
    return root.findall("./channel/item")

def news_item(node, category, region):
    title = (node.findtext("title") or "").strip()
    url = (node.findtext("link") or "").strip()
    pub = (node.findtext("pubDate") or "").strip()
    if not title or not url.startswith("https://"):
        return None
    try:
        date = email.utils.parsedate_to_datetime(pub).astimezone(dt.timezone.utc).date()
    except (TypeError, ValueError):
        return None
    if (TODAY - date).days not in (0, 1, 2):
        return None
    # Stable ID deduplicates feed stories across executions.
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:18]
    source_node = node.find("source")
    publisher = (source_node.text or "").strip() if source_node is not None else "Google News RSS"
    return {
        "id": "feed-" + digest,
        "date": date.isoformat(),
        "category": category,
        "region": region,
        "country": "",
        "company": "",
        "title": title[:240],
        "summary": "Automatically discovered media headline; not independently verified. Check the original publication and official regulator or company records before relying on approval or acquisition claims.",
        "impact": "Research lead requiring source verification.",
        "status": "Unverified news discovery — not an established regulatory authorization",
        "source": publisher or "Google News RSS",
        "sourceUrl": url,
        "priority": "low",
        "tag": "Unverified feed"
    }

def main():
    data = load()
    existing = {item["id"]: item for item in data.get("items", [])}
    collected = []
    for query, category, region in TOPICS:
        try:
            nodes = fetch(query)
            count = 0
            for node in nodes:
                x = news_item(node, category, region)
                if x and x["id"] not in existing and x["id"] not in {y["id"] for y in collected}:
                    collected.append(x)
                    count += 1
                if count >= LIMIT_PER_TOPIC or len(collected) >= MAX_NEW:
                    break
            print(f"{category}/{region}: {count} new leads")
        except Exception as exc:
            print(f"Feed unavailable ({category}/{region}): {type(exc).__name__}: {exc}")
        if len(collected) >= MAX_NEW:
            break
    if not collected:
        print("No new feed leads; archive unchanged")
        return
    for x in collected:
        existing[x["id"]] = x
    data["items"] = sorted(existing.values(), key=lambda x:(x.get("date", ""),x.get("id", "")),reverse=True)
    data["asOf"] = max(data.get("asOf",""), TODAY.isoformat())
    data["timezone"] = "Asia/Kolkata"
    ARCHIVE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Added {len(collected)} unverified leads; retained {len(data['items'])} total records")

if __name__ == "__main__":
    main()
