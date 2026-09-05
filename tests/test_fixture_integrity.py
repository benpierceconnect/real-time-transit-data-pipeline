import json
from pathlib import Path

from transit_collector.api_client import parse_payload

ROOT = Path(__file__).parents[1]


def test_synthetic_fixture_is_valid_and_parseable():
    payload = json.loads((ROOT / "data" / "fixtures" / "synthetic_vehicle_snapshot.json").read_text())
    observations = parse_payload(payload)
    assert payload["meta"]["synthetic"] is True
    assert len(observations) == 7
    assert all(item.vehicle_id.startswith("demo-vehicle-") for item in observations)
    assert all(item.route_id == "1" for item in observations)
