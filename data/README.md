# Public Demonstration Data

All committed data in this repository is synthetic and deterministic.

- `fixtures/synthetic_vehicle_snapshot.json` provides seven API-shaped vehicle observations for the default collector mode.
- `sample/synthetic_trip_observations.csv` provides a replayable sequence of complete and incomplete synthetic trips for testing and analysis.

Generate or verify both files with:

```bash
python scripts/generate_synthetic_data.py
python scripts/generate_synthetic_data.py --check
```

Live mode can optionally read the public MBTA V3 API. Live data is not committed to the repository. Use of MassDOT/MBTA data is subject to the MassDOT developer terms and attribution requirements.
