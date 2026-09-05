from __future__ import annotations

import logging
import time
from typing import Iterable

from .config import CollectorConfig
from .models import VehicleObservation

LOGGER = logging.getLogger(__name__)

INSERT_SQL = """
INSERT INTO vehicle_observations (
    vehicle_id, latitude, longitude, route_id, trip_id, direction_id,
    stop_sequence, occupancy_status, bearing_degrees, speed_mps, observed_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


class MySqlStore:
    def __init__(self, config: CollectorConfig):
        self.config = config
        self._connection = None

    def connect(self, attempts: int = 30, delay_seconds: float = 2.0) -> None:
        import mysql.connector

        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                self._connection = mysql.connector.connect(
                    host=self.config.mysql_host,
                    port=self.config.mysql_port,
                    user=self.config.mysql_user,
                    password=self.config.mysql_password,
                    database=self.config.mysql_database,
                    autocommit=False,
                    connection_timeout=10,
                )
                LOGGER.info("Connected to MySQL on attempt %s", attempt)
                return
            except mysql.connector.Error as exc:
                last_error = exc
                LOGGER.warning(
                    "MySQL connection attempt %s/%s failed: %s",
                    attempt,
                    attempts,
                    exc,
                )
                time.sleep(delay_seconds)
        raise RuntimeError("Unable to connect to MySQL") from last_error

    def insert_many(self, observations: Iterable[VehicleObservation]) -> int:
        items = list(observations)
        if not items:
            return 0
        if self._connection is None or not self._connection.is_connected():
            self.connect()

        cursor = self._connection.cursor()
        try:
            cursor.executemany(INSERT_SQL, [item.mysql_values() for item in items])
            self._connection.commit()
            return cursor.rowcount
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()

    def close(self) -> None:
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
