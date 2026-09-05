from __future__ import annotations

import logging
import signal
import threading
import time

from .api_client import TransitApiClient, load_synthetic_snapshot
from .config import CollectorConfig
from .mysql_store import MySqlStore
from .replay import replay_batches

LOGGER = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def run_periodic(config: CollectorConfig, store: MySqlStore, stop: threading.Event) -> None:
    client = TransitApiClient(config.transit_api_url, config.transit_api_key)
    while not stop.is_set():
        started = time.monotonic()
        try:
            observations = (
                client.fetch()
                if config.mode == "live"
                else load_synthetic_snapshot(
                    config.synthetic_snapshot_path,
                    refresh_timestamps=config.refresh_synthetic_timestamps,
                )
            )
            inserted = store.insert_many(observations)
            LOGGER.info("Inserted %s observations in %s mode", inserted, config.mode)
        except Exception:
            LOGGER.exception("Collection cycle failed")

        elapsed = time.monotonic() - started
        stop.wait(max(0.0, config.interval_seconds - elapsed))


def run_replay(config: CollectorConfig, store: MySqlStore, stop: threading.Event) -> None:
    total = 0
    for batch in replay_batches(config.replay_csv_path, config.replay_batch_size):
        if stop.is_set():
            break
        inserted = store.insert_many(batch)
        total += inserted
        LOGGER.info("Replayed %s observations; cumulative total=%s", inserted, total)
        stop.wait(config.replay_delay_seconds)
    LOGGER.info("Replay complete; inserted=%s", total)


def main() -> None:
    config = CollectorConfig.from_env()
    configure_logging(config.log_level)
    stop = threading.Event()

    def request_stop(signum, _frame):
        LOGGER.info("Received signal %s; stopping collector", signum)
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    store = MySqlStore(config)
    try:
        store.connect()
        if config.mode == "replay":
            run_replay(config, store, stop)
        else:
            run_periodic(config, store, stop)
    finally:
        store.close()


if __name__ == "__main__":
    main()
