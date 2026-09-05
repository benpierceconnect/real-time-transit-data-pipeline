from __future__ import annotations

import os
from typing import Any

from pymongo import DESCENDING, MongoClient

from serialization import serializable


class TransitRepository:
    def __init__(self, uri: str | None = None, database: str | None = None):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://mongo:27017")
        self.database_name = database or os.getenv("MONGO_DATABASE", "transit_demo")
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
        self.db = self.client[self.database_name]

    def ping(self) -> bool:
        self.client.admin.command("ping")
        return True

    def latest_vehicles(self, limit: int = 100) -> list[dict[str, Any]]:
        documents = list(
            self.db.latest_vehicles.find({}, {"_id": 0})
            .sort("observed_at", DESCENDING)
            .limit(max(1, min(limit, 500)))
        )
        return [serializable(document) for document in documents]

    def stats(self) -> dict[str, Any]:
        latest = self.db.latest_vehicles.count_documents({})
        observations = self.db.vehicle_observations.estimated_document_count()
        events = self.db.cdc_events.estimated_document_count()
        latest_document = self.db.vehicle_observations.find_one(
            {},
            {"_id": 0, "observed_at": 1, "cdc_processed_at": 1},
            sort=[("observation_id", DESCENDING)],
        )
        return {
            "latest_vehicle_count": latest,
            "observation_count": observations,
            "cdc_event_count": events,
            "latest_observation": serializable(latest_document) if latest_document else None,
        }
