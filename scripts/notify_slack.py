#!/usr/bin/env python3
"""
Send summarized security notifications to Slack
"""
import os
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "triage-summary.md"
WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")


def extract_summary():
    text = REPORT.read_text(encoding="utf-8")
    critical = text.count("CRITICAL:")
    high = text.count("HIGH:")
    return critical, high


def notify_slack():
    critical, high = extract_summary()
    color = "#2ECC71" if critical + high == 0 else "#E74C3C"
    msg = {
        "attachments": [
            {
                "fallback": "Security summary notification",
                "color": color,
                "title": "VulnFlask-SecureCI Security Report",
                "text": f"*High/Critical Issues:* {high + critical}\n*Generated:* {datetime.utcnow().isoformat()} UTC",
                "footer": "GitHub Actions - Day 15 Observability",
            }
        ]
    }
    requests.post(WEBHOOK, json=msg)


if __name__ == "__main__":
    notify_slack()
