from __future__ import annotations

from datetime import datetime
import json
import os
import time
import urllib.request


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "transit-pipeline-validator/1.0"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def is_iso_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    text = value.strip().replace("Z", "+00:00")
    try:
        datetime.fromisoformat(text)
    except ValueError:
        return False
    return True


def validate_payloads(
    web_health: dict,
    cdc_health: dict,
    stats: dict,
    vehicles: dict,
    expected_mode: str,
) -> None:
    if web_health.get("status") != "ok":
        raise RuntimeError(f"web health is not ok: {web_health}")
    if web_health.get("data_mode") != expected_mode:
        raise RuntimeError(f"web reports an unexpected data mode: {web_health}")
    if cdc_health.get("status") != "ready":
        raise RuntimeError(f"CDC is not ready: {cdc_health}")
    if not cdc_health.get("processed_events", 0):
        raise RuntimeError(f"CDC has not processed an event: {cdc_health}")
    if cdc_health.get("failed_events", 0):
        raise RuntimeError(f"CDC reports failed events: {cdc_health}")
    if stats.get("data_mode") != expected_mode:
        raise RuntimeError(f"stats reports an unexpected data mode: {stats}")
    if not stats.get("observation_count", 0):
        raise RuntimeError(f"MongoDB has no observations: {stats}")
    if not stats.get("cdc_event_count", 0):
        raise RuntimeError(f"MongoDB has no CDC events: {stats}")

    records = vehicles.get("data")
    if not isinstance(records, list) or not records:
        raise RuntimeError("Vehicle API returned no data")
    if expected_mode in {"synthetic", "replay"}:
        invalid_ids = [
            record.get("vehicle_id")
            for record in records
            if not str(record.get("vehicle_id", "")).startswith("demo-vehicle-")
        ]
        if invalid_ids:
            raise RuntimeError(f"Non-synthetic vehicle IDs found: {invalid_ids}")

    latest_timestamp = (stats.get("latest_observation") or {}).get("observed_at")
    if not is_iso_timestamp(latest_timestamp):
        raise RuntimeError(f"Latest observation timestamp is not readable ISO data: {latest_timestamp}")
    for record in records:
        if not is_iso_timestamp(record.get("observed_at")):
            raise RuntimeError(f"Vehicle timestamp is not readable ISO data: {record}")


def main() -> None:
    web_port = os.getenv("WEB_PORT", "3000")
    cdc_port = os.getenv("CDC_HEALTH_PORT", "8080")
    expected_mode = os.getenv("EXPECTED_DATA_MODE", "synthetic").strip().lower()
    timeout_seconds = int(os.getenv("VALIDATION_TIMEOUT_SECONDS", "120"))
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            web_health = fetch_json(f"http://localhost:{web_port}/health")
            cdc_health = fetch_json(f"http://localhost:{cdc_port}/health")
            stats = fetch_json(f"http://localhost:{web_port}/api/stats")
            vehicles = fetch_json(f"http://localhost:{web_port}/api/vehicles?limit=100")
            validate_payloads(web_health, cdc_health, stats, vehicles, expected_mode)
            print(json.dumps({
                "web": web_health,
                "cdc": cdc_health,
                "stats": stats,
                "sample_vehicle": vehicles["data"][0],
            }, indent=2))
            print("Running-stack validation passed.")
            return
        except Exception as exc:
            last_error = exc
            time.sleep(3)

    raise SystemExit(f"Running-stack validation failed: {last_error}")


if __name__ == "__main__":
    main()
