from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from write_manifest import write_manifest

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public-export" / "real-time-transit-data-pipeline"
EXCLUDED_NAMES = {
    ".git", ".env", ".venv", "venv", "target", "__pycache__",
    ".pytest_cache", "public-export", "release-evidence",
}


def ignore(directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in EXCLUDED_NAMES}


def run_check(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        if OUTPUT.exists():
            shutil.rmtree(OUTPUT)
        raise SystemExit(result.stdout + result.stderr)


def remove_generated_test_artifacts(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir() and path.name in {"__pycache__", ".pytest_cache"}:
            shutil.rmtree(path)
        elif path.is_file() and path.suffix in {".pyc", ".pyo", ".class"}:
            path.unlink()


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, OUTPUT, ignore=ignore)
    run_check(["python", "scripts/generate_synthetic_data.py", "--check"], OUTPUT)
    run_check(["python", "scripts/secret_scan.py", "--public-files"], OUTPUT)
    run_check(["python", "scripts/validate_project.py"], OUTPUT)
    run_check(["pytest", "-q"], OUTPUT)
    remove_generated_test_artifacts(OUTPUT)
    write_manifest(OUTPUT)
    run_check(["python", "scripts/write_manifest.py", "--verify"], OUTPUT)
    run_check(["python", "scripts/secret_scan.py", "--public-files"], OUTPUT)
    print(f"Public candidate prepared at: {OUTPUT}")
    print("This is not publication approval. Complete docs/PUBLICATION_CHECKLIST.md first.")


if __name__ == "__main__":
    main()
