#!/usr/bin/env python3
"""
rename_repository_structure.py
--------------------------------
Normalizes and renames files/folders/workflow YAMLs in the repo
to industry-standard naming and updates references.

Dry-run by default. Use --apply to perform changes.
"""

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APPLY = False

# -------------------------------
# Folder and file rename mappings
# -------------------------------
FOLDER_MAP = {
    "app": "src",
    "scripts": "tools/ci",
    "iac": "infra/terraform",
    "k8s": "infra/kubernetes",
    "falco": "ops/runtime",
    "observability": "ops/observability",
    "ai-triage": "ops/triage",
    "dependency-track": "infra/dependency-track",
}

WORKFLOW_MAP = {
    "ci-build.yml": "build-lint-test.yml",
    "code-security.yml": "static-code-analysis.yml",
    "container-security.yml": "container-security-scan.yml",
    "iac-scan.yml": "infrastructure-security-scan.yml",
    "dast-scan.yml": "dast-owasp-zap.yml",
    "policy-validate.yml": "policy-compliance.yml",
    "feedback.yml": "pull-request-feedback.yml",
    "runtime-policies.yml": "runtime-policy.yml",
    "runtime-monitor.yml": "runtime-monitoring.yml",
    "deploy.yml": "secure-deployment.yml",
    "dashboard.yml": "security-dashboard.yml",
    "reporting.yml": "weekly-security-report.yml",
    "observability.yml": "observability-alerts.yml",
    "analytics.yml": "security-insights.yml",
    "triage.yml": "vulnerability-triage.yml",
    "threat-validate.yml": "threat-model-validation.yml",
}


def git_mv(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if APPLY:
        subprocess.run(["git", "mv", str(src), str(dst)], check=False)
    print(f"rename: {src.relative_to(REPO)} -> {dst.relative_to(REPO)}")


def replace_in_file(p: Path, replacements: list[tuple[str, str]]):
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return
    changed = text
    for old, new in replacements:
        changed = changed.replace(old, new)
    if APPLY and changed != text:
        p.write_text(changed, encoding="utf-8")


def safe_move_tree(mapping):
    for old, new in mapping.items():
        src = REPO / old
        dst = REPO / new
        if not src.exists():
            continue
        git_mv(src, dst)


def rename_workflows():
    wf_dir = REPO / ".github" / "workflows"
    for old, new in WORKFLOW_MAP.items():
        src, dst = wf_dir / old, wf_dir / new
        if not src.exists():
            continue
        git_mv(src, dst)


def replace_paths():
    # Path-level replacements (folder names in code/docs/CI)
    path_patterns = [
        ("src/", "src/"),
        ("infra/terraform/", "infra/terraform/"),
        ("infra/kubernetes/", "infra/kubernetes/"),
        ("ops/runtime/", "ops/runtime/"),
        ("ops/observability/", "ops/ops/observability/"),
        ("ops/triage/", "ops/triage/"),
        ("infra/dependency-track/", "infra/infra/dependency-track/"),
    ]
    for p in REPO.rglob("*"):
        if not p.is_file() or ".git" in str(p):
            continue
        if p.suffix.lower() in (
            ".py",
            ".yml",
            ".yaml",
            ".md",
            ".json",
            ".html",
            ".txt",
        ):
            replace_in_file(p, path_patterns)


def main():
    import argparse

    global APPLY
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply", action="store_true", help="Apply renames (default: dry run)"
    )
    args = parser.parse_args()
    APPLY = args.apply

    print(f"\n[INFO] Repository root: {REPO}")
    print(f"[INFO] Mode: {'APPLY' if APPLY else 'DRY-RUN'}")
    print("=" * 60)

    print("\n== Folder Renames ==")
    safe_move_tree(FOLDER_MAP)

    print("\n== Workflow File Renames ==")
    rename_workflows()

    print("\n== Updating Internal References ==")
    replace_paths()

    print("\n[INFO] Normalization Complete.")
    if not APPLY:
        print("Dry run only. Re-run with --apply to execute the changes.")


if __name__ == "__main__":
    main()
