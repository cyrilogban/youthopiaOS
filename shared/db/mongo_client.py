from __future__ import annotations

from shared.config.settings import settings
from shared.db.mongo import TelemetryMongoGateway


def get_mongo_gateway() -> TelemetryMongoGateway:
    return TelemetryMongoGateway(settings.MONGO_URI)


def get_mongo_client():
    return get_mongo_gateway().connect().client
