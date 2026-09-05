import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_payload():
    path = Path(__file__).parents[2] / "data" / "fixtures" / "synthetic_vehicle_snapshot.json"
    return json.loads(path.read_text(encoding="utf-8"))
