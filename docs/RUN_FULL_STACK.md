# Fresh-Start Reproduction Runbook

The reviewed v3 application already passed the fresh-start gate on September 5, 2026, and Ben Pierce has approved publication. This runbook is retained for independent reproduction and future application changes; the documentation-only release update does not require another unchanged full-stack run.

Use this runbook from a brand-new extraction of the public release. Do not reuse old Docker volumes. Do not manually restart the CDC service during the release gate.

## 1. Verify the untouched public files

Before creating `.env`, run:

```bash
python -m pip install -r requirements-dev.txt -r collector/requirements.txt -r web/requirements.txt
python scripts/write_manifest.py --verify
python scripts/generate_synthetic_data.py --check
python scripts/secret_scan.py --public-files
python scripts/validate_project.py
pytest -q
```

The secret scan must pass on the distributable file set.

## 2. Configure local-only credentials

```bash
cp .env.example .env
```

Replace the three `change-me-...` passwords with new disposable local-only values. Keep:

```dotenv
COLLECTOR_MODE=synthetic
```

Never commit or upload `.env`.

## 3. Validate Compose configuration

```bash
docker compose --env-file .env config --quiet
```

## 4. Run the destructive empty-volume release gate

```bash
python scripts/validate_fresh_start.py --confirm-reset --keep-running
```

This command:

1. Removes the project's existing Docker containers and volumes.
2. Builds all custom images without cache.
3. Starts all five services.
4. Waits for the exact runtime validator to observe at least one CDC event.
5. Requires synthetic vehicle IDs and readable timestamps.
6. Requires the CDC container restart count to remain `0`.
7. Leaves the validated stack running for direct checks.

Expected final lines:

```text
Running-stack validation passed.
Fresh-start integration validation passed.
CDC processed at least one event and the CDC container restart count remained 0.
```

A manual `docker compose restart cdc-service` invalidates the release run.

## 5. Confirm service status

```bash
docker compose --env-file .env ps
```

All five services should be running. MySQL, MongoDB, CDC, and web should report healthy.

## 6. Direct database checks

MySQL:

```bash
docker compose --env-file .env exec mysql sh -lc 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "SELECT COUNT(*) AS rows_logged FROM vehicle_observations;"'
```

MongoDB:

```bash
docker compose --env-file .env exec mongo mongosh --quiet --eval 'db.getSiblingDB("transit_demo").vehicle_observations.countDocuments({})'
docker compose --env-file .env exec mongo mongosh --quiet --eval 'db.getSiblingDB("transit_demo").cdc_events.countDocuments({})'
docker compose --env-file .env exec mongo mongosh --quiet --eval 'db.getSiblingDB("transit_demo").latest_vehicles.findOne({}, {_id: 0})'
```

Because the collector remains active, counts can differ by one collection cycle while commands are being run. They must be increasing and internally plausible.

## 7. Browser review

Open:

```text
http://localhost:3000
```

Confirm:

- The notice says `Current data mode: synthetic`
- Seven synthetic vehicles appear
- Vehicle IDs begin with `demo-vehicle-`
- Metrics increase
- Observation timestamps display as readable dates and times
- Map tiles remain inside the map container
- `© OpenStreetMap contributors` is visible
- The MassDOT/MBTA no-affiliation statement appears

## 8. Final local checks after `.env` exists

```bash
python scripts/generate_synthetic_data.py --check
python scripts/secret_scan.py --public-files
python scripts/validate_project.py
pytest -q
```

`--public-files` intentionally excludes the local-only `.env` while continuing to scan all distributable project files.

## 9. Capture release evidence

Save:

- Exact candidate ZIP SHA-256
- `docker compose --env-file .env ps`
- Fresh-start validator output
- CDC restart count of `0`
- Java and Python test results
- MySQL row count
- MongoDB observation and CDC-event counts
- One sanitized synthetic MongoDB document
- `/api/stats` output
- Browser screenshot with synthetic mode, readable timestamps, and visible attribution
- Final public-files secret-scan output

Do not capture `.env` or passwords.

## 10. Stop and remove test volumes

```bash
docker compose --env-file .env down -v
```

## Recorded execution and scope

The September 5 Windows host did not expose a `python` or `py` launcher. The documented reset, no-cache build, first start, exact running-stack validator, and restart-count checks were executed separately, using Python 3.13 through Docker for the runtime script. Final review accepted that equivalent sequence. No manual service restart occurred.

Recorded results: 45 Python tests with zero skips, seven Java tests with no failures/errors/skips, zero CDC restarts, and synchronized counts of 84 MySQL rows, 84 MongoDB observations, and 84 CDC events. Those are recorded capture values, not mandatory exact counts for another active run.

## Release record

Historical credential retirement, final review, and Ben's explicit publication approval are recorded in `VALIDATION.md` and `RELEASE_REVIEW.md`. The public release differs from the tested v3 archive only in Markdown documentation and its manifest. No further owner approval or unchanged Docker rerun is needed for that packaging scope.

Application changes or an internet-facing deployment require separate review. Optional live/replay modes are not covered by the recorded synthetic-mode runtime result. Never upload local credentials or private evidence.
