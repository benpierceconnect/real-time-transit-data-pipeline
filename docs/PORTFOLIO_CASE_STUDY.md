# Portfolio Case Study

## Problem

Build a reproducible system that collects transit vehicle observations, stores them relationally, captures every row-level change, maintains traceable event history and current state in a document database, and exposes the results through an API and map.

## Architecture

- Python collector
- MySQL source table with row-based binary logging
- Embedded Debezium CDC service in Java
- MongoDB event, observation, and current-state collections
- Flask JSON API
- Leaflet/OpenStreetMap browser map
- Docker Compose orchestration

## Reliability work

- Deterministic synthetic data for offline demonstration
- Optional live public-data mode
- Environment-based configuration
- TCP-aware MySQL health check that waits for the final port-3306 server
- CDC readiness tied to connector-task startup rather than a startup file
- Process failure when the Debezium engine terminates unexpectedly, allowing Docker restart policy to recover
- Empty-volume release validation that requires a CDC event and zero CDC restarts
- Structured logs and visible error handling
- Java and Python tests
- Secret scanning with separate public-files and local-environment modes
- Traceable CDC event storage
- Latest-state upserts by vehicle identifier

## Historical analytical result

A private educational prototype produced a preserved 6,767-observation slice spanning 36 trips, 13 vehicles, and approximately 4.85 hours. That slice was not the full runtime. A later audit removed three incomplete trips. The corrected primary result uses 20 trips that reached stop sequence 24 and estimates:

- 45.40-minute average completion time
- 7.56 km/h average point-to-point speed

The private captured data is not distributed in this repository. The public synthetic analysis is separate.

## Public synthetic analysis

The committed synthetic replay data contains 186 observations, six complete trips, and two incomplete trips. It is designed to demonstrate deterministic analysis, transparent completeness rules, and offline testing. Its generated values are not substitutes for the historical private-prototype findings.

## Validation

The exact v3 application passed a fresh extraction and empty-volume synthetic start on September 5, 2026, without a manual service restart. The CDC restart count remained zero and the exact running-stack validator passed with no failed events.

A synchronized capture recorded 84 MySQL rows, 84 MongoDB observations, and 84 CDC events. Seven synthetic vehicles were visible through the API and browser map. The complete Python suite passed 45 tests with zero skips; the no-cache Java build passed seven tests with no failures, errors, or skips.

The previous candidate's first-start readiness defect is documented in `VALIDATION.md`, along with its correction. The private evidence was reviewed before Ben Pierce's explicit publication approval. The final release adds only documentation and manifest updates; it does not change tested application files.

## Limitations

- Community OpenStreetMap tiles are appropriate only for compliant, modest portfolio traffic.
- Live data availability and fields can change without notice.
- The local demonstration is not designed as a highly available production deployment.
- Historical captured data is private and not included.
- The validated scope is the local default synthetic mode, not optional live/replay runtime behavior or production hardening.
