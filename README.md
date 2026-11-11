# PulseScope — Global Medical Wearables Intelligence

The same dashboard URL will be **https://drmani1.github.io/pulsescope-dashboard/** once GitHub Pages has been enabled.

## Enable the website (one-time)

Open [Settings → Pages](https://github.com/drmani1/pulsescope-dashboard/settings/pages) and choose **Build and deployment → Source → GitHub Actions**. Inspect the [Actions tab](https://github.com/drmani1/pulsescope-dashboard/actions) for successful deployment; the website URL may return 404 until then.

## Daily updates

- `.github/workflows/daily.yml` is scheduled for about **08:15 IST daily** (02:45 UTC); scheduled GitHub Actions runs may be delayed.
- `scripts/discover_news.py` discovers RSS news leads in medical wearables, wellness, FDA, CDSCO, EU MDR, and medtech M&A. New leads are explicitly **UNVERIFIED** and must never be treated as actual device approval/clearance or confirmed acquisition solely from their headline. An unavailable feed produces no new records.
- The daily workflow appends new leads without deleting prior records, commits `data/briefings.json`, and publishes the site at the same URL.
- The **separate 8:00 AM ChatGPT editorial briefing is not automatically integrated with GitHub**. To publish its verified JSON output, merge it with `python scripts/merge_daily.py daily.json`, then commit the changed archive to `main`. Alternatively, ask ChatGPT to publish a briefing in a conversation with GitHub write access.
- GitHub Actions may fail or be suspended. Check the [daily workflow](https://github.com/drmani1/pulsescope-dashboard/actions/workflows/daily.yml) periodically; this is not a guarantee of uninterrupted updates.

## Archive and exports

The shared cumulative `data/briefings.json` is fetched when the page opens and again every 15 minutes. Previous days are retained. The dashboard offers CSV and JSON exports. Browser-only imports are not published across devices unless separately merged and committed to GitHub.

This is a **selective news intelligence feed**, not a complete regulator database. For confirmed FDA 510(k), CDSCO licences or EU MDR certificates, use official primary records. The repository is public; do not add private health information or credentials.
