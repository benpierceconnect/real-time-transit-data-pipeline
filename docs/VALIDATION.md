# Validation Record

## Pre-release architecture validation - September 4, 2026

A pre-release architecture passed a five-service fixture-mode run:

- Collector, MySQL, embedded Debezium CDC, MongoDB, and Flask/web ran together
- Java tests passed: 3/3
- Python tests passed: 19/19
- The runtime validator passed with 553 processed events, zero failed events, and seven current vehicles
- A later direct check captured matching totals of 560 MySQL rows, 560 MongoDB observations, and 560 CDC events
- The browser map, metrics, markers, and observation table rendered correctly
- An SLF4J version conflict was corrected by aligning the runtime binding to 1.7.36
- A local Leaflet containment fallback was added for browsers that block the external stylesheet

Private evidence and hashes are retained outside this public candidate.

## Exact public candidate v2 validation - September 5, 2026

The exact v2 archive matched its expected SHA-256 and passed its public-file, test, build, and recovered-runtime checks:

- Archive: 88 files with all 87 manifest entries matching
- Secret scan: passed on the untouched public archive
- Synthetic-data and structure validation: passed
- Python tests: 34 passed, 0 skipped
- Java tests during no-cache image build: 3 passed, 0 failures, 0 errors, 0 skipped
- All custom images built successfully
- Browser review confirmed seven synthetic vehicles, readable timestamps, contained map tiles, visible OpenStreetMap attribution, and the MassDOT/MBTA no-affiliation statement

### Fresh-start validation failure

The untouched empty-volume start did not pass:

1. The MySQL health check used `mysqladmin ping -h localhost`.
2. The official MySQL image's temporary socket-only initialization server satisfied that check while TCP port 3306 was unavailable.
3. Compose started the CDC service too early.
4. Debezium received `Connection refused` and terminated.
5. The CDC container still reported healthy because `/tmp/cdc-ready` had been written before successful connector startup.
6. The collector later connected to MySQL and continued inserting, but MongoDB remained empty.
7. The runtime validator failed with zero CDC events.

A diagnostic manual restart of only `cdc-service` after MySQL stabilized recovered the pipeline. The validator then passed with matching totals of 315 MySQL rows, 315 MongoDB observations, and 315 CDC events. That recovery proved the core application logic, but a manual restart does not satisfy the automatic fresh-start release gate.

The v2 validation evidence archive SHA-256 is:

```text
c7ba5443d6028479aa4ed6faa4a963f0427dc5e1b40ab56db41f655ff12f5a81
```

## Corrected candidate changes

This candidate addresses the v2 blockers:

- MySQL health requires TCP on `127.0.0.1:3306`, so the temporary port-0 server cannot satisfy readiness.
- CDC health uses the Java HTTP health endpoint instead of `/tmp/cdc-ready`.
- CDC readiness is set only after the Debezium connector task reports successful startup or an event is processed.
- Debezium completion is monitored with a completion callback and blocking termination future.
- Unexpected engine termination changes health to `failed`, exits the Java process, and allows Docker's restart policy to recover.
- `scripts/validate_fresh_start.py` deletes project volumes, performs a no-cache build, starts the stack, requires at least one CDC event, and requires CDC restart count `0`.
- `scripts/secret_scan.py --public-files` scans distributable files while intentionally excluding the local-only `.env`.
- The runbook scans public files before `.env` creation and uses public-files mode after local configuration exists.
- README and provenance documents distinguish the earlier private educational prototype from the independently authored public edition.
- The historical 6,767-observation slice is explicitly described as approximately 4.85 hours and not the full runtime.
- Corrected historical results of 45.40 minutes and 7.56 km/h are primary; the public synthetic analysis is separate.

## Corrected candidate static validation

Preparation-workspace results on September 5, 2026:

- Synthetic-data integrity: passed
- Public-files secret scan: passed
- Required-file, Compose-health, and release-language validation: passed
- SHA-256 manifest: 97 entries; verification passed
- Python source compilation: passed
- JavaScript syntax: passed
- Shell syntax: passed
- Dependency-free Java health classes compiled with Java 21
- Changed CDC lifecycle source compiled against API-shape stubs modeled on the documented Debezium builder callbacks
- Python tests: 40 passed, 1 skipped because Flask and PyMongo are unavailable in the preparation workspace
- Synthetic analysis: passed

The complete-environment run below resolved that preparation-workspace dependency gap and ran the exact Java tests during the no-cache CDC image build.

## Exact v3 fresh-start validation - September 5, 2026

**Result: passed.** A brand-new extraction and empty project volumes started successfully. No manual restart of the CDC service or another project service was performed. The CDC restart count remained `0`.

| Evidence item | Recorded result |
|---|---|
| Candidate archive | `real-time-transit-data-pipeline-public-candidate-v3-NOT-APPROVED-2026-09-05.zip` |
| Candidate SHA-256 | `8a37cb918277f4b2ad481fd1edb69675c53c87bd7154fafa04bbe574e6aeccad` |
| Public files | 98; all 97 manifest entries matched |
| Exact running-stack validator | Passed |
| Initial validator capture | 14 processed events, 0 failed events |
| Synchronized database capture | 84 MySQL rows; 84 MongoDB observations; 84 CDC events |
| Current vehicles | Seven `demo-vehicle-*` records |
| Python tests before local `.env` | 45 passed, 0 skipped |
| Python tests after local `.env` | 45 passed, 0 skipped |
| Java no-cache build tests | 7 passed, 0 failures, 0 errors, 0 skipped |
| Browser | Synthetic mode, seven vehicles, readable timestamps, contained tiles, attribution and no-affiliation statement verified |
| Public checks | Manifest, generator integrity, public-file secret scan, project validation passed |

Java's seven tests comprise four `HealthStateTest` tests and three `ChangeEventMapperTest` tests. Earlier three-test expectations were superseded by this complete run.

### Execution method and evidence scope

The Windows host had no `python` or `py` launcher. The documented wrapper operations were performed separately from the exact extraction: project-only reset, no-cache build, untouched first start, the exact `validate_running_stack.py` using Python 3.13 through Docker host networking, and direct restart-count inspection. Final review accepted this sequence as the intended fresh-start test; the wrapper itself was not claimed to have been invoked.

The collector remained active during evidence capture. Counts from different capture times are not measurements of one immutable database snapshot. The 84/84/84 capture is the synchronized comparison, not a performance benchmark.

The private evidence archive SHA-256 is:

```text
9f46c1dbe55da181ea3771ec728783445d6cfa0a933b3a9991d5da1f3ecf940c
```

All 40 evidence-manifest entries were verified. The complete evidence archive is kept private because it includes local paths and unrelated environment details. No raw evidence or personal machine identifiers have been added to this release.

### Security and Git evidence

Ben confirmed that the historical database password will never be reused and that the historical Mapbox token is revoked or permanently inactive. The token-list deletion was also reported in the supplied evidence. No historical credential is included here.

The validated local source had one commit, `3c99271127fc9a92c6bffd4b51e9456321471c0e`. Its tracked-file snapshot was archived and checked with the project's pattern-based scanner. This is a source-snapshot check, not a claim of exhaustive Git-object analysis or a separate commercial secret audit. The administrative release has changed documentation and therefore must not be represented as that exact old commit.

## Owner-approved public release

Ben Pierce explicitly approved public publication as `real-time-transit-data-pipeline`, limited to the reviewed v3 application and documentation-only updates recording the completed validation and approval.

Only Markdown documentation and `MANIFEST.sha256` are changed from the tested candidate. No source, dependency, Compose, test, fixture, or generated analysis file is changed. Accordingly, the documentation-inclusive release has a new manifest and archive hash, while the application tested above remains unchanged.

Run the existing manifest verifier and public-files scanner against the actual release tree before upload. Publication approval is complete; this document does not assert that a GitHub push has occurred.

## Limitations

Runtime evidence covers the default synthetic mode in the recorded Docker Desktop environment. Optional live and replay modes have not been independently established by this same run. Source publication does not authorize or establish an internet-facing production deployment. Rights notices, localhost-bound demonstration settings, and the existing license remain unchanged.
