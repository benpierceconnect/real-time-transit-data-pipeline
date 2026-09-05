from pathlib import Path
import sys

import pytest

pytest.importorskip("flask")
pytest.importorskip("pymongo")

WEB = Path(__file__).parents[1]
sys.path.insert(0, str(WEB))

import app as web_app  # noqa: E402
from serialization import serializable  # noqa: E402


class FakeRepository:
    def ping(self):
        return True

    def latest_vehicles(self, limit=100):
        return [{
            "vehicle_id": "demo-vehicle-01",
            "route_id": "1",
            "direction_id": 0,
            "observed_at": "2026-09-04T18:48:31+00:00",
        }][:limit]

    def stats(self):
        return {
            "latest_vehicle_count": 1,
            "observation_count": 10,
            "cdc_event_count": 10,
            "latest_observation": {
                "vehicle_id": "demo-vehicle-01",
                "observed_at": "2026-09-04T18:48:31+00:00",
            },
        }


class FailingRepository:
    def ping(self):
        raise RuntimeError("database unavailable")

    def latest_vehicles(self, limit=100):
        raise RuntimeError("database unavailable")

    def stats(self):
        raise RuntimeError("database unavailable")


def test_health_and_api_endpoints(monkeypatch):
    monkeypatch.setattr(web_app, "repository", FakeRepository())
    monkeypatch.setenv("DATA_MODE", "synthetic")
    client = web_app.app.test_client()
    assert client.get("/health").get_json() == {"status": "ok", "data_mode": "synthetic"}
    assert client.get("/api/stats").get_json()["observation_count"] == 10
    assert client.get("/api/stats").get_json()["data_mode"] == "synthetic"
    assert client.get("/api/vehicles?limit=5").get_json()["data"][0]["vehicle_id"] == "demo-vehicle-01"


def test_index_includes_map_configuration_and_mode(monkeypatch):
    monkeypatch.setattr(web_app, "repository", FakeRepository())
    monkeypatch.setenv("DATA_MODE", "replay")
    response = web_app.app.test_client().get("/")
    assert response.status_code == 200
    assert b"tile.openstreetmap.org" in response.data
    assert b"OpenStreetMap contributors" in response.data
    assert b"Current data mode: replay" in response.data


def test_backend_errors_return_503(monkeypatch):
    monkeypatch.setattr(web_app, "repository", FailingRepository())
    client = web_app.app.test_client()
    assert client.get("/health").status_code == 503
    assert client.get("/api/stats").status_code == 503
    assert client.get("/api/vehicles").status_code == 503


def test_numeric_debezium_timestamps_are_serialized_as_iso():
    milliseconds = serializable({"observed_at": 1762388068000})["observed_at"]
    microseconds = serializable({"observed_at": 1762388068000000})["observed_at"]
    assert milliseconds.startswith("2025-11-06T")
    assert microseconds.startswith("2025-11-06T")


def test_security_headers_are_present(monkeypatch):
    monkeypatch.setattr(web_app, "repository", FakeRepository())
    response = web_app.app.test_client().get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
