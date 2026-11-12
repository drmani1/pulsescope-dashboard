#!/usr/bin/env python3
"""Legacy RSS ingestion intentionally disabled.

Google News RSS article URLs are redirects and may land on ad-laden, spammy
or otherwise unsafe destinations. PulseScope never publishes such links
automatically. New verified records must instead be reviewed, sourced from
trusted direct HTTPS hosts and merged via scripts/merge_daily.py.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
print("PulseScope RSS discovery disabled for link safety.")
print("Daily trusted-source audit still runs. New verified stories must be curated and merged.")
print("Use: python scripts/merge_daily.py verified_daily_brief.json")
sys.exit(0)
