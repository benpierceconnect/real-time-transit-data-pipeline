from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_compose_uses_expected_services_and_loopback_bindings():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert set(services) == {"mysql", "mongo", "cdc-service", "collector", "web"}
    assert services["mysql"]["image"] == "mysql:8.4.11"
    assert services["mongo"]["image"] == "mongo:8.0.29-noble"
    assert services["collector"]["environment"]["COLLECTOR_MODE"] == "${COLLECTOR_MODE:-synthetic}"
    assert services["cdc-service"]["environment"]["MYSQL_TABLE"] == "vehicle_observations"
    assert services["web"]["environment"]["DATA_MODE"] == "${COLLECTOR_MODE:-synthetic}"

    for name in ("mysql", "mongo", "cdc-service", "web"):
        for published_port in services[name].get("ports", []):
            assert str(published_port).startswith("127.0.0.1:"), (
                f"{name} must bind published ports to loopback for local development"
            )


def test_public_web_service_has_no_private_data_mount():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    assert "volumes" not in compose["services"]["web"]


def test_mysql_healthcheck_waits_for_final_tcp_server():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    command = compose["services"]["mysql"]["healthcheck"]["test"]
    joined = " ".join(command)
    assert "--protocol=TCP" in joined
    assert "127.0.0.1" in joined
    assert "-P 3306" in joined
    assert "localhost" not in joined


def test_cdc_healthcheck_uses_the_failure_aware_http_endpoint():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    command = compose["services"]["cdc-service"]["healthcheck"]["test"]
    assert command[:4] == ["CMD", "java", "-cp", "/app/transit-cdc-service.jar"]
    assert "com.benpierce.transitcdc.Healthcheck" in command
    assert "http://127.0.0.1:8080/health" in command
    assert "/tmp/cdc-ready" not in " ".join(command)

