from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from .models import VehicleObservation


def replay_batches(path: str | Path, batch_size: int) -> Iterator[list[VehicleObservation]]:
    batch: list[VehicleObservation] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            batch.append(VehicleObservation.from_csv_row(row))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
