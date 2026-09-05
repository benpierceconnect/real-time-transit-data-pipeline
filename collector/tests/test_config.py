import pytest

from transit_collector.config import CollectorConfig


def test_config_from_environment(monkeypatch):
    monkeypatch.setenv("MYSQL_PASSWORD", "local-test-password")
    monkeypatch.setenv("COLLECTOR_MODE", "replay")
    monkeypatch.setenv("REPLAY_BATCH_SIZE", "0")
    monkeypatch.setenv("REPLAY_DELAY_SECONDS", "-1")

    config = CollectorConfig.from_env()

    assert config.mysql_password == "local-test-password"
    assert config.mode == "replay"
    assert config.replay_batch_size == 1
    assert config.replay_delay_seconds == 0.0


def test_config_defaults_to_synthetic_mode(monkeypatch):
    monkeypatch.setenv("MYSQL_PASSWORD", "local-test-password")
    monkeypatch.delenv("COLLECTOR_MODE", raising=False)
    assert CollectorConfig.from_env().mode == "synthetic"


def test_config_requires_mysql_password(monkeypatch):
    monkeypatch.delenv("MYSQL_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="MYSQL_PASSWORD is required"):
        CollectorConfig.from_env()


def test_config_rejects_unknown_mode(monkeypatch):
    monkeypatch.setenv("MYSQL_PASSWORD", "local-test-password")
    monkeypatch.setenv("COLLECTOR_MODE", "unknown")
    with pytest.raises(ValueError, match="synthetic, live, or replay"):
        CollectorConfig.from_env()
