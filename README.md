# PulseScope — Global Medical Wearables Intelligence

The same dashboard URL will be **https://drmani1.github.io/pulsescope-dashboard/** once GitHub Pages has been enabled.

## Enable the website (one-time)

Open [Settings → Pages](https://github.com/drmani1/pulsescope-dashboard/settings/pages) and choose **Build and deployment → Source → GitHub Actions**. Inspect the [Actions tab](https://github.com/drmani1/pulsescope-dashboard/actions) for successful deployment; the website URL may return 404 until then.

## Daily updates

- `.github/workflows/daily.yml` audits only vetted links every day at approximately **08:15 IST** and republishes the validated archive. Unreviewed RSS ingestion is disabled.
- The **separate 8:00 AM ChatGPT editorial briefing is not automatically integrated with GitHub**. To publish its verified JSON output, merge it with `python scripts/merge_daily.py daily.json`, then commit the changed archive to `main`. Alternatively, ask ChatGPT to publish a briefing in a conversation with GitHub write access.
- GitHub Actions may fail or be suspended. Check the [daily workflow](https://github.com/drmani1/pulsescope-dashboard/actions/workflows/daily.yml) periodically; this is not a guarantee of uninterrupted updates.

## Archive and exports

The shared cumulative `data/briefings.json` is fetched when the page opens and again every 15 minutes. Previous days are retained. The dashboard offers CSV and JSON exports. Browser-only imports are not published across devices unless separately merged and committed to GitHub.

This is a **selective news intelligence feed**, not a complete regulator database. For confirmed FDA 510(k), CDSCO licences or EU MDR certificates, use official primary records. The repository is public; do not add private health information or credentials.


## Link-safety policy (12 Nov 2026)

PulseScope now uses a **reviewed source-domain allowlist** for both the website and its publishing/merging pipeline, implemented in `scripts/validate_sources.py` and `index.html`. It allows direct HTTPS URLs to official regulators, universities, peer-reviewed science publishers, clinical-trial registries, confirmed companies and carefully selected medical-news outlets. It blocks unknown URLs, Google News redirect links, common tracking redirects, and unsafe imports. Approved links show their destination domain; external links open without sharing the dashboard as a referrer.

**Removed from the visible dashboard:** 13 historical unreviewed Google News RSS links that could redirect to unpredictable pages. The earlier records remain in Git history for auditing. The 15 editor-reviewed research/regulatory/news records are retained.

**Automatic discovery paused for link safety:** The old Google News RSS script is intentionally disabled. The daily GitHub Actions job now audits and republishes **only previously vetted records**, not third-party RSS headlines. The 8:00 AM IST ChatGPT editorial briefing remains scheduled and can publish new verified items only when GitHub write access is available. If no verified records are published, the dashboard may show yesterday's data; this is safer than posting unverified links. Do not imply that daily content updates are guaranteed.

**Limits:** HTTPS and an approved domain reduce exposure but cannot guarantee that external pages will never be compromised, changed or redirected. Before adding a new source domain, manually inspect both the company/agency identity and the final linked page. To add a new vetted host, update the allowlists in both `scripts/validate_sources.py` and `index.html`.

