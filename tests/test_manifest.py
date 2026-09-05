from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from write_manifest import render_manifest, verify_manifest, write_manifest  # noqa: E402


def test_manifest_write_and_verify(tmp_path: Path):
    (tmp_path / "a.txt").write_text("alpha\n", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "b.txt").write_text("beta\n", encoding="utf-8")

    manifest = write_manifest(tmp_path)
    assert manifest.read_text(encoding="utf-8") == render_manifest(tmp_path)
    assert verify_manifest(tmp_path) == []

    (tmp_path / "a.txt").write_text("changed\n", encoding="utf-8")
    assert verify_manifest(tmp_path)
