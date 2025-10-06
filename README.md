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

---

## Keywords
**AppSec**, **DevSecOps**, **SSDLC**, **Threat Modeling**, **CI/CD Security**,  
**SAST**, **DAST**, **IAST**, **SCA**, **IaC Security**, **Policy-as-Code**, **Cloud Security**

---

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).  
© 2025 Aslaf Shaikh
