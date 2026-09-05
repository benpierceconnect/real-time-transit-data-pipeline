from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "web"))

from serialization import epoch_number_to_iso, serializable  # noqa: E402


def test_epoch_units_convert_to_same_instant():
    expected_prefix = "2025-11-06T"
    values = [
        1_762_388_068,
        1_762_388_068_000,
        1_762_388_068_000_000,
        1_762_388_068_000_000_000,
    ]
    for value in values:
        assert epoch_number_to_iso(value).startswith(expected_prefix)


def test_nested_timestamp_fields_become_iso_strings():
    payload = serializable({
        "observed_at": 1_762_388_068_000,
        "nested": {"collected_at": 1_762_388_068_000_000},
        "ordinary_number": 42,
    })
    assert payload["observed_at"].startswith("2025-11-06T")
    assert payload["nested"]["collected_at"].startswith("2025-11-06T")
    assert payload["ordinary_number"] == 42


def test_datetime_is_normalized_to_iso():
    result = serializable({"observed_at": datetime(2026, 9, 4, 18, 48, 31)})
    assert result["observed_at"] == "2026-09-04T18:48:31+00:00"
