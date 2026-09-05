package com.benpierce.transitcdc;

import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

public final class HealthState {
    private enum Phase { STARTING, READY, FAILED, STOPPED }

    private final AtomicReference<Phase> phase = new AtomicReference<>(Phase.STARTING);
    private final AtomicLong processed = new AtomicLong(0);
    private final AtomicLong failed = new AtomicLong(0);
    private final AtomicReference<String> lastError = new AtomicReference<>("");
    private final AtomicReference<Instant> lastEventAt = new AtomicReference<>();

    public void markStarting() {
        phase.set(Phase.STARTING);
    }

    public void markReady() {
        phase.set(Phase.READY);
    }

    public void processed() {
        processed.incrementAndGet();
        lastEventAt.set(Instant.now());
        phase.set(Phase.READY);
    }

    public void failed(Throwable throwable) {
        failed.incrementAndGet();
        lastError.set(message(throwable));
    }

    public void engineStopped(Throwable throwable) {
        lastError.set(message(throwable));
        phase.set(Phase.FAILED);
    }

    public void markStopped() {
        phase.set(Phase.STOPPED);
    }

    public String status() {
        return switch (phase.get()) {
            case READY -> "ready";
            case FAILED -> "failed";
            case STOPPED -> "stopped";
            case STARTING -> "starting";
        };
    }

    public boolean ready() { return phase.get() == Phase.READY; }
    public long processedCount() { return processed.get(); }
    public long failedCount() { return failed.get(); }
    public String lastError() { return lastError.get(); }
    public Instant lastEventAt() { return lastEventAt.get(); }

    private static String message(Throwable throwable) {
        if (throwable == null) return "unknown";
        String value = throwable.getMessage();
        return value == null || value.isBlank() ? throwable.getClass().getSimpleName() : value;
    }
}
