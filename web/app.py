from __future__ import annotations

import logging
import os

from flask import Flask, jsonify, render_template, request

from repository import TransitRepository

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger(__name__)

app = Flask(__name__)
repository = TransitRepository()


def _data_mode() -> str:
    value = os.getenv("DATA_MODE", "synthetic").strip().lower()
    return value if value in {"synthetic", "replay", "live"} else "unknown"


def _map_config() -> dict[str, str]:
    return {
        "tile_url": (
            os.getenv("MAP_TILE_URL")
            or "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        ),
        "attribution": (
            '&copy; <a href="https://www.openstreetmap.org/copyright">'
            "OpenStreetMap contributors</a>"
        ),
        "report_url": "https://www.openstreetmap.org/fixthemap",
    }


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return response


@app.get("/")
def index():
    return render_template(
        "index.html",
        map_config=_map_config(),
        data_mode=_data_mode(),
    )


@app.get("/api/vehicles")
def vehicles():
    limit = request.args.get("limit", default=100, type=int)
    try:
        return jsonify({"data": repository.latest_vehicles(limit=limit)})
    except Exception:
        LOGGER.exception("Unable to load latest vehicles")
        return jsonify({"error": "The data service is temporarily unavailable"}), 503


@app.get("/api/stats")
def stats():
    try:
        payload = repository.stats()
        payload["data_mode"] = _data_mode()
        return jsonify(payload)
    except Exception:
        LOGGER.exception("Unable to load transit statistics")
        return jsonify({"error": "The data service is temporarily unavailable"}), 503


@app.get("/health")
def health():
    try:
        repository.ping()
        return jsonify({"status": "ok", "data_mode": _data_mode()})
    except Exception:
        LOGGER.exception("Health check failed")
        return jsonify({"status": "unavailable", "data_mode": _data_mode()}), 503
