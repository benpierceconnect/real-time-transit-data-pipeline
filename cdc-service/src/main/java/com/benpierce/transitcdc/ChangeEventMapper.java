package com.benpierce.transitcdc;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.bson.Document;

import java.io.IOException;
import java.util.Optional;

public final class ChangeEventMapper {
    private final ObjectMapper objectMapper;

    public ChangeEventMapper() {
        this(new ObjectMapper());
    }

    ChangeEventMapper(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public Optional<MappedChange> map(String rawValue) throws IOException {
        if (rawValue == null || rawValue.isBlank()) {
            return Optional.empty();
        }

        JsonNode root = objectMapper.readTree(rawValue);
        JsonNode payload = root.has("payload") ? root.path("payload") : root;
        String operation = payload.path("op").asText("unknown");
        JsonNode afterNode = payload.path("after");
        JsonNode beforeNode = payload.path("before");
        JsonNode sourceNode = payload.path("source");

        if ((operation.equals("d") || operation.equals("t")) && afterNode.isMissingNode()) {
            return Optional.empty();
        }
        if ((afterNode.isMissingNode() || afterNode.isNull())
                && (beforeNode.isMissingNode() || beforeNode.isNull())) {
            return Optional.empty();
        }

        Document after = toDocument(afterNode);
        Document before = toDocument(beforeNode);
        Document source = toDocument(sourceNode);
        Document active = after != null ? after : before;
        Long observationId = numberAsLong(active == null ? null : active.get("observation_id"));
        String vehicleId = active == null ? null : active.getString("vehicle_id");

        return Optional.of(new MappedChange(
                operation,
                observationId,
                vehicleId,
                before,
                after,
                source,
                rawValue));
    }

    private Document toDocument(JsonNode node) {
        if (node == null || node.isMissingNode() || node.isNull()) {
            return null;
        }
        return Document.parse(node.toString());
    }

    private Long numberAsLong(Object value) {
        return value instanceof Number number ? number.longValue() : null;
    }
}
