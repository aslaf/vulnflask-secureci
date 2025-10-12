#!/usr/bin/env python3
"""
Vulnerability Aggregation & Triage
-----------------------------------
Aggregates results from multiple scanners and produces:

  - triage-summary.md   : human-readable summary table
  - triage-summary.json : machine-readable severity counts
  - triage-high.md      : list of high/critical findings (for GitHub Issues)

This script is resilient — it will always create output files,
even if no scan results are available.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

# Input artifact paths (these may or may not exist)
P_BANDIT = ROOT / "bandit-report.json"
P_SEMGREP = ROOT / "semgrep-report.json"
P_PIP = ROOT / "pip-audit-report.json"
P_TRIVY = ROOT / "trivy-report.json"
P_ZAP_HTML = ROOT / "report_html.html"

# Outputs
OUT_MD = ROOT / "triage-summary.md"
OUT_JSON = ROOT / "triage-summary.json"
OUT_HIGHS = ROOT / "triage-high.md"

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
ToolSummary = Dict[str, Dict[str, int]]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def load_json(path: Path) -> Optional[dict]:
    """Load a JSON file if present."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def norm_sev(raw: str) -> str:
    """Normalize severity names across tools."""
    if not raw:
        return "MEDIUM"
    r = raw.strip().upper()
    if r in SEVERITY_ORDER:
        return r
    return {
        "ERROR": "CRITICAL",
        "BLOCKER": "CRITICAL",
        "MAJOR": "HIGH",
        "WARNING": "MEDIUM",
        "WARN": "MEDIUM",
        "MINOR": "LOW",
        "INFO": "INFO",
        "INFORMATIONAL": "INFO",
    }.get(r, "MEDIUM")


def add_count(summary: ToolSummary, tool: str, sev: str):
    summary.setdefault(tool, {})
    summary[tool][sev] = summary[tool].get(sev, 0) + 1


# ---------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------
def summarize_bandit(path: Path, summary: ToolSummary, top: List[str]):
    data = load_json(path)
    if not data:
        return
    for item in data.get("results", []):
        sev = norm_sev(item.get("issue_severity"))
        add_count(summary, "Bandit", sev)
        if sev in ("CRITICAL", "HIGH"):
            top.append(
                f"[Bandit] {item.get('test_id', '')}: {item.get('issue_text', '').strip()}"
            )


def summarize_semgrep(path: Path, summary: ToolSummary, top: List[str]):
    data = load_json(path)
    if not data:
        return
    for item in data.get("results", []):
        sev = norm_sev(item.get("extra", {}).get("severity"))
        add_count(summary, "Semgrep", sev)
        if sev in ("CRITICAL", "HIGH"):
            top.append(
                f"[Semgrep] {item.get('check_id', '')}: {item.get('extra', {}).get('message', '')}"
            )


def summarize_pip_audit(path: Path, summary: ToolSummary, top: List[str]):
    data = load_json(path)
    if not data:
        return

    def handle_vuln(v):
        sev = norm_sev(v.get("severity") or v.get("severity_name", "MEDIUM"))
        add_count(summary, "pip-audit", sev)
        if sev in ("CRITICAL", "HIGH"):
            top.append(
                f"[pip-audit] {v.get('id', 'VULN')}: {v.get('advisory', '').strip()}"
            )

    if isinstance(data, dict) and "dependencies" in data:
        for dep in data["dependencies"]:
            for v in dep.get("vulns") or dep.get("vulnerabilities") or []:
                handle_vuln(v)
    elif isinstance(data, list):
        for dep in data:
            for v in dep.get("vulns", []):
                handle_vuln(v)


def summarize_trivy(path: Path, summary: ToolSummary, top: List[str]):
    data = load_json(path)
    if not data:
        return
    for result in data.get("Results", []):
        for v in result.get("Vulnerabilities") or []:
            sev = norm_sev(v.get("Severity"))
            add_count(summary, "Trivy", sev)
            if sev in ("CRITICAL", "HIGH"):
                top.append(
                    f"[Trivy] {v.get('VulnerabilityID', '')} in {v.get('PkgName', '')}"
                )


def summarize_zap_html(path: Path, summary: ToolSummary, top: List[str]):
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8", errors="ignore").upper()
        crit = len(re.findall(r"RISK LEVEL:\s*HIGH", content))
        med = len(re.findall(r"RISK LEVEL:\s*MEDIUM", content))
        low = len(re.findall(r"RISK LEVEL:\s*LOW", content))
        if crit:
            add_count(summary, "ZAP", "HIGH")
        if med:
            add_count(summary, "ZAP", "MEDIUM")
        if low:
            add_count(summary, "ZAP", "LOW")
    except Exception:
        pass


# ---------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------
def totals(summary: ToolSummary) -> Dict[str, int]:
    agg = {k: 0 for k in SEVERITY_ORDER}
    for tool, counts in summary.items():
        for sev, n in counts.items():
            agg[sev] = agg.get(sev, 0) + n
    return agg


def write_outputs(summary: ToolSummary, top: List[str]):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Markdown summary
    lines = [
        "# Security Triage Summary",
        f"**Generated:** {ts}",
        "",
        "| Tool | CRITICAL | HIGH | MEDIUM | LOW | INFO |",
        "|------|----------|------|--------|-----|------|",
    ]
    for tool in sorted(summary.keys()):
        row = [tool] + [str(summary[tool].get(sev, 0)) for sev in SEVERITY_ORDER]
        lines.append("| " + " | ".join(row) + " |")

    # Totals
    t = totals(summary)
    lines += [
        "",
        "## Totals",
        *(f"- {sev}: **{t[sev]}**" for sev in SEVERITY_ORDER),
        "",
        "## High-Risk Highlights",
    ]
    lines += [f"- {item}" for item in top[:20]] or ["- No HIGH/CRITICAL items found."]

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    OUT_JSON.write_text(
        json.dumps(
            {k.lower(): v for k, v in t.items()},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    if top:
        OUT_HIGHS.write_text(
            "# High/Critical Findings\n\n"
            + "\n".join(f"- {x}" for x in top[:50])
            + "\n",
            encoding="utf-8",
        )
    else:
        OUT_HIGHS.write_text("# High/Critical Findings\n\n- None\n", encoding="utf-8")

    print(f"[OK] Wrote: {OUT_MD}")
    print(f"[OK] Wrote: {OUT_JSON}")
    print(f"[OK] Wrote: {OUT_HIGHS}")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main() -> None:
    summary: ToolSummary = {}
    top: List[str] = []

    summarize_bandit(P_BANDIT, summary, top)
    summarize_semgrep(P_SEMGREP, summary, top)
    summarize_pip_audit(P_PIP, summary, top)
    summarize_trivy(P_TRIVY, summary, top)
    summarize_zap_html(P_ZAP_HTML, summary, top)

    for tool in ["Bandit", "Semgrep", "pip-audit", "Trivy", "ZAP"]:
        summary.setdefault(tool, {})

    try:
        write_outputs(summary, top)
    except Exception as e:
        print(f"[ERROR] Could not write triage outputs: {e}")
        for f in [OUT_MD, OUT_JSON, OUT_HIGHS]:
            f.write_text(
                "# Placeholder\nNo findings or data to summarize.\n", encoding="utf-8"
            )
        print("[WARN] Created placeholder triage summary files.")


if __name__ == "__main__":
    main()
