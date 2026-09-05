from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class VehicleObservation:
    vehicle_id: str
    latitude: float
    longitude: float
    route_id: str | None
    trip_id: str | None
    direction_id: int | None
    stop_sequence: int | None
    occupancy_status: str | None
    bearing_degrees: float | None
    speed_mps: float | None
    observed_at: datetime

    @classmethod
    def from_api_record(cls, record: Mapping[str, Any]) -> "VehicleObservation":
        attributes = record.get("attributes") or {}
        relationships = record.get("relationships") or {}

        vehicle_id = str(record.get("id") or "").strip()
        if not vehicle_id:
            raise ValueError("vehicle record is missing id")

        return cls(
            vehicle_id=vehicle_id,
            latitude=_required_coordinate(attributes.get("latitude"), "latitude", -90, 90),
            longitude=_required_coordinate(attributes.get("longitude"), "longitude", -180, 180),
            route_id=_relationship_id(relationships, "route"),
            trip_id=_relationship_id(relationships, "trip"),
            direction_id=_optional_int(attributes.get("direction_id")),
            stop_sequence=_optional_int(attributes.get("current_stop_sequence")),
            occupancy_status=_optional_string(attributes.get("occupancy_status")),
            bearing_degrees=_optional_float(attributes.get("bearing")),
            speed_mps=_optional_float(attributes.get("speed")),
            observed_at=_parse_datetime(attributes.get("updated_at")),
        )

    @classmethod
    def from_csv_row(cls, row: Mapping[str, Any]) -> "VehicleObservation":
        return cls(
            vehicle_id=str(row["vehicle_id"]),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            route_id=_optional_string(row.get("route_id")),
            trip_id=_optional_string(row.get("trip_id")),
            direction_id=_optional_int(row.get("direction_id")),
            stop_sequence=_optional_int(row.get("stop_sequence")),
            occupancy_status=_optional_string(row.get("occupancy_status")),
            bearing_degrees=_optional_float(row.get("bearing_degrees")),
            speed_mps=_optional_float(row.get("speed_mps")),
            observed_at=_parse_datetime(row.get("observed_at")),
        )

    def with_current_timestamp(self) -> "VehicleObservation":
        return replace(self, observed_at=datetime.now(timezone.utc))

    def mysql_values(self) -> tuple[Any, ...]:
        return (
            self.vehicle_id,
            self.latitude,
            self.longitude,
            self.route_id,
            self.trip_id,
            self.direction_id,
            self.stop_sequence,
            self.occupancy_status,
            self.bearing_degrees,
            self.speed_mps,
            self.observed_at.astimezone(timezone.utc).replace(tzinfo=None),
        )


def _relationship_id(relationships: Mapping[str, Any], key: str) -> str | None:
    relationship = relationships.get(key) or {}
    data = relationship.get("data") or {}
    value = data.get("id")
    return str(value) if value is not None else None


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or "").strip()
        if not text:
            return datetime.now(timezone.utc)
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _required_coordinate(value: Any, name: str, low: float, high: float) -> float:
    result = float(value)
    if not low <= result <= high:
        raise ValueError(f"{name} is outside the valid range")
    return result


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "nan", "null"}:
        return None
    return text


def _optional_float(value: Any) -> float | None:
    text = _optional_string(value)
    return float(text) if text is not None else None


def _optional_int(value: Any) -> int | None:
    text = _optional_string(value)
    return int(float(text)) if text is not None else None
