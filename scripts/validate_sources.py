#!/usr/bin/env python3
"""Fail closed if a public PulseScope story contains a dubious destination.

This is a URL-policy and provenance gate, not proof a site is malware-free.
Editors must still check that the actual page supports the story.
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl

ARCHIVE = Path(__file__).resolve().parents[1] / "data" / "briefings.json"

# Exact registrable domains; subdomains are permitted only with a dot boundary.
TRUSTED_DOMAINS = {
    "fda.gov", "cdsco.gov.in", "europa.eu", "who.int", "nih.gov",
    "clinicaltrials.gov", "gov.uk", "canada.ca", "tga.gov.au",
    "pmda.go.jp", "mhlw.go.jp", "nmpa.gov.cn",
    "reuters.com", "mobihealthnews.com",
    "nature.com", "science.org", "nejm.org", "thelancet.com",
    "jamanetwork.com", "bmj.com",
    "mit.edu", "technion.ac.il", "heart.org",
    "counselhealth.com", "empatica.com", "skribemedical.com",
    "xr.health",
}
REDIRECT_PARAMS = {"url", "u", "target", "dest", "destination", "redirect", "redirect_uri", "redir",
                   "return", "returnurl", "next", "goto", "continue", "adurl", "link"}

def trusted_url(address):
    if not isinstance(address, str) or len(address) > 1800:
        return False
    if any(ord(c) <= 32 for c in address):
        return False
    try:
        url = urlsplit(address)
        host = (url.hostname or "").lower().rstrip(".")
        if not (url.scheme == "https" and host and url.username is None and
                url.password is None and url.port is None and
                all(ord(c) < 128 for c in host) and
                any(host == domain or host.endswith("." + domain)
                    for domain in TRUSTED_DOMAINS)):
            return False
        return not any(key.lower() in REDIRECT_PARAMS
                       for key, _ in parse_qsl(url.query, keep_blank_values=True))
    except (TypeError, ValueError):
        return False

def validate(path=ARCHIVE):
    d = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(d, dict) or not isinstance(d.get("items"), list):
        raise ValueError("Expected an archive containing an items array")
    invalid = []
    for item in d["items"]:
        if (not isinstance(item, dict) or
                str(item.get("id", "")).startswith("feed-") or
                not trusted_url(item.get("sourceUrl", ""))):
            invalid.append(str(item.get("id", "<missing>")))
    if invalid:
        raise ValueError("Blocked records / unreviewed URLs: " + ", ".join(invalid[:30]))
    print(f"Source policy passed for {len(d['items'])} reviewed stories.")
    print("Note: an allowed HTTPS domain is not a guarantee that a page is safe or accurate.")

if __name__ == "__main__":
    try:
        validate(Path(sys.argv[1]) if len(sys.argv) > 1 else ARCHIVE)
    except (OSError, ValueError) as err:
        sys.exit("Source link policy failed: " + str(err))
