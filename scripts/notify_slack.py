#!/usr/bin/env python3
"""
notify_slack.py — Day 15 Observability
Send summarized security notifications to Slack.
Gracefully handles missing triage-summary.md.
"""
import os
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "triage-summary.md"
WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")


def extract_summary():
    """
    Return (critical, high) counts.
    If file missing, return zeros and warn.
    """
    if not REPORT.exists():
        print("[WARN] triage-summary.md not found → sending placeholder notification.")
        return 0, 0

    try:
        text = REPORT.read_text(encoding="utf-8")
        critical = text.count("CRITICAL:")
        high = text.count("HIGH:")
        print(f"[INFO] Extracted summary: CRITICAL={critical}, HIGH={high}")
        return critical, high
    except Exception as e:
        print(f"[ERROR] Could not read summary file: {e}")
        return 0, 0


def notify_slack():
    """
    Build and send Slack message with fallback logic.
    """
    if not WEBHOOK:
        print("[ERROR] SLACK_WEBHOOK_URL not set in environment.")
        return

    critical, high = extract_summary()
    total = critical + high
    color = "#2ECC71" if total == 0 else "#E74C3C"

    msg = {
        "attachments": [
            {
                "fallback": "Security summary notification",
                "color": color,
                "title": "🛡️ VulnFlask-SecureCI — Security Report",
                "text": (
                    f"*High/Critical Issues:* {total}\n"
                    f"*Generated:* {datetime.utcnow().isoformat()} UTC"
                    + (
                        "\n_(No triage-summary.md found — placeholder run.)_"
                        if total == 0
                        else ""
                    )
                ),
                "footer": "GitHub Actions • Day 15 Observability",
            }
        ]
    }

    try:
        response = requests.post(WEBHOOK, json=msg, timeout=10)
        response.raise_for_status()
        print(f"[INFO] Slack notification sent successfully ({response.status_code}).")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Slack API request failed: {e}")


if __name__ == "__main__":
    print("=== Running Slack Notification ===")
    notify_slack()
