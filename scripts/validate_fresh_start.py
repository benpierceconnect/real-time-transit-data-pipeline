from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def compose_command(env_file: Path, *args: str) -> list[str]:
    return ["docker", "compose", "--env-file", str(env_file), *args]


def run(command: list[str], *, env: dict[str, str] | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command))
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=capture,
        check=True,
    )


def parse_restart_count(value: str) -> int:
    count = int(value.strip())
    if count < 0:
        raise ValueError("restart count cannot be negative")
    return count


def cdc_restart_count(env_file: Path) -> int:
    container = run(
        compose_command(env_file, "ps", "-q", "cdc-service"),
        capture=True,
    ).stdout.strip()
    if not container:
        raise RuntimeError("CDC service container was not found")
    result = run(
        ["docker", "inspect", "-f", "{{.RestartCount}}", container],
        capture=True,
    )
    return parse_restart_count(result.stdout)


def diagnostics(env_file: Path) -> None:
    for args in (("ps",), ("logs", "--tail", "200", "mysql", "cdc-service", "collector")):
        try:
            completed = subprocess.run(
                compose_command(env_file, *args),
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            print(completed.stdout)
            if completed.stderr:
                print(completed.stderr, file=sys.stderr)
        except Exception as exc:  # pragma: no cover - diagnostic fallback
            print(f"Unable to capture Docker diagnostics: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Destructively validate an empty-volume Docker start and require CDC to process "
            "at least one event without a manual or automatic CDC restart."
        )
    )
    parser.add_argument(
        "--confirm-reset",
        action="store_true",
        help="Required acknowledgment that project Docker volumes will be deleted.",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Local environment file relative to the repository root (default: .env).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=240,
        help="Maximum time for the running-stack validator (default: 240).",
    )
    parser.add_argument(
        "--reuse-images",
        action="store_true",
        help="Skip the no-cache image build and reuse existing images.",
    )
    parser.add_argument(
        "--keep-running",
        action="store_true",
        help="Leave the validated stack running for browser and database review.",
    )
    args = parser.parse_args(argv)

    if not args.confirm_reset:
        parser.error("--confirm-reset is required because this check deletes project Docker volumes")
    if args.timeout_seconds < 30:
        parser.error("--timeout-seconds must be at least 30")
    if shutil.which("docker") is None:
        raise SystemExit("Docker was not found on PATH")

    env_file = (ROOT / args.env_file).resolve()
    if not env_file.is_file():
        raise SystemExit(f"Local environment file not found: {env_file}")

    run(compose_command(env_file, "config", "--quiet"))
    run(compose_command(env_file, "down", "-v", "--remove-orphans"))

    try:
        if not args.reuse_images:
            run(compose_command(env_file, "build", "--no-cache", "--progress", "plain"))
        run(compose_command(env_file, "up", "-d"))

        validator_env = os.environ.copy()
        validator_env["EXPECTED_DATA_MODE"] = "synthetic"
        validator_env["VALIDATION_TIMEOUT_SECONDS"] = str(args.timeout_seconds)
        run([sys.executable, "scripts/validate_running_stack.py"], env=validator_env)

        restart_count = cdc_restart_count(env_file)
        if restart_count != 0:
            raise RuntimeError(
                f"CDC service restart count is {restart_count}; expected 0 for an untouched fresh start"
            )

        print("Fresh-start integration validation passed.")
        print("CDC processed at least one event and the CDC container restart count remained 0.")
        if args.keep_running:
            print("Stack left running for direct database and browser review.")
        else:
            run(compose_command(env_file, "down", "-v"))
        return 0
    except Exception:
        diagnostics(env_file)
        print(
            "Fresh-start integration validation failed. The stack was left running for diagnosis.",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    sys.exit(main())
