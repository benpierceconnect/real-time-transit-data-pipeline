#!/usr/bin/env bash
set -euo pipefail

python scripts/generate_synthetic_data.py --check
python scripts/secret_scan.py --public-files
python scripts/validate_project.py
python scripts/write_manifest.py --verify
python -m compileall -q collector web analysis scripts tests
node --check web/static/app.js
bash -n mysql/init/001_schema.sh mysql/init/002_create_debezium_user.sh scripts/run_local_checks.sh
pytest -q
python analysis/synthetic_trip_analysis.py
