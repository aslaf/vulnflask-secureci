#!/usr/bin/env python3
"""
notify_slack.py — clean rebuild (Day 15 Observability)
Sends a concise status message to Slack.
"""
import os
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "triage-summary.md"
WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")


def summarize():
    """Return counts of critical/high findings, or (0,0) if file missing."""
    if not REPORT.exists():
        print("[WARN] triage-summary.md not found — placeholder summary sent.")
        return 0, 0
    text = REPORT.read_text(encoding="utf-8", errors="ignore")
    critical = text.count("CRITICAL:")
    high = text.count("HIGH:")
    return critical, high


def notify():
    """Post summary message to Slack."""
    if not WEBHOOK:
        print("[ERROR] SLACK_WEBHOOK_URL not found in environment.")
        return

    critical, high = summarize()
    total = critical + high
    color = "#2ECC71" if total == 0 else "#E74C3C"

    payload = {
        "attachments": [
            {
                "fallback": "Security summary",
                "color": color,
                "title": "🛡️ VulnFlask-SecureCI — Weekly Security Report",
                "text": f"*High/Critical Findings:* {total}\nGenerated: {datetime.utcnow().isoformat()} UTC",
                "footer": "GitHub Actions – Day 15 Observability",
            }
        ]
    }

    try:
        r = requests.post(WEBHOOK, json=payload, timeout=10)
        r.raise_for_status()
        print(f"[INFO] Slack message sent ({r.status_code}).")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Slack post failed: {e}")


if __name__ == "__main__":
    notify()
