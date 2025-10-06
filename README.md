# VulnFlask-SecureCI  
**End-to-End DevSecOps Pipeline for a Vulnerable Flask Application**

---

## Overview
VulnFlask-SecureCI is a **real-world DevSecOps learning project** that demonstrates how to embed security across the entire software development lifecycle (SSDLC).  
It starts from a vulnerable Flask web application and evolves into a **secure CI/CD pipeline** that automatically detects, prevents, and governs security risks — from code to cloud.

---

## Objectives
- Build an intentionally vulnerable web app (OWASP Top 10) to simulate common attack surfaces.  
- Integrate **security automation** (linting, testing, threat modeling, SAST, SCA, DAST, IAST, runtime).  
- Enforce **policy-as-code** and **risk-based governance** in the CI/CD pipeline.  
- Achieve end-to-end visibility of security posture in every stage.

---

## Project Structure
vulnflask-secureci/
├── app/                      # Vulnerable Flask application
├── tests/                    # Unit tests (pytest, mocking)
├── threat_model/             # STRIDE-based risk register + validator
├── .github/workflows/        # CI/CD workflows (Build, Threat Validation)
├── .pre-commit-config.yaml   # Local lint + format hooks
├── requirements.txt
└── README.md
---

## Implemented Stages

| **Tasks** | **Focus** | **Deliverable** | **Key Tools / Features** |
|----------|------------|------------------|---------------------------|
| **1** | Flask App + OWASP Top 10 | Vulnerable app running locally | Flask, Jinja2, HTML templates |
| **2A** | Code Quality + Base CI | Lint, format, test pipeline | Black, isort, flake8, pytest, pre-commit |
| **2B** | Threat Modeling + Validation CI | STRIDE threat register + risk gate | PyYAML, GitHub Actions |
| **3** | SAST + SCA + Secrets CI | Static & dependency scanning | Bandit, Trivy, Gitleaks |
| **4** | Container Security | SBOM + image scanning | Docker, Syft, Trivy |
| **5** | IaC Scanning | Terraform security checks | Checkov, tfsec |
| **6** | CI/CD Deploy | Secure deploy to AWS EKS | GitHub Actions, EKS, Terraform |
| **7** | DAST | Dynamic scanning | OWASP ZAP |
| **8** | IAST | Runtime instrumentation | PyT or Contrast |
| **9** | Runtime Policies | Behavioral detection | Falco, OPA Gatekeeper |
| **10** | Wrap-Up | Governance report + LinkedIn summary | Markdown report + badges |

---

## Security Highlights
- **SSDLC enforcement**: security built into every stage  
- **Threat modeling (STRIDE)** integrated as CI gate  
- **Pre-commit automation** for code hygiene  
- **SAST, SCA, DAST, IaC, Runtime** controls  
- **Cloud-native security** (AWS EKS + Terraform)  
- **Policy-as-Code**: automated risk validation before merge  

# VulnFlask-SecureCI
### A Full DevSecOps Pipeline for a Vulnerable Flask E-commerce App

VulnFlask-SecureCI is an educational project that demonstrates how to build a secure, automated CI/CD pipeline around an intentionally vulnerable Python Flask application.
The goal is to learn Application Security (AppSec), DevSecOps, and Threat Modeling by integrating real-world security tooling — from SAST and SCA to DAST, IAST, and runtime policy enforcement.

---

## Key Learning Areas

- Threat modeling with STRIDE and automated gating (`threats.yml`)
- SAST (Semgrep, Bandit) and dependency scanning (pip-audit)
- Container scanning with Trivy & SBOM generation (Syft)
- IaC scanning using Checkov for Terraform
- DAST with OWASP ZAP (baseline & active)
- IAST-style runtime instrumentation
- Secure Kubernetes deployments & policy controls (OPA Gatekeeper, Falco)

---

## Project Structure

**Directory layout:**

- **`app/`** – Vulnerable Flask application
  - `app.py` – Main application file (intentionally vulnerable)
  - `templates/` – Jinja2 templates (index, login, admin, etc.)

- **`tests/`** – Unit tests and fixtures
  - `test_basic.py` – Basic route and mock tests
  - `conftest.py` – Pytest configuration

- **`threat_model/`** – STRIDE threat model and validation logic
  - `threats.yml` – Risk register of threats
  - `validate_threats.py` – CI script to enforce threat mitigations

- **`.github/workflows/`** – CI/CD pipelines
  - `threat-validate.yml` – Threat validation workflow

- `.pre-commit-config.yaml` – Linting and code formatting hooks
- `requirements.txt` – Python dependencies
- `README.md` – Project documentation

---

## Roadmap

| Day | Focus | Deliverable | Status |
|-----|--------|-------------|--------|
| 1 | Flask App + OWASP Top 10 vulns | Vulnerable app running locally | **Completed** |
| 2A | Code Quality + Base CI | Linting, formatting, testing CI | **Completed** |
| 2B | Threat Model & Validation CI | STRIDE model enforcement via GitHub Actions | **Completed** |
| 3 | SAST + SCA + Secrets CI | Automated static & dependency scanning | Pending |
| 4 | Container + SBOM | Secure containerization | Pending |
| 5 | IaC Scanning | Terraform + Checkov | Pending |
| 6 | CI/CD Deploy | AWS EKS / local k3d staging | Pending |
| 7 | DAST | OWASP ZAP | Pending |
| 8 | IAST | Runtime instrumentation | Pending |
| 9 | Runtime Policies | Falco + OPA Gatekeeper | Pending |
| 10 | Wrap-Up | Governance report + LinkedIn post | Pending |

---

## Tech Stack

**Languages / Frameworks:** Python, Flask
**Security Tools:** Bandit, Semgrep, Trivy, Syft, Checkov, OWASP ZAP, Falco, OPA
**Automation:** GitHub Actions, Pre-Commit, Pytest, Terraform
**Cloud / Containers:** Docker, AWS EKS, Kubernetes (k3d)

---

## Keywords

**AppSec**, **DevSecOps**, **SSDLC**, **Threat Modeling**, **CI/CD Security**,  
**SAST**, **DAST**, **IAST**, **SCA**, **IaC Security**, **Policy-as-Code**, **Cloud Security**


---

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). © 2025 Aslaf Shaikh
