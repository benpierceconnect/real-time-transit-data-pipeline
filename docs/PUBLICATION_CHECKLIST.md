# Public Release Checklist

**Status:** Reviewed v3 portfolio publication approved by Ben Pierce. Runtime and credential gates below are complete. Perform ordinary exact-tree and secret checks before the upload. This approval is not a production-deployment or blanket third-party-rights certification.

## Source and provenance

- [x] Public candidate contains independently authored source and documentation
- [x] Private instructional content, templates, evaluation evidence, and educational logos are absent
- [x] Private PDFs, Word documents, screenshots, and historical source-audit material are absent
- [x] Relational schema and stored field names were independently designed
- [x] File-by-file clean-room provenance review completed
- [x] Public candidate uses neutral project and application branding

## Data

- [x] Captured API fixture removed
- [x] Historical CSV sample removed
- [x] Deterministic synthetic JSON fixture added
- [x] Deterministic synthetic replay CSV added
- [x] Synthetic generator and integrity check added
- [x] Live API mode stores no data in the repository
- [x] Historical 6,767-observation data slice described as private and not the full runtime
- [x] Corrected 45.40-minute and 7.56 km/h historical results documented
- [x] Public synthetic results clearly separated from historical results

## Attribution

- [x] MassDOT/MBTA acknowledgment and no-affiliation statement added
- [x] MassDOT/MBTA logos excluded
- [x] OpenStreetMap attribution visible
- [x] OpenStreetMap tile URL matches the current community policy
- [x] Leaflet BSD 2-Clause notice included
- [x] Third-party notices added

## Security

- [x] `.env` excluded
- [x] `.env.example` contains example values only
- [x] Public-files secret-scan mode added
- [x] Historical credential-bearing files excluded
- [x] Ben confirms the historical database password will never be reused
- [x] Ben confirms the historical Mapbox token is revoked or permanently inactive
- [x] Review the supplied one-commit tracked-file snapshot scan; its limited scope is documented in `VALIDATION.md`
- [ ] Confirm the actual local committed tree matches the approved release before the first push
- [x] Review final screenshots and generated outputs for credentials and personal identifiers

## Fresh-start defect corrections

- [x] MySQL health check requires TCP on port 3306
- [x] File-based CDC readiness removed
- [x] CDC health uses the Java HTTP endpoint
- [x] CDC readiness tied to successful Debezium task startup
- [x] Unexpected Debezium termination changes health and exits the process
- [x] Empty-volume integration validator added
- [x] Integration validator requires a CDC event
- [x] Integration validator requires CDC restart count `0`
- [x] Runbook secret-scan ordering corrected

## Static reproducibility

- [x] Synthetic files match the generator
- [x] Project structure validation available
- [x] Python source compilation available
- [x] JavaScript and shell syntax checks available
- [x] XML, YAML, and JSON validation available
- [x] Java source and tests compile against local API-shape stubs in the preparation workflow
- [x] Corrected preparation-workspace static test results recorded in `docs/VALIDATION.md`
- [x] Maven tests pass on the exact corrected candidate
- [x] Complete Python suite passes on the exact corrected candidate with Flask and PyMongo installed

## Exact corrected-candidate runtime

- [x] Generate the exact corrected ZIP and record its SHA-256
- [x] Extract it into a brand-new folder
- [x] Run the public-file secret scan before creating `.env`
- [x] Build all Docker images without cache
- [x] Start from empty volumes
- [x] Process at least one CDC event without a manual restart
- [x] Confirm CDC container restart count is `0`
- [x] Run `scripts/validate_running_stack.py`
- [x] Capture MySQL, MongoDB observation, and MongoDB CDC-event counts
- [x] Confirm the web interface shows only synthetic IDs in default mode
- [x] Confirm the interface displays the active data mode
- [x] Confirm timestamps render as readable date/time values
- [x] Capture a new browser screenshot with visible OpenStreetMap attribution
- [x] Rerun the public-files secret scan and complete tests after the runtime run
- [x] Record the exact candidate ZIP SHA-256 or commit in `docs/VALIDATION.md`

## Optional demonstrations, not blockers for this synthetic-demo release

- [ ] Run replay mode, when desired
- [ ] Run live mode, when desired and attribution requirements are accepted
- [ ] Add a short demonstration video or GIF, when practical

## Final review

- [x] Inspect every file in the exact corrected candidate after the final runtime run
- [x] Review the final repository with Ben
- [x] Receive Ben's explicit publication approval
- [x] Owner approval received for the public repository name `real-time-transit-data-pipeline`
- [ ] Create/push the approved public GitHub repository and verify the uploaded files

## Approved packaging scope

Only documentation recording the completed run and approval, plus the regenerated manifest, differs from the runtime-tested v3 archive. The complete private evidence package remains excluded. Application and configuration changes would be outside this documentation-only approval.

Final runtime evidence: 45 Python tests, 7 Java tests, zero CDC restarts, and synchronized 84/84/84 storage counts. See `VALIDATION.md` for capture context and limitations.
