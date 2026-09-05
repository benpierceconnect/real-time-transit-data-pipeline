from pathlib import Path

from transit_collector.replay import replay_batches


CSV_TEXT = """vehicle_id,latitude,longitude,route_id,trip_id,direction_id,stop_sequence,occupancy_status,bearing_degrees,speed_mps,observed_at
v1,42.1,-71.1,1,t1,0,1,MANY_SEATS_AVAILABLE,90,5,2026-01-01T00:00:00Z
v2,42.2,-71.2,1,t2,1,2,FEW_SEATS_AVAILABLE,180,6,2026-01-01T00:00:10Z
v3,42.3,-71.3,1,t3,0,3,,270,,2026-01-01T00:00:20Z
"""


def test_replay_batches_respects_batch_size(tmp_path: Path):
    path = tmp_path / "observations.csv"
    path.write_text(CSV_TEXT, encoding="utf-8")
    batches = list(replay_batches(path, batch_size=2))
    assert [len(batch) for batch in batches] == [2, 1]
    assert batches[0][0].vehicle_id == "v1"
    assert batches[1][0].trip_id == "t3"
    assert batches[1][0].speed_mps is None
