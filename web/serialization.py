from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

_TIMESTAMP_FIELDS = {"observed_at", "collected_at", "cdc_processed_at"}


def serializable(value: Any, field_name: str | None = None) -> Any:
    """Convert MongoDB-compatible values into JSON-safe values.

    Debezium can serialize MySQL temporal columns as numeric epoch values.
    Timestamp fields are normalized to UTC ISO 8601 strings for API clients.
    """
    if isinstance(value, dict):
        return {key: serializable(item, key) for key, item in value.items()}
    if isinstance(value, list):
        return [serializable(item) for item in value]
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if field_name in _TIMESTAMP_FIELDS and isinstance(value, (int, float)):
        return epoch_number_to_iso(value)
    return value


def epoch_number_to_iso(value: int | float) -> str:
    """Normalize epoch seconds, milliseconds, microseconds, or nanoseconds."""
    magnitude = abs(float(value))
    if magnitude >= 1e17:
        seconds = float(value) / 1_000_000_000
    elif magnitude >= 1e14:
        seconds = float(value) / 1_000_000
    elif magnitude >= 1e11:
        seconds = float(value) / 1_000
    else:
        seconds = float(value)
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return str(value)
