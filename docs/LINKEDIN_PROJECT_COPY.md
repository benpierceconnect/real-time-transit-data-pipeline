# LinkedIn Project Copy

The exact v3 synthetic-mode fresh-start validation and owner publication approval are complete. Use this copy only once the public GitHub repository link is actually live and verified; approval alone is not publication.

## Title

Real-Time Transit Data Pipeline

## Description

Built a five-service transit event pipeline using Python, MySQL, embedded Debezium change data capture, MongoDB, Flask, Docker Compose, and an interactive Leaflet map.

The public portfolio edition uses deterministic synthetic data by default, writes observations to MySQL, propagates row-level changes into traceable MongoDB event and current-state collections, and serves pipeline metrics and vehicle locations through a Flask API and browser interface. Optional live mode reads the public MBTA V3 API with required MassDOT attribution.

Added environment-based configuration, TCP-aware MySQL readiness, failure-aware CDC lifecycle handling, an empty-volume integration validator, unit tests, Java build tests, secret scanning, synthetic data generation, data-quality checks, neutral branding, and third-party attribution.

A separate private historical analysis used a 6,767-observation data slice that covered approximately 4.85 hours, not the full runtime. After excluding incomplete trips, 20 complete trips averaged approximately 45.40 minutes and 7.56 km/h point-to-point speed. The private captured records are not published.

## Recorded validation

Validated the exact v3 application from a fresh extraction and empty Docker volumes without a manual service restart. The CDC restart count remained zero. The complete Python suite passed 45 tests and the Java build passed seven. A synchronized capture showed matching MySQL, MongoDB observation, and CDC-event totals, with seven synthetic vehicles displayed through the API and browser map.

The public packaging update changed documentation and the manifest only. This is a locally validated portfolio demonstration, not a claim of production hosting or end-to-end testing of the optional live mode.

## Skills

Python, Data Engineering, SQL, MySQL, Debezium, Change Data Capture, MongoDB, Docker, Docker Compose, Flask, API Development, Data Pipelines, ETL, Data Quality, Git
