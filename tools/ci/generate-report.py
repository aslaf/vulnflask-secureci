#!/usr/bin/env python3
"""
generate-report.py
-----------------------------------
Day 11 – Governance Reporting Workflow
Generates a consolidated summary of all security scans and saves it
as 'security-report.md' for artifact upload.
"""

import datetime
import os

# -------------------------------------------------------------------
# 1️Define mock data (replace with real scan outputs later)
# -------------------------------------------------------------------
summary = {
    "Bandit (SAST)": {"status": "Passed", "findings": 0},
    "Semgrep (Code Analysis)": {"status": "Passed", "findings": 0},
    "pip-audit (Dependency SCA)": {"status": "Warnings", "findings": 2},
    "TruffleHog (Secrets Scan)": {"status": "Passed", "findings": 0},
    "OWASP ZAP (DAST)": {"status": "Passed", "findings": 0},
    "Checkov (IaC Security)": {"status": "Passed", "findings": 0},
    "Grype (Container Vulnerability)": {"status": "Passed", "findings": 1},
}

# -------------------------------------------------------------------
# 2️Generate report content
# -------------------------------------------------------------------
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

report_lines = [
    "# VulnFlask-SecureCI — Security Summary Report",
    "",
    f"**Generated:** {timestamp}",
    "",
    "## Scan Summary",
    "| Tool | Status | Findings |",
    "|------|---------|-----------|",
]

for tool, data in summary.items():
    report_lines.append(f"| {tool} | {data['status']} | {data['findings']} |")

report_lines += [
    "",
    "## Observations",
    "- All pipelines executed successfully except minor dependency warnings.",
    "- No hardcoded secrets or high-severity vulnerabilities detected.",
    "- SBOM generation and IaC scans are compliant.",
    "",
    "## 🛠️ Next Steps",
    "1. Integrate this output into Day 12 dashboards.",
    "2. Auto-parse JSON from scan tools for real-time updates.",
    "3. Notify via Slack or Teams when high findings appear.",
    "",
    "_Report generated automatically by SecureCI governance pipeline._",
]

# -------------------------------------------------------------------
# 3 Write to file
# -------------------------------------------------------------------
output_file = "security-report.md"
with open(output_file, "w") as f:
    f.write("\n".join(report_lines))

# -------------------------------------------------------------------
# 4️Confirmation log
# -------------------------------------------------------------------
print("[INFO] Security report generated successfully → " + os.path.abspath(output_file))
