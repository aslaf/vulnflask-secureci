#!/usr/bin/env python3
import json
import os
from datetime import datetime
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # resolved in CI install step


ROOT = Path(__file__).resolve().parent.parent


def load_json(p: Path):
    try:
        if p.exists():
            with p.open() as f:
                return json.load(f)
    except Exception:
        return None
    return None


def load_yaml(p: Path):
    if not yaml or not p.exists():
        return None
    try:
        with p.open() as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def summarize_bandit(obj):
    out = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    if not obj:
        return out, "bandit-report.json (not found)"
    for r in obj.get("results", []):
        sev = str(r.get("issue_severity", "")).upper()
        if sev in out:
            out[sev] += 1
    return out, "bandit-report.json"


def summarize_semgrep(obj):
    out = {"INFO": 0, "WARNING": 0, "ERROR": 0}
    if not obj:
        return out, "semgrep-report.json (not found)"
    for r in obj.get("results", []):
        sev = str(r.get("extra", {}).get("severity", "")).upper()
        if sev in out:
            out[sev] += 1
    return out, "semgrep-report.json"


def summarize_pip_audit(obj):
    # pip-audit JSON is typically a list of packages with "vulns"
    total = 0
    if obj is None:
        src = "pip-audit-report.json (not found)"
        return {"total_vulns": total}, src
    try:
        for pkg in obj:
            vulns = pkg.get("vulns", []) or []
            total += len(vulns)
    except Exception:
        # some versions emit {"dependencies":[],"vulnerabilities":[]}
        vulns = obj.get("vulnerabilities", []) if isinstance(obj, dict) else []
        total = len(vulns)
    return {"total_vulns": total}, "pip-audit-report.json"


def summarize_trivy(obj):
    # Trivy JSON: {"Results":[{"Vulnerabilities":[{"Severity":"CRITICAL"}, ...]}]}
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    if obj is None:
        return counts, "trivy-report.json (not found)"
    for res in obj.get("Results", []):
        for v in res.get("Vulnerabilities", []) or []:
            sev = str(v.get("Severity", "")).upper()
            if sev in counts:
                counts[sev] += 1
    return counts, "trivy-report.json"


def summarize_threats(obj):
    # threat_model/threats.yml: list of {id, title, risk, status}
    open_high = 0
    open_critical = 0
    items = []
    if not obj:
        return {
            "open_high": 0,
            "open_critical": 0,
            "items": [],
        }, "threats.yml (not found)"
    for t in obj or []:
        risk = str(t.get("risk", "")).strip().upper()
        status = str(t.get("status", "")).strip().upper()
        if status == "OPEN" and risk in {"HIGH", "CRITICAL"}:
            if risk == "HIGH":
                open_high += 1
            else:
                open_critical += 1
            items.append(
                f"- [{t.get('id')}] {t.get('title')} (Risk: {risk}) – **{status}**"
            )
    return {
        "open_high": open_high,
        "open_critical": open_critical,
        "items": items,
    }, "threats.yml"


def section(title: str, body: str) -> str:
    return f"## {title}\n\n{body}\n"


def main():
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    bandit_obj = load_json(ROOT / "bandit-report.json")
    semgrep_obj = load_json(ROOT / "semgrep-report.json")
    pip_obj = load_json(ROOT / "pip-audit-report.json")
    trivy_obj = load_json(ROOT / "trivy-report.json")
    threats_obj = load_yaml(ROOT / "threat_model" / "threats.yml")

    bandit, b_src = summarize_bandit(bandit_obj)
    semgrep, s_src = summarize_semgrep(semgrep_obj)
    pip_sum, p_src = summarize_pip_audit(pip_obj)
    trivy, t_src = summarize_trivy(trivy_obj)
    threats, th_src = summarize_threats(threats_obj)

    md = []
    md.append(f"# Security Summary\nGenerated: **{ts}**\n")

    # Threat model
    th_lines = [
        f"- Source: `{th_src}`",
        f"- Open **Critical**: **{threats['open_critical']}**",
        f"- Open **High**: **{threats['open_high']}**",
    ]
    if threats["items"]:
        th_lines.append(
            "\n**Open High/Critical Items:**\n" + "\n".join(threats["items"])
        )
    md.append(section("Threat Model", "\n".join(th_lines)))

    # SAST
    md.append(
        section(
            "SAST (Bandit & Semgrep)",
            "\n".join(
                [
                    f"**Bandit** `{b_src}` → HIGH: **{bandit['HIGH']}**, MED: **{bandit['MEDIUM']}**, "
                    f"LOW: **{bandit['LOW']}**",
                    f"**Semgrep** `{s_src}` → ERROR: **{semgrep['ERROR']}**, WARNING: **{semgrep['WARNING']}**, "
                    f"INFO: **{semgrep['INFO']}**",
                ]
            ),
        )
    )

    # SCA
    md.append(
        section(
            "Dependencies (SCA - pip-audit)",
            f"`{p_src}` → total vulnerable findings: **{pip_sum['total_vulns']}**",
        )
    )

    # Container
    md.append(
        section(
            "Container (Trivy)",
            f"`{t_src}` → CRITICAL: **{trivy['CRITICAL']}**, HIGH: **{trivy['HIGH']}**, "
            f"MEDIUM: **{trivy['MEDIUM']}**, LOW: **{trivy['LOW']}**",
        )
    )

    # Notes
    md.append(
        section(
            "Notes",
            "- Values are best-effort if reports were not produced in this workflow.\n"
            "- Empty or missing files are reported as “(not found)”.\n"
            "- Treat this report as a governance view; gates remain in their own workflows.",
        )
    )

    out = "\n".join(md).strip() + "\n"
    (ROOT / "security_summary.md").write_text(out, encoding="utf-8")

    # Also show the top of the report in the job summary
    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        with open(gh_summary, "a", encoding="utf-8") as f:
            f.write("# Security Summary (excerpt)\n")
            f.write(out.split("## SAST", 1)[0])  # show header + Threat Model section


if __name__ == "__main__":
    main()
