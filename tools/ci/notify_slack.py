#!/usr/bin/env python3
"""
notify_slack.py — Day 15/16 Observability
Posts a compact security summary to Slack:
- Posture score + delta from previous run
- Most findings tool (+top severity hint when possible)
- Top category mapping
Falls back gracefully if files are missing.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import requests

ROOT = Path(__file__).resolve().parents[1]
WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")

INSIGHTS = ROOT / "insights.json"
TRIAGE = ROOT / "triage-summary.md"

# Optional raw reports for fallback
BANDIT = ROOT / "bandit-report.json"
SEMGREP = ROOT / "semgrep-report.json"
PIP_AUDIT = ROOT / "pip-audit-report.json"
TRIVY = ROOT / "trivy-report.json"
ZAP_HTML = ROOT / "report_html.html"


def load_json(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def summarize_high_crit() -> Tuple[int, int]:
    """Old behavior: count HIGH/CRITICAL from triage-summary.md if present."""
    if not TRIAGE.exists():
        return 0, 0
    text = TRIAGE.read_text(encoding="utf-8", errors="ignore")
    critical = text.count("CRITICAL:")
    high = text.count("HIGH:")
    return critical, high


def from_insights() -> Dict:
    """Return dict with score, delta, tools counts if insights.json exists."""
    data = load_json(INSIGHTS) or {}
    score = data.get("score")
    history = data.get("history") or []
    # delta vs previous
    delta = 0
    try:
        if len(history) >= 2:
            last = history[-1].get("score", score or 0)
            prev = history[-2].get("score", last)
            delta = round((last - prev), 1)
        elif score is not None:
            delta = 0
    except Exception:
        delta = 0

    tools = data.get("tools") or {}  # expected shape: {"bandit": N, "semgrep": N, ...}
    return {"score": score, "delta": delta, "tools": tools}


def count_bandit() -> int:
    d = load_json(BANDIT) or {}
    return len(d.get("results", []))


def count_semgrep() -> int:
    d = load_json(SEMGREP) or {}
    return len(d.get("results", []))


def count_pip_audit() -> int:
    d = load_json(PIP_AUDIT)
    if not d:
        return 0
    total = 0
    if isinstance(d, dict) and "dependencies" in d:
        for dep in d["dependencies"]:
            vulns = dep.get("vulns") or dep.get("vulnerabilities") or []
            total += len(vulns)
    elif isinstance(d, list):
        for dep in d:
            total += len(dep.get("vulns", []))
    return total


def count_trivy() -> Tuple[int, str]:
    """Return (total, top_sev_label) from Trivy JSON if available."""
    d = load_json(TRIVY) or {}
    total = 0
    sev_map: Dict[str, int] = {}
    for res in d.get("Results", []) or []:
        for v in res.get("Vulnerabilities", []) or []:
            total += 1
            sev = (v.get("Severity") or "").upper()
            sev_map[sev] = sev_map.get(sev, 0) + 1
    # pick most frequent severity label
    top = "-"
    if sev_map:
        top = max(sev_map.items(), key=lambda kv: kv[1])[0].title()  # e.g., Medium
    return total, top


def count_zap() -> int:
    """Crude: count 'alert' strings in the HTML (baseline default file)."""
    if not ZAP_HTML.exists():
        return 0
    try:
        t = ZAP_HTML.read_text(encoding="utf-8", errors="ignore").lower()
        return t.count("alert")
    except Exception:
        return 0


def best_tool(tools_from_insights: Dict[str, int]) -> Tuple[str, str]:
    """
    Decide which tool has the most findings.
    Returns (tool_name, detail_text).
    If insights lacks per-tool counts, fall back to raw reports.
    """
    tools = dict(tools_from_insights) if tools_from_insights else {}

    # Fallbacks to raw reports if missing
    if "bandit" not in tools:
        tools["bandit"] = count_bandit()
    if "semgrep" not in tools:
        tools["semgrep"] = count_semgrep()
    if "pip-audit" not in tools:
        tools["pip-audit"] = count_pip_audit()
    if "trivy" not in tools:
        trivy_total, _ = count_trivy()
        tools["trivy"] = trivy_total
    if "zap" not in tools and ZAP_HTML.exists():
        tools["zap"] = count_zap()

    if not tools:
        return ("-", "-")

    # pick max
    tool = max(tools.items(), key=lambda kv: kv[1])[0]
    detail = f"{tools[tool]} findings"

    # If trivy wins, add top severity hint
    if tool == "trivy":
        ttotal, top = count_trivy()
        if ttotal:
            detail = f"{ttotal} {top}"

    return (tool, detail)


def category_for_tool(tool: str) -> str:
    tool = (tool or "").lower()
    if tool == "trivy":
        return "Outdated Dependencies / Container CVEs"
    if tool in ("pip-audit", "scascan", "dependency-check"):
        return "Outdated Dependencies"
    if tool in ("bandit", "semgrep"):
        return "Static Code Issues"
    if tool == "zap":
        return "Runtime / DAST Alerts"
    return "General Security"


def notify_slack():
    if not WEBHOOK:
        print("[ERROR] SLACK_WEBHOOK_URL not set.")
        return

    # posture score + delta
    i = from_insights()
    score = i.get("score")
    delta = i.get("delta", 0.0)
    delta_str = f"{delta:+g}" if isinstance(delta, (int, float)) else "0"

    # most findings tool
    tool, detail = best_tool(i.get("tools") or {})
    category = category_for_tool(tool)

    # high/critical legacy (optional)
    critical, high = summarize_high_crit()

    # Colour by posture
    color = (
        "#2ECC71"
        if (isinstance(score, (int, float)) and score >= 85)
        else "#F59E0B"
        if isinstance(score, (int, float)) and score >= 70
        else "#E74C3C"
    )

    lines = []
    if isinstance(score, (int, float)):
        lines.append(
            f"📊 *Security Posture:* {round(score)} / 100 ({delta_str} from last run)"
        )
    else:
        lines.append("📊 *Security Posture:* N/A")

    if tool != "-":
        lines.append(f"🧩 *Most Findings Tool:* {tool.title()} ({detail})")
        lines.append(f"🔍 *Top Category:* {category}")

    # Keep previous signal (optional)
    if (critical + high) > 0:
        lines.append(f"⚠️ *High/Critical Findings:* {critical + high}")

    payload = {
        "attachments": [
            {
                "fallback": "Security posture summary",
                "color": color,
                "title": "VulnFlask-SecureCI — Security Summary",
                "text": "\n".join(lines),
                "footer": "GitHub Actions · Observability",
                "ts": int(datetime.utcnow().timestamp()),
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
    notify_slack()
