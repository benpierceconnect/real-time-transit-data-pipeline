package com.benpierce.transitcdc;

import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import io.debezium.engine.format.Json;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public final class DebeziumRunner implements AutoCloseable {
    private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumRunner.class);

    private final DebeziumEngine<ChangeEvent<String, String>> engine;
    private final ExecutorService executor;
    private final ChangeEventMapper mapper;
    private final MongoSink sink;
    private final HealthState health;
    private final CompletableFuture<Void> termination = new CompletableFuture<>();
    private final AtomicBoolean closing = new AtomicBoolean(false);

    public DebeziumRunner(AppConfig config, MongoSink sink, HealthState health) {
        this.mapper = new ChangeEventMapper();
        this.sink = sink;
        this.health = health;
        this.executor = Executors.newSingleThreadExecutor(runnable -> {
            Thread thread = new Thread(runnable, "debezium-engine");
            thread.setDaemon(false);
            return thread;
        });
        this.engine = DebeziumEngine.create(Json.class)
                .using(config.debeziumProperties())
                .using((DebeziumEngine.CompletionCallback) this::handleCompletion)
                .using(new DebeziumEngine.ConnectorCallback() {
                    @Override
                    public void connectorStarted() {
                        LOGGER.info("Debezium connector started");
                    }

                    @Override
                    public void taskStarted() {
                        health.markReady();
                        LOGGER.info("Debezium connector task started; CDC service is ready");
                    }

                    @Override
                    public void taskStopped() {
                        if (!closing.get()) {
                            health.markStarting();
                            LOGGER.warn("Debezium connector task stopped");
                        }
                    }
                })
                .notifying(this::handle)
                .build();
    }

    public void start() {
        health.markStarting();
        executor.execute(() -> {
            try {
                engine.run();
            } catch (Throwable throwable) {
                handleCompletion(false, "Debezium engine threw an exception", throwable);
            } finally {
                if (!termination.isDone()) {
                    handleCompletion(true, "Debezium engine returned", null);
                }
            }
        });
        LOGGER.info("Debezium engine submitted; waiting for connector task startup");
    }

    public void awaitTermination() throws Exception {
        try {
            termination.get();
        } catch (InterruptedException exc) {
            Thread.currentThread().interrupt();
            throw exc;
        } catch (ExecutionException exc) {
            Throwable cause = exc.getCause();
            if (cause instanceof Exception exception) {
                throw exception;
            }
            throw new RuntimeException(cause);
        }
    }

    private void handleCompletion(boolean success, String message, Throwable error) {
        if (termination.isDone()) return;

        if (closing.get()) {
            health.markStopped();
            termination.complete(null);
            return;
        }

        String detail = message == null || message.isBlank()
                ? "Debezium engine terminated unexpectedly"
                : message;
        Throwable failure = error == null ? new IllegalStateException(detail) : error;
        health.engineStopped(failure);
        LOGGER.error("Debezium engine terminated unexpectedly: success={} message={}",
                success, detail, failure);
        termination.completeExceptionally(failure);
    }

    private void handle(ChangeEvent<String, String> event) {
        try {
            mapper.map(event.value()).ifPresent(change -> {
                sink.accept(change);
                health.processed();
                LOGGER.debug("Processed CDC event observation_id={} operation={}",
                        change.observationId(), change.operation());
            });
        } catch (Exception exc) {
            health.failed(exc);
            LOGGER.error("Unable to process CDC event", exc);
        }
    }

    @Override
    public void close() throws IOException {
        if (!closing.compareAndSet(false, true)) return;

        IOException closeFailure = null;
        try {
            engine.close();
        } catch (IOException exc) {
            closeFailure = exc;
        } finally {
            executor.shutdown();
            try {
                if (!executor.awaitTermination(15, TimeUnit.SECONDS)) {
                    executor.shutdownNow();
                }
            } catch (InterruptedException exc) {
                Thread.currentThread().interrupt();
                executor.shutdownNow();
            }
            health.markStopped();
            termination.complete(null);
        }

        if (closeFailure != null) throw closeFailure;
    }
}
