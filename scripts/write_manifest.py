from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "MANIFEST.sha256"
SKIP_PARTS = {
    ".git", ".venv", "venv", "target", "__pycache__", ".pytest_cache",
    "public-export", "release-evidence",
}
SKIP_NAMES = {".env", MANIFEST_NAME}


def included_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.name not in SKIP_NAMES
        and not any(part in SKIP_PARTS for part in path.relative_to(root).parts)
        and path.suffix.lower() not in {".pyc", ".pyo", ".class", ".zip"}
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_manifest(root: Path) -> str:
    lines = [f"{sha256(path)}  {path.relative_to(root).as_posix()}" for path in included_files(root)]
    return "\n".join(lines) + "\n"


def write_manifest(root: Path) -> Path:
    destination = root / MANIFEST_NAME
    destination.write_text(render_manifest(root), encoding="utf-8", newline="\n")
    return destination


def verify_manifest(root: Path) -> list[str]:
    manifest = root / MANIFEST_NAME
    if not manifest.is_file():
        return [f"missing {MANIFEST_NAME}"]
    expected = render_manifest(root)
    actual = manifest.read_text(encoding="utf-8")
    return [] if actual == expected else [f"{MANIFEST_NAME} does not match the current public files"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write or verify the public-file SHA-256 manifest.")
    parser.add_argument("--verify", action="store_true", help="Verify instead of rewriting the manifest.")
    args = parser.parse_args(argv)

    if args.verify:
        findings = verify_manifest(ROOT)
        if findings:
            print("Manifest verification failed:")
            print("\n".join(f"- {item}" for item in findings))
            return 1
        print("Manifest verification passed.")
        return 0

    destination = write_manifest(ROOT)
    print(f"Wrote {destination.relative_to(ROOT)} with {len(included_files(ROOT))} entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
