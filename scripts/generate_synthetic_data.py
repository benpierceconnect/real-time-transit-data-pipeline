from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
from io import StringIO
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "fixtures" / "synthetic_vehicle_snapshot.json"
REPLAY = ROOT / "data" / "sample" / "synthetic_trip_observations.csv"

BASE_LAT = 42.3298
BASE_LON = -71.0838
END_LAT = 42.3731
END_LON = -71.1177


def snapshot_payload() -> dict[str, object]:
    records: list[dict[str, object]] = []
    for index in range(7):
        direction = index % 2
        fraction = (index + 1) / 8
        if direction == 1:
            fraction = 1 - fraction
        records.append(
            {
                "type": "vehicle",
                "id": f"demo-vehicle-{index + 1:02d}",
                "attributes": {
                    "bearing": float(45 + index * 35) % 360,
                    "current_stop_sequence": 2 + index * 3,
                    "direction_id": direction,
                    "latitude": round(BASE_LAT + (END_LAT - BASE_LAT) * fraction, 6),
                    "longitude": round(BASE_LON + (END_LON - BASE_LON) * fraction, 6),
                    "occupancy_status": [
                        "MANY_SEATS_AVAILABLE",
                        "FEW_SEATS_AVAILABLE",
                        "STANDING_ROOM_ONLY",
                    ][index % 3],
                    "speed": round(4.5 + index * 0.35, 2),
                    "updated_at": f"2026-01-01T12:00:{index * 5:02d}Z",
                },
                "relationships": {
                    "route": {"data": {"id": "1", "type": "route"}},
                    "trip": {
                        "data": {
                            "id": f"demo-trip-{index + 1:02d}",
                            "type": "trip",
                        }
                    },
                },
            }
        )
    return {
        "data": records,
        "meta": {"synthetic": True, "record_count": len(records)},
    }


def replay_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start = datetime(2026, 1, 1, 14, 0, tzinfo=timezone.utc)

    # Six trips contain stop sequences 1 through 25. Two end early so the
    # analysis can demonstrate an explicit complete-trip rule.
    trip_lengths = [25, 25, 25, 25, 25, 25, 16, 20]
    seconds_per_stop = [86, 91, 95, 88, 93, 89, 92, 90]

    for trip_index, stop_count in enumerate(trip_lengths):
        direction = trip_index % 2
        trip_start = start + timedelta(minutes=trip_index * 6)
        for stop_index in range(stop_count):
            fraction = stop_index / 24
            if direction == 1:
                fraction = 1 - fraction
            rows.append(
                {
                    "vehicle_id": f"demo-vehicle-{trip_index % 4 + 1:02d}",
                    "latitude": round(
                        BASE_LAT + (END_LAT - BASE_LAT) * fraction, 6
                    ),
                    "longitude": round(
                        BASE_LON + (END_LON - BASE_LON) * fraction, 6
                    ),
                    "route_id": "1",
                    "trip_id": f"synthetic-trip-{trip_index + 1:02d}",
                    "direction_id": direction,
                    "stop_sequence": stop_index + 1,
                    "occupancy_status": (
                        "MANY_SEATS_AVAILABLE"
                        if stop_index < 12
                        else "FEW_SEATS_AVAILABLE"
                    ),
                    "bearing_degrees": 315.0 if direction == 0 else 135.0,
                    "speed_mps": round(5.0 + trip_index * 0.15, 2),
                    "observed_at": (
                        trip_start
                        + timedelta(
                            seconds=stop_index * seconds_per_stop[trip_index]
                        )
                    ).isoformat(),
                }
            )
    return rows


def render_snapshot() -> str:
    return json.dumps(snapshot_payload(), indent=2) + "\n"


def render_replay() -> str:
    fieldnames = [
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
    ]
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(replay_rows())
    return buffer.getvalue()


def expected_files() -> dict[Path, str]:
    return {SNAPSHOT: render_snapshot(), REPLAY: render_replay()}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic synthetic transit data"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed files match the generator",
    )
    args = parser.parse_args()

    expected = expected_files()
    if args.check:
        mismatches = [
            str(path.relative_to(ROOT))
            for path, text in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        if mismatches:
            raise SystemExit(f"Synthetic data is out of date: {mismatches}")
        print("Synthetic data matches the generator.")
        return

    for path, text in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
