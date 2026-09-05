from pathlib import Path
import json

ROOT = Path(__file__).parents[1]

REQUIRED_FIELDS = {
    "vehicle_id",
    "latitude",
    "longitude",
    "route_id",
    "trip_id",
    "direction_id",
    "stop_sequence",
    "occupancy_status",
    "bearing_degrees",
    "speed_mps",
    "observed_at",
}


def test_schema_fields_are_consistent_across_services():
    schema = (ROOT / "mysql/init/001_schema.sh").read_text(encoding="utf-8")
    collector = (ROOT / "collector/transit_collector/mysql_store.py").read_text(encoding="utf-8")
    frontend = (ROOT / "web/static/app.js").read_text(encoding="utf-8")
    fixture = json.loads(
        (ROOT / "data/fixtures/synthetic_vehicle_snapshot.json").read_text(encoding="utf-8")
    )

    for field in REQUIRED_FIELDS:
        assert field in schema
        assert field in collector

    first = fixture["data"][0]
    attributes = first["attributes"]
    assert first["id"].startswith("demo-vehicle-")
    assert attributes["current_stop_sequence"] is not None
    assert "updated_at" in attributes
    assert "vehicle.stop_sequence" in frontend
    assert "vehicle.observed_at" in frontend


def test_web_mode_follows_collector_mode_in_compose():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "COLLECTOR_MODE: ${COLLECTOR_MODE:-synthetic}" in compose
    assert "DATA_MODE: ${COLLECTOR_MODE:-synthetic}" in compose
