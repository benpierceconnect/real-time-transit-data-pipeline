package com.benpierce.transitcdc;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class HealthStateTest {
    @Test
    void startsUnreadyAndBecomesReadyWhenTaskStarts() {
        HealthState state = new HealthState();
        assertEquals("starting", state.status());
        assertFalse(state.ready());

        state.markReady();
        assertEquals("ready", state.status());
        assertTrue(state.ready());
    }

    @Test
    void processedEventMarksServiceReadyAndRecordsTimestamp() {
        HealthState state = new HealthState();
        state.processed();

        assertEquals(1, state.processedCount());
        assertEquals("ready", state.status());
        assertNotNull(state.lastEventAt());
    }

    @Test
    void engineTerminationMakesReadinessFail() {
        HealthState state = new HealthState();
        state.markReady();
        state.engineStopped(new IllegalStateException("connection refused"));

        assertEquals("failed", state.status());
        assertFalse(state.ready());
        assertEquals("connection refused", state.lastError());
    }

    @Test
    void eventFailureIsCountedWithoutPretendingTheEventSucceeded() {
        HealthState state = new HealthState();
        state.markReady();
        state.failed(new IllegalArgumentException("bad event"));

        assertEquals(1, state.failedCount());
        assertEquals(0, state.processedCount());
        assertEquals("bad event", state.lastError());
    }
}
