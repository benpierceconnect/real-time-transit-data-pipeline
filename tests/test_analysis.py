from pathlib import Path
import json

from synthetic_trip_analysis import analyze, load_observations

ROOT = Path(__file__).parents[1]
DATA = ROOT / "data" / "sample" / "synthetic_trip_observations.csv"
SUMMARY = ROOT / "analysis" / "results" / "synthetic_analysis_summary.json"


def test_published_synthetic_analysis_summary():
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert payload["observation_count"] == 186
    assert payload["trip_count"] == 8
    assert payload["vehicle_count"] == 4
    assert payload["complete_trip_count"] == 6
    assert payload["incomplete_trip_count"] == 2
    assert payload["mean_complete_duration_minutes"] > 30
    assert payload["mean_complete_point_to_point_speed_kmh"] > 0


def test_synthetic_analysis_reproduces_committed_summary():
    frame = load_observations(DATA)
    summary, complete, incomplete = analyze(frame)
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary.observation_count == payload["observation_count"]
    assert summary.complete_trip_count == 6
    assert summary.incomplete_trip_count == 2
    assert (complete["end_sequence"] >= 24).all()
    assert (incomplete["end_sequence"] < 24).all()
