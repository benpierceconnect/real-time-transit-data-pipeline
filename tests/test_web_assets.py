from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_web_template_has_accessible_elements_and_attribution():
    template = (ROOT / "web" / "templates" / "index.html").read_text(encoding="utf-8")
    for element_id in (
        "health", "vehicle-count", "observation-count", "event-count",
        "last-updated", "map", "refresh", "vehicle-table", "map-config",
    ):
        assert f'id="{element_id}"' in template
    assert "Massachusetts Department of Transportation" in template
    assert "not affiliated with, endorsed by, or certified" in template
    assert "Report a map issue" in template


def test_frontend_uses_neutral_schema_and_osm_policy_url():
    javascript = (ROOT / "web" / "static" / "app.js").read_text(encoding="utf-8")
    app = (ROOT / "web" / "app.py").read_text(encoding="utf-8")
    assert "vehicle.vehicle_id" in javascript
    assert "vehicle.stop_sequence" in javascript
    assert "vehicle.observed_at" in javascript
    assert "https://tile.openstreetmap.org/{z}/{x}/{y}.png" in app
    assert "https://{s}.tile.openstreetmap.org" not in javascript
    assert "escapeText" in javascript
    assert "formatTimestamp" in javascript
    assert "Current data mode" in (ROOT / "web" / "templates" / "index.html").read_text(encoding="utf-8")


def test_web_container_includes_serialization_module():
    dockerfile = (ROOT / "web" / "Dockerfile").read_text(encoding="utf-8")
    assert "serialization.py" in dockerfile
