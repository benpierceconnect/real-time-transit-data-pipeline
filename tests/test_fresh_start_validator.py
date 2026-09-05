from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_fresh_start import compose_command, parse_restart_count  # noqa: E402


def test_compose_command_always_uses_the_requested_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    command = compose_command(env_file, "up", "-d")
    assert command == ["docker", "compose", "--env-file", str(env_file), "up", "-d"]


def test_restart_count_parser_accepts_zero_and_rejects_negative_values():
    assert parse_restart_count("0\n") == 0
    assert parse_restart_count("2") == 2
    with pytest.raises(ValueError):
        parse_restart_count("-1")
