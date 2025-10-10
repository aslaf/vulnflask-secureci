#!/usr/bin/env python3
"""
notify_slack.py
-----------------------------------
Day 15 – Observability & Notifications
Sends summarized security notifications to Slack
using the SLACK_WEBHOOK_URL secret.
"""

import os
from datetime import datetime
from pathlib import Path

import requests

# --------------------------------------------------------------------
# Paths & Config
# --------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "triage-summary.md"
WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def extract_summary():
    """
    Extract critical/high issue counts from triage-summary.md.
    If the file doesn't exist, return (0, 0) and log warning.
    """
    if not REPORT.exists():
        print("[WARN] triage-summary.md not found, sending placeholder message.")
        return 0, 0

    try:
        text = REPORT.read_text(encoding="utf-8")
        critical = text.count("CRITICAL:")
        high = text.count("HIGH:")
        print(f"[INFO] Extracted findings → CRITICAL={critical}, HIGH={high}")
        return critical, high
    except Exception as e:
        print(f"[ERROR] Failed to read triage-summary.md: {e}")
        return 0, 0


def notify_slack():
    """
    Build Slack message and send to configured webhook.
    """
    critical, high = extract_summary()
    if not WEBHOOK:
        print("[ERROR] SLACK_WEBHOOK_URL not set. Exiting.")
        return

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
        print(f"[ERROR] Slack API call failed: {e}")


# --------------------------------------------------------------------
# Entry Point
# --------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Slack Notification Runner (Day 15) ===")
    notify_slack()
