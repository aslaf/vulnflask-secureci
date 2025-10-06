import sys

import yaml

with open("threat_model/threats.yml", "r") as f:
    data = yaml.safe_load(f)

open_threats = [
    t
    for t in data.get("threats", [])
    if t.get("status", "").lower() == "open"
    and t.get("risk", "").lower() in ("high", "critical")
]

if open_threats:
    print(
        "Validation failed: High/Critical threats still Open in threat_model/threats.yml\n"
    )
    for t in open_threats:
        print(f"- [{t['id']}] {t['title']} (Risk: {t['risk']}) – Status: {t['status']}")
    sys.exit(1)

print("Threat model validation passed: no open high/critical risks found.")
