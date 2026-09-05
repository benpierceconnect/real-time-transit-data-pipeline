#!/usr/bin/env bash
set -euo pipefail

: "${MYSQL_ROOT_PASSWORD:?MYSQL_ROOT_PASSWORD is required}"
: "${DEBEZIUM_USER:?DEBEZIUM_USER is required}"
: "${DEBEZIUM_PASSWORD:?DEBEZIUM_PASSWORD is required}"

if [[ ! "${DEBEZIUM_USER}" =~ ^[A-Za-z0-9_]+$ ]]; then
  echo "DEBEZIUM_USER may contain only letters, numbers, and underscores." >&2
  exit 1
fi

if [[ ! "${DEBEZIUM_PASSWORD}" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "For this local development script, DEBEZIUM_PASSWORD may contain only letters, numbers, periods, underscores, and hyphens." >&2
  exit 1
fi

mysql --protocol=socket -uroot -p"${MYSQL_ROOT_PASSWORD}" <<SQL
CREATE USER IF NOT EXISTS '${DEBEZIUM_USER}'@'%' IDENTIFIED BY '${DEBEZIUM_PASSWORD}';
ALTER USER '${DEBEZIUM_USER}'@'%' IDENTIFIED BY '${DEBEZIUM_PASSWORD}';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO '${DEBEZIUM_USER}'@'%';
FLUSH PRIVILEGES;
SQL
