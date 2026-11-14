# PulseScope — Global Medical Wearables Intelligence

**Permanent dashboard:** https://drmani1.github.io/pulsescope-dashboard/

Research and intelligence tracker for medical-grade wearables, health and wellness sensors, cardiovascular and metabolic monitoring, sleep and stress technologies, medtech corporate developments, and FDA / CDSCO / EU MDR. All historical entries remain in a cumulative, publicly readable source-linked archive.

## Automated daily publishing — enabled

- **08:00 IST**: Separate ChatGPT daily global editorial briefing (enabled). It is instructed to verify direct official/journal/company links and attempt to write curated additions to this repository using the connected GitHub tool. That write is conditional on the automation's available connection and successful completion; inspect the task result and repository commits rather than assuming it happened.
- **Approximately 08:15 IST every day**: [Daily PulseScope Safe-Source Updates](https://github.com/drmani1/pulsescope-dashboard/actions/workflows/daily.yml) runs automatically via GitHub Actions, including weekends. GitHub can delay, suspend, or fail scheduled runs.
  - Directly queries the **U.S. National Library of Medicine's PubMed E-utilities** for newly indexed, topically relevant wearable research metadata.
  - Checks the **official openFDA 510(k) database**, which is updated **monthly**; a matching record is posted only when its direct FDA decision-letter PDF can be checked. 510(k) clearance is never described as PMA approval.
  - Posts **only pre-approved direct HTTPS source URLs**; no Google News redirects, short links, ad funnels or third-party RSS ingestion.
  - Adds only genuinely new entries. Preserves prior records. If no new eligible findings are found, it records a daily check without inventing a story.
  - Commits the shared archive and last-check status, then **deploys the site to the same Pages URL in the same workflow** (GitHub Actions token commits do not trigger other workflows).
- **GitHub Pages** deployment from edited archive/UI also runs via [Publish PulseScope](https://github.com/drmani1/pulsescope-dashboard/actions/workflows/deploy.yml).

**Scope and accuracy:** The unattended PubMed feed is **bibliographic discovery, not clinical appraisal**. Indexed articles are not guaranteed peer reviewed or clinically valid. openFDA releases may lag; this is not exhaustive FDA clearance/approval monitoring. Autonomous regulatory/licensing tracking for **CDSCO and EU MDR**, company acquisitions and consumer wellness launches relies on the separate editorial task; those topics are **not claimed fully covered by the independent GitHub feed**.

## Historical archive and exports

- Cumulative reviewed/news records: `data/briefings.json`.
- Last automated source-check information: `data/status.json`.
- The dashboard loads published records and updates them every ~15 minutes while open.
- It displays the latest source-check status separately from the news snapshot, and supports **CSV and JSON** exports.
- Browser-only imports remain local unless explicitly merged into the GitHub repository.
- Publish an editorial JSON export via `python scripts/merge_daily.py briefing.json`, then commit the archive. The merge validates direct-source hostnames and preserves older records.

## Security

The domain policy is maintained in `scripts/validate_sources.py` (publishing) and `index.html` (browser). It restricts links to selected direct HTTPS government agencies, research organizations, journals, reputable news domains and verified company websites. Unknown/redirecting domains are blocked. **HTTPS and a vetted domain reduce risk but cannot guarantee that any site will remain uncompromised.** Verify the destination and the contents of a new page before relying on medical-device claims.

This is a **selective intelligence dashboard**, not a medical decision tool, an exhaustive global registry, or evidence that all linked products are clinically approved. The repository is public: never add private health data or credentials.
