from __future__ import annotations

from pathlib import Path
import json
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "NOTICE.md", "THIRD_PARTY_NOTICES.md", "LICENSE", ".env.example",
    ".gitignore", "pytest.ini", "docker-compose.yml", "collector/Dockerfile",
    "collector/requirements.txt", "collector/transit_collector/api_client.py",
    "cdc-service/Dockerfile", "cdc-service/pom.xml",
    "cdc-service/src/main/java/com/benpierce/transitcdc/Healthcheck.java",
    "cdc-service/src/test/java/com/benpierce/transitcdc/HealthStateTest.java",
    "mysql/init/001_schema.sh", "web/Dockerfile", "web/app.py", "web/serialization.py",
    "web/tests/test_app.py", "analysis/synthetic_trip_analysis.py",
    "data/fixtures/synthetic_vehicle_snapshot.json",
    "data/sample/synthetic_trip_observations.csv", "scripts/generate_synthetic_data.py",
    "scripts/validate_fresh_start.py", "scripts/write_manifest.py",
    ".github/workflows/fresh-start.yml", "tests/test_compose_config.py",
    "tests/test_web_assets.py", "tests/test_provenance.py",
    "tests/test_schema_consistency.py", "tests/test_web_serialization.py",
    "tests/test_runtime_validator.py", "tests/test_release_docs.py",
    "tests/test_secret_scan.py", "tests/test_fresh_start_validator.py",
    "tests/test_manifest.py",
    "tests/test_cdc_lifecycle_source.py", "docs/RELEASE_REVIEW.md",
    "docs/PROVENANCE.md", "docs/ATTRIBUTION.md", "docs/VALIDATION.md",
    "docs/PUBLICATION_CHECKLIST.md", "docs/RUN_FULL_STACK.md", "docs/architecture.svg",
]


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    with (ROOT / "docker-compose.yml").open(encoding="utf-8") as handle:
        compose = yaml.safe_load(handle)
    expected_services = {"mysql", "mongo", "collector", "cdc-service", "web"}
    actual_services = set(compose.get("services", {}))
    if expected_services != actual_services:
        raise SystemExit(f"Unexpected services: {actual_services}")

    mysql_health = " ".join(compose["services"]["mysql"]["healthcheck"]["test"])
    if "--protocol=TCP" not in mysql_health or "127.0.0.1" not in mysql_health or "-P 3306" not in mysql_health:
        raise SystemExit("MySQL health check must require the final TCP server on port 3306")

    cdc_health = compose["services"]["cdc-service"]["healthcheck"]["test"]
    cdc_health_text = " ".join(cdc_health)
    if "com.benpierce.transitcdc.Healthcheck" not in cdc_health_text or "/tmp/cdc-ready" in cdc_health_text:
        raise SystemExit("CDC health check must use the failure-aware HTTP health client")

    ET.parse(ROOT / "cdc-service" / "pom.xml")
    payload = json.loads((ROOT / "data" / "fixtures" / "synthetic_vehicle_snapshot.json").read_text())
    if payload.get("meta", {}).get("synthetic") is not True or len(payload.get("data", [])) != 7:
        raise SystemExit("Synthetic fixture is invalid")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_language = [
        "independently authored",
        "synthetic",
        "Massachusetts Department of Transportation",
        "OpenStreetMap contributors",
        "6,767-observation",
        "not the full runtime",
        "45.40-minute",
        "7.56 km/h",
        "public synthetic dataset is separate",
        "empty-volume",
        "Do not publish",
    ]
    missing_language = [text for text in required_language if text not in readme]
    if missing_language:
        raise SystemExit(f"README is missing required release language: {missing_language}")

    prohibited = [
        "MIT " + "xPRO",
        "course " + "assignment",
        "supplied " + "starter components",
        "graded " + "100/100",
    ]
    for phrase in prohibited:
        for path in ROOT.rglob("*"):
            if not path.is_file() or any(part in {".git", "public-export"} for part in path.parts):
                continue
            if path.suffix.lower() not in {
                ".md", ".txt", ".py", ".java", ".html", ".js", ".css", ".xml",
                ".yml", ".yaml", ".json", ".sh",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if phrase in text:
                raise SystemExit(
                    f"Prohibited restricted-material phrase found in {path.relative_to(ROOT)}: {phrase}"
                )

    print("Project structure and release-language validation passed.")


if __name__ == "__main__":
    main()
