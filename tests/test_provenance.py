from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_public_repository_uses_neutral_independent_positioning():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    prohibited = ("MIT " + "xPRO", "course " + "assignment", "supplied " + "starter components", "graded " + "100/100")
    for phrase in prohibited:
        assert phrase not in readme
    assert "independently authored" in readme
    assert "synthetic" in readme


def test_restricted_material_and_private_evidence_are_absent():
    prohibited_suffixes = {".doc", ".docx", ".pdf"}
    prohibited_names = {
        "RESTORATION_AUDIT_SOURCE.md",
        "RESTORATION_DECISIONS.md",
        "Assignment_Grade_100_of_100.png",
    }
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        assert path.suffix.lower() not in prohibited_suffixes
        assert path.name not in prohibited_names
        assert "data/private" not in path.as_posix()


def test_public_data_is_synthetic():
    public_data = [path for path in (ROOT / "data").rglob("*") if path.is_file()]
    assert public_data
    for path in public_data:
        if path.suffix.lower() in {".json", ".csv"}:
            assert "synthetic" in path.name
