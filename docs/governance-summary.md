## Governance & Security Coverage

VulnFlask-SecureCI demonstrates a full DevSecOps pipeline that automates security from code to runtime:

| Layer | Security Focus | Tools | CI/CD Enforcement |
|-------|----------------|--------|--------------------|
| **1. Threat Modeling** | STRIDE validation | Custom Python validator | Blocks merge if High/Critical threats open |
| **2. SAST / SCA / Secrets** | Code, dependency, secret scanning | Bandit, Semgrep, pip-audit, Gitleaks | Non-blocking but reports uploaded |
| **3. Container & SBOM** | Image & SBOM generation | Trivy, Syft | Fails build on Critical CVEs |
| **4. IaC Scanning** | Terraform misconfig detection | Checkov | Non-blocking for demo |
| **5. DAST** | Runtime attack surface | OWASP ZAP (local + live) | Generates HTML reports |
| **6. IAST** | Instrumented runtime checks | Mock logger | Reports to artifact store |
| **7. Runtime Monitoring** | Host-level behavior | Falco, OPA Gatekeeper | Detects shell/privilege escalations |
| **8. Governance & Reporting** | Audit & risk visibility | GitHub Actions Artifacts + SBOMs | Centralized evidence collection |
