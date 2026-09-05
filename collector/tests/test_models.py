from datetime import timezone

from transit_collector.api_client import parse_payload


def test_parse_payload_extracts_route_and_trip(sample_payload):
    observations = parse_payload(sample_payload)
    assert observations
    first = observations[0]
    assert first.vehicle_id.startswith("demo-vehicle-")
    assert first.route_id == "1"
    assert first.trip_id.startswith("demo-trip-")
    assert first.observed_at.tzinfo == timezone.utc
    assert -90 <= first.latitude <= 90
    assert -180 <= first.longitude <= 180


def test_parse_payload_rejects_missing_data_list():
    try:
        parse_payload({"unexpected": []})
    except ValueError as exc:
        assert "data list" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_parse_payload_skips_invalid_record_when_valid_records_remain(sample_payload):
    payload = {"data": list(sample_payload["data"]) + [{"id": "bad", "attributes": {"latitude": 999, "longitude": 0}}]}
    observations = parse_payload(payload)
    assert len(observations) == len(sample_payload["data"])


def test_parse_payload_rejects_when_every_record_is_invalid():
    payload = {"data": [{"id": "bad", "attributes": {"latitude": 999, "longitude": 0}}]}
    try:
        parse_payload(payload)
    except ValueError as exc:
        assert "No valid vehicle observations" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
