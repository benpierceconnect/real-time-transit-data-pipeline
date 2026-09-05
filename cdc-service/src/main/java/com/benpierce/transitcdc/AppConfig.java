package com.benpierce.transitcdc;

import java.util.Map;
import java.util.Properties;

public record AppConfig(
        String mysqlHost,
        int mysqlPort,
        String mysqlDatabase,
        String mysqlTable,
        String debeziumUser,
        String debeziumPassword,
        int debeziumServerId,
        String offsetFile,
        String schemaHistoryFile,
        String mongoUri,
        String mongoDatabase,
        int healthPort) {

    public static AppConfig fromEnvironment() {
        Map<String, String> env = System.getenv();
        return new AppConfig(
                env.getOrDefault("MYSQL_HOST", "mysql"),
                integer(env, "MYSQL_PORT", 3306),
                env.getOrDefault("MYSQL_DATABASE", "transit_demo"),
                env.getOrDefault("MYSQL_TABLE", "vehicle_observations"),
                required(env, "DEBEZIUM_USER"),
                required(env, "DEBEZIUM_PASSWORD"),
                integer(env, "DEBEZIUM_SERVER_ID", 184054),
                env.getOrDefault("DEBEZIUM_OFFSET_FILE", "/state/offsets.dat"),
                env.getOrDefault("DEBEZIUM_SCHEMA_HISTORY_FILE", "/state/schema-history.dat"),
                env.getOrDefault("MONGO_URI", "mongodb://mongo:27017"),
                env.getOrDefault("MONGO_DATABASE", "transit_demo"),
                integer(env, "CDC_HEALTH_PORT", 8080));
    }

    public Properties debeziumProperties() {
        Properties props = new Properties();
        props.setProperty("name", "transit-event-engine");
        props.setProperty("connector.class", "io.debezium.connector.mysql.MySqlConnector");
        props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
        props.setProperty("offset.storage.file.filename", offsetFile);
        props.setProperty("offset.flush.interval.ms", "1000");
        props.setProperty("database.hostname", mysqlHost);
        props.setProperty("database.port", Integer.toString(mysqlPort));
        props.setProperty("database.user", debeziumUser);
        props.setProperty("database.password", debeziumPassword);
        props.setProperty("database.server.id", Integer.toString(debeziumServerId));
        props.setProperty("topic.prefix", "transit-events");
        props.setProperty("database.include.list", mysqlDatabase);
        props.setProperty("table.include.list", mysqlDatabase + "." + mysqlTable);
        props.setProperty("include.schema.changes", "false");
        props.setProperty("snapshot.mode", "initial");
        props.setProperty("schema.history.internal", "io.debezium.storage.file.history.FileSchemaHistory");
        props.setProperty("schema.history.internal.file.filename", schemaHistoryFile);
        props.setProperty("database.allowPublicKeyRetrieval", "true");
        props.setProperty("database.ssl.mode", "disabled");
        props.setProperty("database.connectionTimeZone", "UTC");
        props.setProperty("decimal.handling.mode", "double");
        props.setProperty("time.precision.mode", "connect");
        props.setProperty("converter.schemas.enable", "false");
        props.setProperty("errors.max.retries", "-1");
        return props;
    }

    private static String required(Map<String, String> env, String name) {
        String value = env.get(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }

    private static int integer(Map<String, String> env, String name, int fallback) {
        String value = env.get(name);
        return value == null || value.isBlank() ? fallback : Integer.parseInt(value);
    }
}
