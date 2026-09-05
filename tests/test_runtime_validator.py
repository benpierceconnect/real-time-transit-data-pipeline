from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_running_stack import is_iso_timestamp, validate_payloads  # noqa: E402


def valid_payloads():
    return (
        {"status": "ok", "data_mode": "synthetic"},
        {"status": "ready", "processed_events": 7, "failed_events": 0},
        {
            "data_mode": "synthetic",
            "observation_count": 7,
            "cdc_event_count": 7,
            "latest_observation": {"observed_at": "2026-09-04T18:48:31+00:00"},
        },
        {"data": [{
            "vehicle_id": "demo-vehicle-01",
            "observed_at": "2026-09-04T18:48:31+00:00",
        }]},
    )


def test_iso_timestamp_validation():
    assert is_iso_timestamp("2026-09-04T18:48:31+00:00")
    assert is_iso_timestamp("2026-09-04T18:48:31Z")
    assert not is_iso_timestamp(1788547710598)
    assert not is_iso_timestamp("not-a-date")


def test_valid_runtime_payloads_pass():
    validate_payloads(*valid_payloads(), expected_mode="synthetic")


def test_runtime_payloads_reject_failed_cdc_events():
    web, cdc, stats, vehicles = valid_payloads()
    cdc["failed_events"] = 1
    try:
        validate_payloads(web, cdc, stats, vehicles, "synthetic")
    except RuntimeError as exc:
        assert "failed events" in str(exc)
    else:
        raise AssertionError("failed CDC events should fail validation")


def test_runtime_payloads_reject_non_synthetic_ids():
    web, cdc, stats, vehicles = valid_payloads()
    vehicles["data"][0]["vehicle_id"] = "captured-id"
    try:
        validate_payloads(web, cdc, stats, vehicles, "synthetic")
    except RuntimeError as exc:
        assert "Non-synthetic" in str(exc)
    else:
        raise AssertionError("non-synthetic IDs should fail validation")
