from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import secret_scan  # noqa: E402


def test_public_files_mode_excludes_local_env(tmp_path: Path):
    (tmp_path / ".env").write_text("DATABASE_PASSWORD=local-only-password\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("DATABASE_PASSWORD=change-me-app-password\n", encoding="utf-8")

    assert secret_scan.scan(include_local_env=False, root=tmp_path) == []
    findings = secret_scan.scan(include_local_env=True, root=tmp_path)
    assert any(".env:1" in finding for finding in findings)


def test_public_files_mode_still_detects_source_credentials(tmp_path: Path):
    assignment_name = "pass" + "word"
    unsafe_value = "definitely-" + "not-safe"
    source = f'{assignment_name} = "{unsafe_value}"\n'
    (tmp_path / "app.py").write_text(source, encoding="utf-8")
    findings = secret_scan.scan(include_local_env=False, root=tmp_path)
    assert any("literal credential assignment" in finding for finding in findings)
