package com.benpierce.transitcdc;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.atomic.AtomicBoolean;

public final class Main {
    private static final Logger LOGGER = LoggerFactory.getLogger(Main.class);

    private Main() {}

    public static void main(String[] args) throws Exception {
        AppConfig config = AppConfig.fromEnvironment();
        HealthState health = new HealthState();
        MongoSink sink = new MongoSink(config.mongoUri(), config.mongoDatabase());
        HealthServer healthServer = new HealthServer(config.healthPort(), health);
        DebeziumRunner runner = new DebeziumRunner(config, sink, health);
        AtomicBoolean shutdownStarted = new AtomicBoolean(false);

        Runnable shutdown = () -> {
            if (!shutdownStarted.compareAndSet(false, true)) return;
            LOGGER.info("Stopping CDC service");
            try { runner.close(); } catch (Exception exc) { LOGGER.warn("Error closing Debezium", exc); }
            try { healthServer.close(); } catch (Exception exc) { LOGGER.warn("Error closing health server", exc); }
            try { sink.close(); } catch (Exception exc) { LOGGER.warn("Error closing MongoDB", exc); }
        };

        Runtime.getRuntime().addShutdownHook(new Thread(shutdown, "shutdown-hook"));

        healthServer.start();
        try {
            runner.start();
            LOGGER.info("Transit CDC service started on health port {}; waiting for engine termination",
                    config.healthPort());
            runner.awaitTermination();
        } finally {
            shutdown.run();
        }
    }
}
