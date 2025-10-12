# VulnFlask-SecureCI (v2-dev branch)
# VulnFlask-SecureCI
### A Full DevSecOps Pipeline for a Vulnerable Flask E-commerce App

VulnFlask-SecureCI is a 10-day project that transforms an intentionally vulnerable Flask e-commerce application into a **secure-by-design CI/CD pipeline.**
It automates every layer of security — from threat modeling to runtime policies — and demonstrates how real-world DevSecOps can continuously prevent, detect, and respond to risks.

## Project Overview

| Phase | Focus | Deliverable | Status |
|-----|--------|-------------|--------|
| 1 | Flask App + OWASP Top 10 vulns | Vulnerable app running locally | **Completed** |
| 2A | Code Quality + Base CI | Linting, formatting, testing CI | **Completed** |
| 2B | Threat Model & Validation CI | STRIDE model enforcement via GitHub Actions | **Completed** |
| 3 | SAST + SCA + Secrets CI | Automated static & dependency scanning | **Completed** |
| 4 | Container + SBOM | Secure containerization | **Completed** |
| 5 | IaC Scanning | Terraform + Checkov | **Completed** |
| 6 | CI/CD Deploy | AWS EKS / local k3d staging | **Completed** |
| 7 | DAST | OWASP ZAP | **Completed** |
| 8 | IAST | Runtime instrumentation | **Completed** |
| 9 | Runtime Policies | Falco + OPA Gatekeeper | **Completed** |
| 10 | Wrap-Up | Governance report | **Completed** |

---
## Architecture

The **VulnFlask-SecureCI** project demonstrates a secure-by-default DevSecOps pipeline around an intentionally vulnerable Flask web app.
It integrates multiple security layers — from threat modeling to runtime enforcement — using open-source tools orchestrated via GitHub Actions.


---

## Key Learnings

- Security as Code: Every control (threat, scan, or policy) codified in CI/CD
- Shift-Left + Shift-Right: Continuous scanning before & after deployment
- Risk-Driven Decisions: High/Critical threats block merges automatically
- Compliance Mapping: Results align with OWASP ASVS & NIST CSF functions
- Automation > Awareness: Minimal manual steps, fully auditable pipeline

---

## Security Coverage Matrix

| Layer | Focus | Tool | CI Behavior |
|--------|--------|------|-------------|
| Threat Modeling | STRIDE validation | Custom Python | Blocks merge on open High/Critical |
| SAST | Static code flaws | Bandit / Semgrep | Non-blocking (demo) |
| SCA | Dependency vulnerabilities | pip-audit | Non-blocking (demo) |
| Secrets | Hard-coded credentials | Gitleaks | Fails if secrets found |
| Container | Image CVEs & SBOM | Trivy / Syft | Blocks on Critical CVEs |
| IaC | Terraform drift/config validation | Checkov | Reports only |
| DAST | Runtime web testing | OWASP ZAP | Generates HTML reports |
| IAST | Runtime behavior monitoring | Python mock logger | Artifact upload |
| Runtime | System & container policies | Falco / OPA Gatekeeper | Enforces privilege limits |

---

## Repository Highlights

<pre>
.github/workflows/
├── threat-validate.yml
├── code-security.yml
├── container-security.yml
├── iac-scan.yml
├── dast-scan.yml
├── dast-live.yml
├── runtime-policies.yml
└── deploy.yml

infra/kubernetes/
├── deployment.yml
├── service.yml
└── policies/
    ├── constraint-template.yaml
    └── deny-privileged.yaml

ops/runtime/
└── rules.yaml
</pre>

---

## Repository Detailed

<pre>
.github/workflows/
├── threat-validate.yml          → Validates STRIDE threat model during CI.
├── code-security.yml            → Runs Bandit, Semgrep, pip-audit, and Gitleaks scans.
├── container-security.yml       → Generates SBOM (Syft) and scans Docker image with Trivy.
├── iac-scan.yml                 → Scans Terraform code for misconfigurations using Checkov.
├── dast-scan.yml                → Runs OWASP ZAP baseline scan locally (containerized target).
├── dast-live.yml                → Executes OWASP ZAP scan against live deployment (Render/Fly.io).
├── runtime-policies.yml         → Monitors and enforces runtime behavior (Falco + OPA Gatekeeper).
└── deploy.yml                   → Builds and deploys Docker image to local K3d or cloud environment.

infra/kubernetes/
├── deployment.yml               → Defines Flask app deployment (replica, container image, ports).
├── service.yml                  → Exposes the app internally via LoadBalancer or NodePort.
└── policies/
    ├── constraint-template.yaml → Gatekeeper ConstraintTemplate for privileged container policy.
    └── deny-privileged.yaml     → OPA constraint denying privileged pods.

ops/runtime/
└── rules.yaml                   → Custom Falco runtime detection rules (shell access, execs, etc).

src/
├── app.py                       → Vulnerable Flask web app (SQLi, XSS, access control flaws).
├── templates/                   → HTML templates (intentionally unsafe rendering).
└── data.db                      → Auto-generated SQLite database for demo purposes.

infra/terraform/
└── main.tf                      → Terraform IaC provisioning sample (S3 + VPC + Subnets).

tests/
└── test_app.py                  → Unit tests for base Flask functionality.

threat_model/
├── threats.yml                  → STRIDE-mapped threat register for validation in CI.
└── validate_threats.py          → Python validation script enforcing “no open High/Critical” risks.

SBOM & Reports/
├── syft-sbom.json               → Software Bill of Materials generated by Syft.
├── trivy-report.json            → Container vulnerability report.
└── zap-report.html              → DAST findings summary (artifact uploaded via CI).

venv/                            → Local Python virtual environment (excluded from CI).
README.md                        → Project documentation and setup guide.
requirements.txt                 → Python dependencies for app and scans.
Dockerfile                       → Container definition for vulnerable Flask app.
</pre>

---

## Governance Summary

All security results are stored as GitHub Artifacts:
	•	bandit-report.json, semgrep-report.json, pip-audit.json
	•	trivy-report.json, sbom.spdx.json, zap-report.html, iast-runtime.log

This enables traceable, auditable evidence of each security control — suitable for SOC 2 / ISO 27001 mappings.

---

## Live Preview

Hosted via **Render**:
🔗 https://vulnflask-secureci.onrender.com

(Note: intentionally vulnerable; for demonstration only.)

---

## Author

**Aslaf Shaikh** — Security Engineer | DevSecOps | AppSec
📍 Toronto, Canada
🔗 github.com/aslaf | 🔗 linkedin.com/in/aslafshaikh

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
© 2025 Aslaf Shaikh
