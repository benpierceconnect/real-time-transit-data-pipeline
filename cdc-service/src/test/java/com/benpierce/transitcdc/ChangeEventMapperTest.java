package com.benpierce.transitcdc;

import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ChangeEventMapperTest {
    @Test
    void mapsInsertEvent() throws Exception {
        String json;
        try (var stream = getClass().getResourceAsStream("/debezium_insert.json")) {
            if (stream == null) throw new IllegalStateException("fixture missing");
            json = new String(stream.readAllBytes(), StandardCharsets.UTF_8);
        }

        var mapped = new ChangeEventMapper().map(json).orElseThrow();
        assertEquals("c", mapped.operation());
        assertEquals(42L, mapped.observationId());
        assertEquals("demo-vehicle-01", mapped.vehicleId());
        assertEquals("1", mapped.after().getString("route_id"));
    }

    @Test
    void mapsDeleteEventFromBeforeDocument() throws Exception {
        String json = """
                {"payload":{"before":{"observation_id":42,"vehicle_id":"demo-vehicle-01"},"after":null,"source":{"table":"vehicle_observations"},"op":"d"}}
                """;
        var mapped = new ChangeEventMapper().map(json).orElseThrow();
        assertEquals("d", mapped.operation());
        assertEquals(42L, mapped.observationId());
        assertEquals("demo-vehicle-01", mapped.vehicleId());
        assertNull(mapped.after());
    }

    @Test
    void ignoresTombstoneAndEmptyPayloads() throws Exception {
        var mapper = new ChangeEventMapper();
        assertTrue(mapper.map(null).isEmpty());
        assertTrue(mapper.map(" ").isEmpty());
        assertTrue(mapper.map("""
                {"payload":{"before":null,"after":null,"op":"d"}}
                """).isEmpty());
    }
}
