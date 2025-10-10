#!/usr/bin/env python3
"""
aggregate_insights.py
Day 16 — Aggregates scan outputs + computes a Security Posture Score.

Inputs (if present at repo root):
  - bandit-report.json
  - semgrep-report.json
  - pip-audit-report.json
  - trivy-report.json
(Other files are ignored when missing; counts become zero.)

Output:
  - insights.json
    {
      "generated": "2025-10-10T01:23:45.678901Z",
      "counts": {"critical": 0, "high": 0, "medium": 2, "low": 5, "info": 0},
      "score": 92,
      "grade": "Good",
      "by_tool": {
        "bandit": {...},
        "semgrep": {...},
        "pip_audit": {...},
        "trivy": {...}
      },
      "history": [{"ts": "...", "score": 88}, ...]  # last 30 scores
    }
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSIGHTS = ROOT / "insights.json"


# -----------------------------
# Helpers
# -----------------------------
def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _blank_counts():
    return {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}


def _add(d, sev, n=1):
    sev = sev.lower()
    if sev in d:
        d[sev] += n


# -----------------------------
# Per-tool parsers → severity counts
# -----------------------------
def counts_from_bandit(report) -> dict:
    c = _blank_counts()
    if not report:
        return c
    # bandit: results[].issue_severity in {"LOW","MEDIUM","HIGH"}
    for r in report.get("results", []):
        sev = (r.get("issue_severity") or "").upper()
        if sev == "HIGH":
            _add(c, "high")
        elif sev == "MEDIUM":
            _add(c, "medium")
        elif sev == "LOW":
            _add(c, "low")
    return c


def counts_from_semgrep(report) -> dict:
    c = _blank_counts()
    if not report:
        return c
    # semgrep: results[].extra.severity or results[].severity → {"ERROR","WARNING","INFO"}
    for r in report.get("results", []):
        sev = (
            (r.get("extra", {}) or {}).get("severity") or r.get("severity") or ""
        ).upper()
        if sev == "ERROR":
            _add(c, "high")
        elif sev == "WARNING":
            _add(c, "medium")
        elif sev == "INFO":
            _add(c, "low")
    return c


def counts_from_pip_audit(report) -> dict:
    c = _blank_counts()
    if not report:
        return c

    # two shapes: list[...] (older) or {"dependencies":[{"vulns":[...]}]}
    def bump(sev: str | None):
        if not sev:
            _add(c, "medium")  # fallback if severity isn’t present
            return
        sev = sev.upper()
        if sev == "CRITICAL":
            _add(c, "critical")
        elif sev == "HIGH":
            _add(c, "high")
        elif sev == "MEDIUM":
            _add(c, "medium")
        elif sev == "LOW":
            _add(c, "low")
        else:
            _add(c, "medium")

    if isinstance(report, dict) and "dependencies" in report:
        for dep in report["dependencies"]:
            for v in dep.get("vulns", []) or dep.get("vulnerabilities", []) or []:
                bump(v.get("severity"))
    elif isinstance(report, list):
        for dep in report:
            for v in dep.get("vulns", []) or dep.get("vulnerabilities", []) or []:
                bump(v.get("severity"))
    return c


def counts_from_trivy(report) -> dict:
    c = _blank_counts()
    if not report:
        return c
    # trivy: Results[].Vulnerabilities[].Severity in {"CRITICAL","HIGH","MEDIUM","LOW","UNKNOWN"}
    for res in report.get("Results", []) or []:
        for v in res.get("Vulnerabilities", []) or []:
            sev = (v.get("Severity") or "").upper()
            if sev == "CRITICAL":
                _add(c, "critical")
            elif sev == "HIGH":
                _add(c, "high")
            elif sev == "MEDIUM":
                _add(c, "medium")
            elif sev == "LOW":
                _add(c, "low")
            else:
                _add(c, "info")
    return c


# -----------------------------
# Score
# -----------------------------
def compute_score(total_counts: dict) -> tuple[int, str]:
    """
    Weighted 0–100 score (higher is better).
    Tunable weights:
      CRIT 15, HIGH 10, MED 3, LOW 1 (INFO 0)
    """
    base = 100
    penalty = (
        total_counts["critical"] * 15
        + total_counts["high"] * 10
        + total_counts["medium"] * 3
        + total_counts["low"] * 1
    )
    score = max(0, base - penalty)

    if score >= 90:
        grade = "Excellent"
    elif score >= 75:
        grade = "Good"
    elif score >= 50:
        grade = "Needs Attention"
    else:
        grade = "Poor"

    return score, grade


# -----------------------------
# History merge (keeps last 30)
# -----------------------------
def merge_history(existing, new_score):
    history = []
    if isinstance(existing, dict):
        history = existing.get("history", [])
    history.append({"ts": datetime.now(timezone.utc).isoformat(), "score": new_score})
    return history[-30:]


# -----------------------------
# Main
# -----------------------------
def main():
    bandit = _load_json(ROOT / "bandit-report.json")
    semgrep = _load_json(ROOT / "semgrep-report.json")
    pip_audit = _load_json(ROOT / "pip-audit-report.json")
    trivy = _load_json(ROOT / "trivy-report.json")

    by_tool = {
        "bandit": counts_from_bandit(bandit),
        "semgrep": counts_from_semgrep(semgrep),
        "pip_audit": counts_from_pip_audit(pip_audit),
        "trivy": counts_from_trivy(trivy),
    }

    # totalize
    totals = _blank_counts()
    for tool_counts in by_tool.values():
        for k, v in tool_counts.items():
            totals[k] += v

    score, grade = compute_score(totals)

    existing = _load_json(INSIGHTS) or {}
    out = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "counts": totals,
        "score": score,
        "grade": grade,
        "by_tool": by_tool,
        "history": merge_history(existing, score),
    }

    INSIGHTS.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[✓] Wrote {INSIGHTS}")
    print(f"[i] totals={totals}  score={score}  grade={grade}")


if __name__ == "__main__":
    main()
