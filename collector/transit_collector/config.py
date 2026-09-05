from __future__ import annotations

from dataclasses import dataclass
import os


def _boolean(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class CollectorConfig:
    mysql_host: str
    mysql_port: int
    mysql_database: str
    mysql_user: str
    mysql_password: str
    mode: str
    interval_seconds: float
    transit_api_url: str
    transit_api_key: str | None
    synthetic_snapshot_path: str
    refresh_synthetic_timestamps: bool
    replay_csv_path: str
    replay_batch_size: int
    replay_delay_seconds: float
    log_level: str

    @classmethod
    def from_env(cls) -> "CollectorConfig":
        password = os.getenv("MYSQL_PASSWORD", "")
        if not password:
            raise ValueError("MYSQL_PASSWORD is required")

        mode = os.getenv("COLLECTOR_MODE", "synthetic").strip().lower()
        if mode not in {"synthetic", "live", "replay"}:
            raise ValueError("COLLECTOR_MODE must be synthetic, live, or replay")

        return cls(
            mysql_host=os.getenv("MYSQL_HOST", "mysql"),
            mysql_port=int(os.getenv("MYSQL_PORT", "3306")),
            mysql_database=os.getenv("MYSQL_DATABASE", "transit_demo"),
            mysql_user=os.getenv("MYSQL_USER", "transit_app"),
            mysql_password=password,
            mode=mode,
            interval_seconds=max(0.1, float(os.getenv("COLLECT_INTERVAL_SECONDS", "10"))),
            transit_api_url=os.getenv(
                "TRANSIT_API_URL",
                "https://api-v3.mbta.com/vehicles?filter[route]=1&include=trip",
            ),
            transit_api_key=os.getenv("TRANSIT_API_KEY") or None,
            synthetic_snapshot_path=os.getenv(
                "SYNTHETIC_SNAPSHOT_PATH",
                "/data/fixtures/synthetic_vehicle_snapshot.json",
            ),
            refresh_synthetic_timestamps=_boolean(
                os.getenv("SYNTHETIC_REFRESH_TIMESTAMPS"), default=True
            ),
            replay_csv_path=os.getenv(
                "REPLAY_CSV_PATH",
                "/data/sample/synthetic_trip_observations.csv",
            ),
            replay_batch_size=max(1, int(os.getenv("REPLAY_BATCH_SIZE", "25"))),
            replay_delay_seconds=max(0.0, float(os.getenv("REPLAY_DELAY_SECONDS", "0.25"))),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
