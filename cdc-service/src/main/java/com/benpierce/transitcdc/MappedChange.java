package com.benpierce.transitcdc;

import org.bson.Document;

public record MappedChange(
        String operation,
        Long observationId,
        String vehicleId,
        Document before,
        Document after,
        Document source,
        String rawEvent) {
}
