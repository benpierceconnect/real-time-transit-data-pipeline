from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".java", ".xml", ".yml", ".yaml", ".json",
    ".js", ".css", ".html", ".sql", ".sh", ".env", ".example", ""
}
SKIP_PARTS = {
    ".git", ".venv", "venv", "target", "__pycache__", "private-evidence",
    "public-export", ".pytest_cache", "release-evidence",
}
ALLOWED_MARKERS = {
    "change-me-root-password",
    "change-me-app-password",
    "change-me-cdc-password",
    "YOUR_DATABASE_PASSWORD",
    "YOUR_MAPBOX_TOKEN",
    "REDACTED",
}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "Mapbox public token": re.compile(r"\bpk\.[A-Za-z0-9._-]{30,}\b"),
    "Mapbox secret token": re.compile(r"\bsk\.[A-Za-z0-9._-]{30,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "OpenAI key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
}
LITERAL_ASSIGNMENT = re.compile(
    r"(?i)(?:password|passwd|secret|api[_-]?key|access[_-]?token)\s*=\s*[\"\']([^\"\']{8,})[\"\']"
)
ENV_ASSIGNMENT = re.compile(
    r"(?i)^(?:[A-Z0-9_]*(?:PASSWORD|SECRET|TOKEN|API_KEY)[A-Z0-9_]*)=([^#\s]*)$"
)


def scan(*, include_local_env: bool = True, root: Path | None = None) -> list[str]:
    scan_root = root or ROOT
    findings: list[str] = []
    for path in scan_root.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if "data/private" in path.as_posix():
            continue
        if path.name == ".env" and not include_local_env:
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name != ".env.example":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(scan_root)
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                token = match.group(0)
                if token not in ALLOWED_MARKERS:
                    findings.append(f"{rel}: possible {label}")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in LITERAL_ASSIGNMENT.finditer(line):
                value = match.group(1).strip()
                if value in ALLOWED_MARKERS or "change-me-" in value:
                    continue
                findings.append(f"{rel}:{line_number}: possible literal credential assignment")
            if path.name.startswith(".env"):
                env_match = ENV_ASSIGNMENT.match(line.strip())
                if env_match:
                    value = env_match.group(1).strip()
                    if not value or value in ALLOWED_MARKERS or "change-me-" in value:
                        continue
                    findings.append(f"{rel}:{line_number}: possible environment credential")
    return sorted(set(findings))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan project text files for obvious live credentials.")
    parser.add_argument(
        "--public-files",
        action="store_true",
        help="Scan the distributable project files while intentionally excluding the local-only .env file.",
    )
    args = parser.parse_args(argv)

    results = scan(include_local_env=not args.public_files)
    if results:
        print("Potential secrets found:")
        print("\n".join(f"- {item}" for item in results))
        return 1

    scope = "public files" if args.public_files else "project files"
    print(f"Secret scan passed for {scope}: no obvious live credentials found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
