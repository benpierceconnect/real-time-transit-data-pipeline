# Release Review

**Verdict:** Approved by Ben Pierce for public portfolio publication
**Repository name:** `real-time-transit-data-pipeline`
**Runtime evidence date:** September 5, 2026
**Scope:** Reviewed v3 application with documentation-only release records
**Upload status:** Approval is recorded; this file does not certify that a GitHub push has occurred.

## Approval

Ben Pierce explicitly approved public publication as `real-time-transit-data-pipeline`, limited to the reviewed v3 application and documentation-only updates recording the completed validation and approval.

The tested application is unchanged. This release updates only Markdown documentation and regenerates the manifest. No new application build or unchanged Docker rerun is required solely for these administrative changes.

## Identity and validation

Tested v3 archive SHA-256:

```text
8a37cb918277f4b2ad481fd1edb69675c53c87bd7154fafa04bbe574e6aeccad
```

Private validation evidence archive SHA-256:

```text
9f46c1dbe55da181ea3771ec728783445d6cfa0a933b3a9991d5da1f3ecf940c
```

The supplied run and final review establish:

- 98 candidate files, with all 97 candidate manifest entries matching
- All 40 evidence manifest entries matching
- Brand-new extraction and empty project volumes
- No manual recovery restart; CDC restart count 0
- Exact running-stack validator passed and CDC failed-event count 0
- Synchronized counts of 84 MySQL rows, 84 MongoDB observations, and 84 CDC events
- Seven synthetic vehicles rendered with readable timestamps and contained map tiles
- Python: 45 passed, 0 skipped, before and after local `.env`
- Java: 7 passed, no failures, errors, or skips
- Manifest, synthetic integrity, public-file scan, and project checks passed
- Attribution and no-affiliation notice visible in the reviewed browser screenshot

Windows ran the wrapper's constituent operations individually, with the exact running-stack validator executed through Docker. Final review accepted that equivalent sequence. It did not rely on the earlier diagnostic restart.

## Earlier defect and resolution

The previous public candidate's socket-based MySQL health check accepted the temporary initialization server. CDC started before TCP readiness, terminated on connection failure, and kept an incorrect ready file. That run failed and was not approved.

The reviewed v3 application requires MySQL TCP readiness, uses failure-aware CDC HTTP health, observes Debezium engine completion, and checks zero CDC restarts. The successful first-start evidence closes that reported defect.

## Public boundary and analytical context

Only the already reviewed independently authored implementation, synthetic data, analysis, and documentation are distributed. Private instructional content, templates, historical captured records, credentials, and complete runtime evidence remain excluded. Neutral branding and existing third-party attribution remain unchanged.

The earlier private 6,767-observation slice spans approximately 4.85 hours, 36 trips, and 13 vehicles, not the full runtime. Corrected historical findings use 20 complete trips and are 45.40 minutes and 7.56 km/h. These values are separate from the public synthetic analysis and are not a claim that private data is available here.

## Security and license

Ben confirmed historical database-password non-reuse and Mapbox-token retirement. The current public file set is checked with the project's pattern-based scanner. The supplied one-commit Git snapshot scan was accepted within its documented scope; it is not exhaustive Git-object or secret-detection assurance.

The original `LICENSE`, notices, third-party terms, and localhost-bound demo configuration are unchanged. This technical release review is not a legal determination or production security certification.

## Publication handoff

The documentation-only release has a regenerated `MANIFEST.sha256`; it must not be described as byte-identical to the older tested ZIP or local commit. Verify that manifest and the actual tracked tree before upload. Do not include `.env` or the private evidence archive.

Owner authorization is complete. The remaining administrative action is to create/push the public repository from an authenticated GitHub environment and verify the public link. No further approval round is requested for the documented scope.
