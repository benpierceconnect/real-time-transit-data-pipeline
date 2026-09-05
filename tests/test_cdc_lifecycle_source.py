from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_cdc_source_is_failure_aware():
    runner = (ROOT / "cdc-service/src/main/java/com/benpierce/transitcdc/DebeziumRunner.java").read_text(encoding="utf-8")
    main = (ROOT / "cdc-service/src/main/java/com/benpierce/transitcdc/Main.java").read_text(encoding="utf-8")
    health = (ROOT / "cdc-service/src/main/java/com/benpierce/transitcdc/HealthState.java").read_text(encoding="utf-8")

    assert "CompletionCallback" in runner
    assert "ConnectorCallback" in runner
    assert "handleCompletion" in runner
    assert "engineStopped" in runner
    assert "awaitTermination" in runner
    assert "runner.awaitTermination()" in main
    assert "finally" in main
    assert "shutdown.run()" in main
    assert 'case FAILED -> "failed"' in health
    assert "/tmp/cdc-ready" not in runner
