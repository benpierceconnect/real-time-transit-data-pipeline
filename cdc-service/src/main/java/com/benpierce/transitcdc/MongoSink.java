package com.benpierce.transitcdc;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Indexes;
import com.mongodb.client.model.ReplaceOptions;
import org.bson.Document;

import java.time.Instant;

import static com.mongodb.client.model.Filters.eq;

public final class MongoSink implements AutoCloseable {
    private final MongoClient client;
    private final MongoCollection<Document> eventCollection;
    private final MongoCollection<Document> observationCollection;
    private final MongoCollection<Document> latestCollection;

    public MongoSink(String uri, String databaseName) {
        this.client = MongoClients.create(uri);
        MongoDatabase database = client.getDatabase(databaseName);
        this.eventCollection = database.getCollection("cdc_events");
        this.observationCollection = database.getCollection("vehicle_observations");
        this.latestCollection = database.getCollection("latest_vehicles");
        createIndexes();
        database.runCommand(new Document("ping", 1));
    }

    private void createIndexes() {
        eventCollection.createIndex(Indexes.ascending("processed_at"));
        observationCollection.createIndex(Indexes.ascending("observation_id"));
        observationCollection.createIndex(Indexes.compoundIndex(
                Indexes.ascending("vehicle_id"), Indexes.descending("observed_at")));
        latestCollection.createIndex(Indexes.ascending("vehicle_id"));
    }

    public void accept(MappedChange change) {
        String processedAt = Instant.now().toString();
        Document event = new Document()
                .append("operation", change.operation())
                .append("observation_id", change.observationId())
                .append("vehicle_id", change.vehicleId())
                .append("before", change.before())
                .append("after", change.after())
                .append("source", change.source())
                .append("processed_at", processedAt);
        eventCollection.insertOne(event);

        if (change.after() == null || change.observationId() == null) {
            return;
        }

        Document observation = new Document(change.after());
        observation.append("cdc_operation", change.operation());
        observation.append("cdc_processed_at", processedAt);
        observationCollection.replaceOne(
                eq("observation_id", change.observationId()),
                observation,
                new ReplaceOptions().upsert(true));

        if (change.vehicleId() != null) {
            latestCollection.replaceOne(
                    eq("vehicle_id", change.vehicleId()),
                    observation,
                    new ReplaceOptions().upsert(true));
        }
    }

    @Override
    public void close() {
        client.close();
    }
}
