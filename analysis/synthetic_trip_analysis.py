from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


@dataclass(frozen=True)
class AnalysisSummary:
    observation_count: int
    trip_count: int
    vehicle_count: int
    earliest_timestamp: str
    latest_timestamp: str
    duration_hours: float
    complete_trip_count: int
    incomplete_trip_count: int
    mean_complete_duration_minutes: float
    mean_complete_point_to_point_speed_kmh: float


def load_observations(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {
        "vehicle_id",
        "latitude",
        "longitude",
        "route_id",
        "trip_id",
        "direction_id",
        "stop_sequence",
        "observed_at",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    frame["observed_at"] = pd.to_datetime(
        frame["observed_at"], errors="raise", utc=True
    )
    return frame.sort_values(["trip_id", "observed_at"]).reset_index(drop=True)


def haversine_km(lat0: float, lon0: float, lat1: float, lon1: float) -> float:
    radius = 6371.0088
    phi0, phi1 = math.radians(lat0), math.radians(lat1)
    dphi = math.radians(lat1 - lat0)
    dlambda = math.radians(lon1 - lon0)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi0) * math.cos(phi1) * math.sin(dlambda / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def trip_spans(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = frame.groupby("trip_id", sort=False)
    first = grouped.first().reset_index()
    last = grouped.last().reset_index()
    spans = first[
        ["trip_id", "latitude", "longitude", "observed_at", "stop_sequence"]
    ].merge(
        last[
            ["trip_id", "latitude", "longitude", "observed_at", "stop_sequence"]
        ],
        on="trip_id",
        suffixes=("_start", "_end"),
    )
    spans = spans.rename(
        columns={
            "stop_sequence_start": "start_sequence",
            "stop_sequence_end": "end_sequence",
            "observed_at_start": "start_time",
            "observed_at_end": "end_time",
            "latitude_start": "start_latitude",
            "longitude_start": "start_longitude",
            "latitude_end": "end_latitude",
            "longitude_end": "end_longitude",
        }
    )
    spans["duration_minutes"] = (
        spans["end_time"] - spans["start_time"]
    ).dt.total_seconds() / 60.0
    spans["point_to_point_km"] = spans.apply(
        lambda row: haversine_km(
            row.start_latitude,
            row.start_longitude,
            row.end_latitude,
            row.end_longitude,
        ),
        axis=1,
    )
    spans["point_to_point_speed_kmh"] = spans["point_to_point_km"] / (
        spans["duration_minutes"] / 60.0
    )
    return spans


def analyze(
    frame: pd.DataFrame,
) -> tuple[AnalysisSummary, pd.DataFrame, pd.DataFrame]:
    spans = trip_spans(frame)
    eligible = spans[
        (spans["start_sequence"] <= 1) & (spans["duration_minutes"] > 0)
    ].copy()
    complete = eligible[eligible["end_sequence"] >= 24].copy()
    incomplete = eligible[eligible["end_sequence"] < 24].copy()
    earliest = frame["observed_at"].min()
    latest = frame["observed_at"].max()

    if complete.empty:
        raise ValueError("No complete trips reached stop sequence 24")

    summary = AnalysisSummary(
        observation_count=int(len(frame)),
        trip_count=int(frame["trip_id"].nunique()),
        vehicle_count=int(frame["vehicle_id"].nunique()),
        earliest_timestamp=earliest.isoformat(),
        latest_timestamp=latest.isoformat(),
        duration_hours=round((latest - earliest).total_seconds() / 3600.0, 4),
        complete_trip_count=int(len(complete)),
        incomplete_trip_count=int(len(incomplete)),
        mean_complete_duration_minutes=round(
            float(complete["duration_minutes"].mean()), 2
        ),
        mean_complete_point_to_point_speed_kmh=round(
            float(complete["point_to_point_speed_kmh"].mean()), 2
        ),
    )
    return summary, complete, incomplete


def write_outputs(
    summary: AnalysisSummary,
    complete: pd.DataFrame,
    incomplete: pd.DataFrame,
    frame: pd.DataFrame,
    output_dir: str | Path,
    figure_dir: str | Path,
) -> None:
    output_path = Path(output_dir)
    figure_path = Path(figure_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    figure_path.mkdir(parents=True, exist_ok=True)

    (output_path / "synthetic_analysis_summary.json").write_text(
        json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8"
    )
    complete.to_csv(output_path / "complete_synthetic_trips.csv", index=False)
    incomplete.to_csv(output_path / "incomplete_synthetic_trips.csv", index=False)

    observations_5min = frame.set_index("observed_at").resample("5min").size()
    plt.figure(figsize=(10, 4.8))
    observations_5min.plot()
    plt.title("Synthetic transit observations per five minutes")
    plt.xlabel("Time")
    plt.ylabel("Observations")
    plt.tight_layout()
    plt.savefig(
        figure_path / "synthetic_observations_per_5_minutes.png", dpi=160
    )
    plt.close()

    sorted_complete = complete.sort_values("start_time")
    plt.figure(figsize=(10, 5.5))
    plt.barh(
        sorted_complete["trip_id"].astype(str),
        sorted_complete["duration_minutes"],
    )
    plt.title("Complete synthetic trip durations")
    plt.xlabel("Duration in minutes")
    plt.ylabel("Trip ID")
    plt.tight_layout()
    plt.savefig(
        figure_path / "synthetic_complete_trip_durations.png", dpi=160
    )
    plt.close()


def run(
    input_path: str | Path,
    output_dir: str | Path,
    figure_dir: str | Path,
) -> AnalysisSummary:
    frame = load_observations(input_path)
    summary, complete, incomplete = analyze(frame)
    write_outputs(summary, complete, incomplete, frame, output_dir, figure_dir)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze deterministic synthetic transit observations"
    )
    parser.add_argument(
        "--input", default="data/sample/synthetic_trip_observations.csv"
    )
    parser.add_argument("--output-dir", default="analysis/results")
    parser.add_argument("--figure-dir", default="analysis/figures")
    args = parser.parse_args()
    summary = run(args.input, args.output_dir, args.figure_dir)
    print(json.dumps(asdict(summary), indent=2))


if __name__ == "__main__":
    main()
