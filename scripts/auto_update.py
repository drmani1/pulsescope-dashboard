#!/usr/bin/env python3
"""PulseScope daily SAFE automatic additions.

Pull bibliographic records directly from NLM PubMed and selected verified
510(k) metadata from the official FDA API. No RSS redirectors, link shorteners,
AI-generated claims, advertising networks, or arbitrary publishers.

The job does NOT establish that a new study's findings are valid, and it
does not substitute for the separately scheduled editorial global briefing.
"""
import datetime as dt
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from validate_sources import trusted_url, validate

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "briefings.json"
STATUS = ROOT / "data" / "status.json"
UTC = dt.timezone.utc
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
NOW = dt.datetime.now(UTC)
TODAY = NOW.astimezone(IST).date()
HEADERS = {
    "User-Agent": "PulseScope-Wearable-Research/1.0 (https://github.com/drmani1/pulsescope-dashboard)",
    "Accept": "application/json",
}
API_HOSTS = {"eutils.ncbi.nlm.nih.gov", "api.fda.gov"}
TITLE_MATCH = re.compile(
    r"\b(?:wearables?|smart[\s-]?watch(?:es)?|smart[\s-]?rings?|"
    r"photoplethysmograph(?:y|ic)|continuous glucose monitor(?:ing)?|"
    r"ambulatory (?:ecg|electrocardiograph)|electrodermal|"
    r"biosensors?|smart textile|skin patch(?:es)?|cardiac patch|"
    r"blood.pressure monitor(?:ing)?|heart.rate variability|"
    r"muscle oxygenation|near.infrared spectroscopy|sleep tracking|"
    r"remote patient monitoring|cuffless|noninvasive (?:glucose|blood pressure))\b",
    re.IGNORECASE,
)
DEVICE_MATCH = re.compile(
    r"(?:wearab|holter|ambulatory|patch|continuous glucose|"
    r"electrocardio|cardiac monitor|pulse oximet|blood pressure|"
    r"non.invasive|smart.watch|photoplethysmograph)",
    re.IGNORECASE,
)


def request_json(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in API_HOSTS:
        raise ValueError("API hostname was not preapproved")
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=24) as response:
        final = urllib.parse.urlsplit(response.geturl())
        if final.scheme != "https" or final.hostname not in API_HOSTS:
            raise ValueError("API attempted an unapproved redirect")
        return json.loads(response.read(1_500_000).decode("utf-8"))


def ensure_public_fda_pdf(address):
    """Check that the PDF is served from FDA, not an arbitrary redirect."""
    if not trusted_url(address):
        return False
    try:
        req = urllib.request.Request(
            address, method="HEAD", headers={"User-Agent": HEADERS["User-Agent"]}
        )
        with urllib.request.urlopen(req, timeout=16) as response:
            final = urllib.parse.urlsplit(response.geturl())
            mime = (response.headers.get("Content-Type") or "").lower()
            return (
                response.status == 200
                and final.scheme == "https"
                and final.hostname is not None
                and final.hostname.endswith(".fda.gov")
                and "pdf" in mime
            )
    except (OSError, urllib.error.URLError, ValueError):
        return False


def pubmed_items():
    term = (
        "(wearable[Title/Abstract] OR smartwatch[Title/Abstract] OR "
        "photoplethysmography[Title/Abstract] OR "
        "\"continuous glucose monitoring\"[Title/Abstract] OR "
        "\"remote patient monitoring\"[Title/Abstract] OR "
        "\"smart textile\"[Title/Abstract] OR "
        "\"heart rate variability\"[Title/Abstract]) "
        "AND (monitor*[Title/Abstract] OR device[Title/Abstract] OR "
        "sensor[Title/Abstract] OR health[Title/Abstract] OR "
        "clinical[Title/Abstract])"
    )
    esearch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode({
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": "30",
        "datetype": "edat",  # New indexed records, not necessarily new publication dates.
        "reldate": "3",
        "sort": "pub_date",
        "tool": "PulseScope",
    })
    search = request_json(esearch)
    ids = search.get("esearchresult", {}).get("idlist", [])
    ids = [str(x) for x in ids if re.fullmatch(r"\d{5,12}", str(x))]
    if not ids:
        return []
    esummary = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(ids[:30]),
        "retmode": "json",
    })
    records = request_json(esummary).get("result", {})
    gathered = []
    for pmid in ids:
        doc = records.get(pmid, {})
        title = re.sub(r"\s+", " ", str(doc.get("title", ""))).strip()
        if not title or not TITLE_MATCH.search(title):
            continue
        journal = str(doc.get("fulljournalname") or doc.get("source") or "PubMed journal record")
        pubdate = str(doc.get("pubdate") or "date not supplied")
        authors = doc.get("authors") or []
        first_author = str(authors[0].get("name", "")) if authors and isinstance(authors[0], dict) else ""
        source_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        if not trusted_url(source_url):
            continue
        gathered.append({
            "id": "pubmed-" + pmid,
            "date": TODAY.isoformat(),
            "category": "tech",
            "region": "Global",
            "country": "International",
            "company": first_author or journal[:100],
            "title": "Newly indexed wearable research: " + title[:210],
            "summary": (
                f"A publication titled '{title[:230]}' was found in the U.S. National "
                f"Library of Medicine's PubMed index. Journal: {journal[:120]}; "
                f"publication date as listed: {pubdate[:60]}. This is bibliographic "
                "discovery only; methods, results, peer-review status and medical "
                "claims have not been independently evaluated."
            ),
            "impact": (
                "Research lead for founders: examine the original study, accuracy, "
                "sample size and real-world validation before drawing product conclusions."
            ),
            "status": (
                "New PubMed-indexed research lead. NOT FDA approval, EU CE marking "
                "or confirmed clinical benefit."
            ),
            "source": "U.S. National Library of Medicine · PubMed",
            "sourceUrl": source_url,
            "priority": "low",
            "tag": "PubMed research discovery · requires appraisal",
        })
        if len(gathered) >= 6:
            break
    return gathered


def fda_items():
    # Official API is updated monthly; this deliberately does not claim daily
    # or comprehensive coverage. Only an official FDA PDF is linked.
    start = TODAY - dt.timedelta(days=45)
    search = f"decision_date:[{start:%Y%m%d} TO {TODAY:%Y%m%d}]"
    query = "https://api.fda.gov/device/510k.json?" + urllib.parse.urlencode({
        "search": search,
        "sort": "decision_date:desc",
        "limit": "100",
    })
    results = request_json(query).get("results", [])
    output = []
    for item in results:
        number = str(item.get("k_number", "")).upper()
        name = re.sub(r"\s+", " ", str(item.get("device_name", ""))).strip()
        date = str(item.get("decision_date", ""))
        decision = str(item.get("decision_description", ""))
        code = str(item.get("decision_code", ""))
        if not (
            re.fullmatch(r"K\d{6}", number)
            and re.fullmatch(r"\d{8}", date)
            and DEVICE_MATCH.search(name)
            and ("substantial" in decision.lower() or code.upper().startswith("SE"))
        ):
            continue
        decision_date = dt.datetime.strptime(date, "%Y%m%d").date()
        if (TODAY - decision_date).days not in range(0, 46):
            continue
        # The K number is issued by FDA; only show a direct FDA letter when
        # it can actually be retrieved with a PDF content type.
        yy = number[1:3]
        letter = f"https://www.accessdata.fda.gov/cdrh_docs/pdf{yy}/{number}.pdf"
        if not ensure_public_fda_pdf(letter):
            continue
        applicant = str(item.get("applicant") or "FDA 510(k) record")
        output.append({
            "id": "fda-510k-" + number,
            "date": decision_date.isoformat(),
            "category": "regulatory",
            "region": "US",
            "country": "United States",
            "company": applicant[:120],
            "title": f"FDA 510(k) substantially equivalent decision: {name[:200]} ({number})",
            "summary": (
                f"FDA 510(k) source identifies {name[:150]} (applicant {applicant[:100]}) "
                f"as substantially equivalent with decision date {decision_date.isoformat()}. "
                "Direct FDA clearance PDF is linked. Verify intended use and whether the "
                "product is actually worn by patients before drawing wearable-market conclusions."
            ),
            "impact": "Official clearance record; a 510(k) clearance is not a PMA approval.",
            "status": "FDA 510(k) substantially equivalent decision (NOT PMA approval)",
            "source": "U.S. FDA · 510(k) decision letter",
            "sourceUrl": letter,
            "priority": "medium",
            "tag": "FDA 510(k) · official decision record",
        })
        if len(output) >= 5:
            break
    return output


def main():
    raw = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    existing = {str(item["id"]): item for item in raw["items"] if isinstance(item, dict) and item.get("id")}
    total_old = len(existing)
    new = 0
    outcomes = {}
    for key, loader in (("PubMed", pubmed_items), ("FDA 510k", fda_items)):
        try:
            found = loader()
            for item in found:
                if not trusted_url(item.get("sourceUrl")):
                    raise ValueError(f"Unsafe URL for {item.get('id')}")
                if item["id"] not in existing:
                    existing[item["id"]] = item
                    new += 1
            outcomes[key] = {"status": "ok", "newRecords": new}
        except Exception as exc:
            outcomes[key] = {"status": "unavailable", "reason": str(exc)[:140]}
            print(f"{key} unavailable: {type(exc).__name__}: {exc}")
    checked = NOW.isoformat(timespec="seconds").replace("+00:00", "Z")
    status = {
        "lastCheckedAtUTC": checked,
        "lastCheckedDateIST": TODAY.isoformat(),
        "addedThisCheck": new,
        "recordsInArchive": len(existing),
        "sources": outcomes,
        "disclaimer": (
            "Official bibliographic and FDA-record discovery only. Not exhaustive "
            "for FDA/CDSCO/EU MDR, wellness, acquisitions or the worldwide industry. "
            "Research findings need editorial review before clinical claims."
        ),
    }
    if new:
        raw["items"] = sorted(existing.values(), key=lambda row: (row.get("date",""), row.get("id","")), reverse=True)
        raw["asOf"] = max(raw.get("asOf", TODAY.isoformat()), TODAY.isoformat())
        # Verify everything before writing; no arbitrary URLs.
        for item in raw["items"]:
            if not trusted_url(item.get("sourceUrl", "")) or str(item["id"]).startswith("feed-"):
                raise ValueError("Existing or new archive entry violates the trusted source policy.")
        ARCHIVE.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        validate(ARCHIVE)
    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"PulseScope check {TODAY}: {new} added, {len(existing)} retained "
        f"(previously {total_old}); {outcomes}"
    )


if __name__ == "__main__":
    main()
