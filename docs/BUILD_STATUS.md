# Build Status

**Current status:** Reviewed v3 runtime passed; publication approved by Ben Pierce. The final packaging changes are documentation and manifest updates only. GitHub upload is a separate operation, not a completed build test.

## Completed on the validated pre-release architecture

- Five-service Docker Compose build
- MySQL, collector, Debezium CDC, MongoDB, and Flask operation
- Java tests: 3 passed
- Python tests: 19 passed
- End-to-end change-event flow
- Browser map validation
- Secret and structure checks
- SLF4J 1.7.36 runtime alignment
- Local Leaflet containment fallback

## Completed on exact public candidate v2

- Archive and manifest verification
- Untouched public-file secret scan
- Synthetic data and project validation
- Python tests: 34 passed, 0 skipped
- Java tests: 3 passed, 0 failed, 0 errors, 0 skipped
- No-cache custom image build
- Browser validation of synthetic mode, readable timestamps, contained tiles, and attribution
- Core pipeline recovery after a diagnostic CDC restart

## v2 release blocker

The v2 exact candidate failed its untouched empty-volume start because MySQL readiness accepted a temporary socket-only server and CDC readiness remained positive after Debezium stopped. A manual CDC restart recovered the pipeline but did not satisfy the release gate.

## Corrected-candidate changes completed in source

- TCP-only MySQL health check for final port-3306 readiness
- Failure-aware CDC HTTP health check
- Debezium connector lifecycle callback handling
- Process termination after unexpected engine completion
- Empty-volume integration validator with zero-restart assertion
- Public-files secret-scan mode
- Corrected runbook ordering
- Historical analysis context and corrected metrics in public documentation
- Additional Python and Java tests

## Corrected-candidate preparation-workspace validation

- SHA-256 manifest: 97 entries; verification passed
- Synthetic-data integrity: passed
- Public-files secret scan: passed
- Project and release-language validation: passed
- Python compilation: passed
- JavaScript and shell syntax: passed
- Python tests: 40 passed, 1 dependency-related skip
- Dependency-free Java health classes compiled with Java 21
- Changed CDC lifecycle source compiled against documented API-shape stubs

## Exact v3 complete-environment validation - September 5, 2026

- New extraction and empty project volumes
- No-cache build of all custom images
- All five services started without a manual service restart
- CDC restart count: 0
- Running-stack validator: passed
- CDC failed events: 0
- Synchronized counts: 84 MySQL rows, 84 MongoDB observations, 84 CDC events
- Seven synthetic vehicles exposed by the API and rendered in Chrome
- Python tests: 45 passed, 0 skipped, before and after `.env` creation
- Java tests: 7 passed, no failures, errors, or skips
- Public-files secret scan, synthetic integrity, manifest, and project validation: passed

The Windows host lacked a Python launcher, so the wrapper's operations were performed separately and the exact running-stack validator ran through Docker. This equivalent sequence was accepted in final review. No recovery restart occurred.

## Approved documentation-only release

Ben Pierce explicitly approved public publication as `real-time-transit-data-pipeline`, limited to the reviewed v3 application and documentation-only updates recording the completed validation and approval.

Application files and test inputs remain byte-identical to the tested v3 archive. The updated manifest identifies the current documentation-inclusive file set. The prior preparation-workspace skip above is historical; the complete-environment v3 evidence contains no skipped Python tests.

No additional unchanged Docker run is required for this administrative documentation update. Optional live/replay runtime demonstrations and production hardening are not claimed.
