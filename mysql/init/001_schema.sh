#!/usr/bin/env bash
set -euo pipefail

: "${MYSQL_ROOT_PASSWORD:?MYSQL_ROOT_PASSWORD is required}"
: "${MYSQL_DATABASE:?MYSQL_DATABASE is required}"

mysql --protocol=socket -uroot -p"${MYSQL_ROOT_PASSWORD}" "${MYSQL_DATABASE}" <<'SQL'
CREATE TABLE IF NOT EXISTS vehicle_observations (
    observation_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    vehicle_id VARCHAR(80) NOT NULL,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    route_id VARCHAR(80),
    trip_id VARCHAR(120),
    direction_id TINYINT,
    stop_sequence INT,
    occupancy_status VARCHAR(60),
    bearing_degrees DECIMAL(6,2),
    speed_mps DECIMAL(8,3),
    observed_at DATETIME(6) NOT NULL,
    collected_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (observation_id),
    INDEX idx_vehicle_observed (vehicle_id, observed_at),
    INDEX idx_trip_progress (trip_id, stop_sequence),
    INDEX idx_observed_at (observed_at)
) ENGINE=InnoDB;
SQL
