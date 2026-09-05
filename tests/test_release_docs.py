from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_readme_contains_limited_historical_analysis_context():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "6,767-observation" in readme
    assert "approximately 4.85 hours" in readme
    assert "not the full runtime" in readme
    assert "45.40-minute" in readme
    assert "7.56 km/h" in readme
    assert "private educational prototype" in readme
    assert "public synthetic dataset is separate" in readme


def test_runbook_scans_public_files_before_creating_local_env():
    runbook = (ROOT / "docs" / "RUN_FULL_STACK.md").read_text(encoding="utf-8")
    scan = "python scripts/secret_scan.py --public-files"
    configure = "cp .env.example .env"
    assert scan in runbook
    assert configure in runbook
    assert runbook.index(scan) < runbook.index(configure)
    assert "validate_fresh_start.py --confirm-reset --keep-running" in runbook


def test_release_documents_keep_publication_gated():
    checklist = (ROOT / "docs" / "PUBLICATION_CHECKLIST.md").read_text(encoding="utf-8")
    validation = (ROOT / "docs" / "VALIDATION.md").read_text(encoding="utf-8")
    assert "Ben confirms the historical database password will never be reused" in checklist
    assert "Ben confirms the historical Mapbox token is revoked or permanently inactive" in checklist
    assert "fresh-start validation" in validation.lower()
    assert "manual restart" in validation.lower()
