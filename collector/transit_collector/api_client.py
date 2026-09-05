from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from .models import VehicleObservation


class TransitApiClient:
    def __init__(self, url: str, api_key: str | None = None, timeout_seconds: float = 15):
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "ben-pierce-transit-pipeline/1.0 "
                "(+https://github.com/benpierceconnect/real-time-transit-data-pipeline; "
                "contact: benpierceconnect@gmail.com)"
            )
        })
        if api_key:
            self.session.headers.update({"x-api-key": api_key})

    def fetch(self) -> list[VehicleObservation]:
        response = self.session.get(self.url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return parse_payload(response.json())


def load_synthetic_snapshot(
    path: str | Path,
    refresh_timestamps: bool = True,
) -> list[VehicleObservation]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    observations = parse_payload(payload)
    if refresh_timestamps:
        return [item.with_current_timestamp() for item in observations]
    return observations


def parse_payload(payload: dict[str, Any]) -> list[VehicleObservation]:
    records = payload.get("data")
    if not isinstance(records, list):
        raise ValueError("transit payload must contain a data list")

    observations: list[VehicleObservation] = []
    errors: list[str] = []
    for index, record in enumerate(records):
        try:
            observations.append(VehicleObservation.from_api_record(record))
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"record {index}: {exc}")

    if not observations:
        detail = "; ".join(errors[:5])
        raise ValueError(f"No valid vehicle observations were found. {detail}")
    return observations
