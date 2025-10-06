# VulnFlask-SecureCI
### A Full DevSecOps Pipeline for a Vulnerable Flask E-commerce App

VulnFlask-SecureCI is an educational project that demonstrates how to build a **secure, automated CI/CD pipeline** around an intentionally vulnerable Python Flask application.
The goal is to learn **AppSec, DevSecOps, and threat modeling** by integrating real security tooling — from SAST and SCA to DAST, IAST, and runtime policy enforcement.

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

## Roadmap
| Day | Focus | Deliverable |
|-----|--------|-------------|
| 1 | Flask App + OWASP Top 10 vulns | Vulnerable app running locally |
| 2 | Threat Model & Validation CI | STRIDE model enforcement |
| 3 | SAST + SCA + Secrets CI | Automated code scanning |
| 4 | Container + SBOM | Secure containerization |
| 5 | IaC Scanning | Terraform + Checkov |
| 6 | CI/CD Deploy | AWS EKS / local k3d staging |
| 7 | DAST | OWASP ZAP |
| 8 | IAST | Runtime instrumentation |
| 9 | Runtime Policies | Falco + OPA Gatekeeper |
| 10 | Wrap-up | Governance + LinkedIn post |

---

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
© 2025 Aslaf Shaikh
