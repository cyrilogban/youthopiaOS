from __future__ import annotations

import pytest

from core.config import load_config
from core.identity import IdentityResolver
from core.telegram_runtime import register_group_chat
from shared.db.mongo import TelemetryMongoGateway
from shared.services.container import build_services
from shared.services.chat_service import ChatService
from shared.services.user_service import UserService
from shared.services.xp_service import XPService, calculate_level


class FakeSupabaseGateway:
    def __init__(self) -> None:
        self.tables = {
            "users": {},
            "telegram_accounts": {},
            "telegram_chats": {},
            "bot_chat_memberships": {},
            "chat_bot_settings": {},
            "chat_subscriptions": {},
            "user_subscriptions": {},
            "xp_transactions": {},
            "user_levels": {},
        }
        self.counter = 0

    def _id(self) -> str:
        self.counter += 1
        return f"id-{self.counter}"

    async def insert(self, table, payload):
        record = {"id": self._id(), **payload}
        if table == "users":
            record.setdefault("total_xp", 0)
            record.setdefault("level", 1)
            record.setdefault("trust_score", 100)
        self.tables[table][record["id"]] = record
        return record

    async def upsert(self, table, payload, *, on_conflict=None):
        keys = [key.strip() for key in (on_conflict or "id").split(",")]
        for record in self.tables[table].values():
            if all(record.get(key) == payload.get(key) for key in keys):
                record.update(payload)
                return record
        return await self.insert(table, payload)

    async def find_one(self, table, column, value):
        for record in self.tables[table].values():
            if record.get(column) == value:
                return record
        return None

    async def find_one_multi(self, table, filters):
        for record in self.tables[table].values():
            if all(record.get(column) == value for column, value in filters.items()):
                return record
        return None

    async def find_many(self, table, filters):
        return [
            record
            for record in self.tables[table].values()
            if all(record.get(column) == value for column, value in filters.items())
        ]

    async def get_by_id(self, table, record_id):
        return self.tables[table][record_id]

    async def update_by_id(self, table, record_id, payload):
        self.tables[table][record_id].update(payload)
        return self.tables[table][record_id]


class TelegramUser:
    id = 123
    username = "grace"
    first_name = "Grace"
    last_name = "Doe"
    is_bot = False


class TelegramChat:
    id = -100123456789
    type = "supergroup"
    title = "YOUTHOPIA BIBLE COMMUNITY"
    username = None


class TelegramMessage:
    chat = TelegramChat()


@pytest.mark.asyncio
async def test_identity_resolver_reuses_one_user_for_telegram_account():
    db = FakeSupabaseGateway()
    resolver = IdentityResolver(UserService(db))

    first = await resolver.resolve_telegram_user(TelegramUser())
    second = await resolver.resolve_telegram_user(TelegramUser())

    assert first["id"] == second["id"]
    assert len(db.tables["users"]) == 1


@pytest.mark.asyncio
async def test_xp_award_updates_user_total_and_level():
    db = FakeSupabaseGateway()
    user = await db.insert("users", {"display_name": "Grace"})
    service = XPService(db)

    await service.award_xp(user["id"], 250, "lusy", "quiz")
    level = await service.get_level(user["id"])

    assert level == {"user_id": user["id"], "total_xp": 250, "level": 3}


@pytest.mark.asyncio
async def test_mongo_telemetry_failure_does_not_raise():
    telemetry = TelemetryMongoGateway("mongodb://invalid-host:27017", server_selection_timeout_ms=1)

    await telemetry.log_event("test.event", bot_name="theo", payload={"ok": True})


def test_level_calculation_floor():
    assert calculate_level(0) == 1
    assert calculate_level(99) == 1
    assert calculate_level(100) == 2


def test_eddy_token_falls_back_to_ed_env(monkeypatch):
    monkeypatch.setenv("ED_BOT_TOKEN", "token-from-ed")
    monkeypatch.delenv("EDDY_BOT_TOKEN", raising=False)

    config = load_config()

    assert config.bots["eddy"].token == "token-from-ed"


@pytest.mark.asyncio
async def test_chat_service_tracks_theo_group_state_in_supabase():
    db = FakeSupabaseGateway()
    service = ChatService(db)

    chat = await service.upsert_chat(
        -100123456789,
        "supergroup",
        title="YOUTHOPIA BIBLE COMMUNITY",
        is_official=True,
    )
    membership = await service.mark_bot_active("theo", chat["id"])

    assert chat["telegram_chat_id"] == -100123456789
    assert chat["is_official"] is True
    assert membership["bot_name"] == "theo"
    assert membership["status"] == "active"
    assert membership["enabled"] is True


@pytest.mark.asyncio
async def test_chat_service_stores_theo_translation_setting():
    db = FakeSupabaseGateway()
    service = ChatService(db)
    chat = await service.upsert_chat(-100123456789, "supergroup")

    settings = await service.set_bot_settings("theo", chat["id"], {"translation": "asv"})

    assert settings["settings"]["translation"] == "asv"


@pytest.mark.asyncio
async def test_chat_service_tracks_daily_devotional_subscription():
    db = FakeSupabaseGateway()
    service = ChatService(db)
    chat = await service.upsert_chat(-100123456789, "supergroup")

    subscription = await service.set_subscription(
        "theo",
        chat["id"],
        "daily_devotional",
        schedule="07:00",
        timezone="Africa/Lagos",
    )

    assert subscription["subscription_type"] == "daily_devotional"
    assert subscription["enabled"] is True
    assert subscription["schedule"] == "07:00"
    assert subscription["timezone"] == "Africa/Lagos"


@pytest.mark.asyncio
async def test_chat_service_reads_enabled_bot_chats():
    db = FakeSupabaseGateway()
    service = ChatService(db)
    chat = await service.upsert_chat(-100123456789, "supergroup")
    await service.mark_bot_active("theo", chat["id"])
    await service.mark_bot_status("lusy", chat["id"], "disabled", enabled=False)

    enabled_theo_chats = await service.get_enabled_bot_chats("theo")

    assert len(enabled_theo_chats) == 1
    assert enabled_theo_chats[0]["chat_id"] == chat["id"]


@pytest.mark.asyncio
async def test_group_message_registers_chat_and_default_bot_settings():
    db = FakeSupabaseGateway()
    services = build_services(db, TelemetryMongoGateway(""))

    chat = await register_group_chat(TelegramMessage(), services, "theo")
    membership = await db.find_one_multi(
        "bot_chat_memberships",
        {"chat_id": chat["id"], "bot_name": "theo"},
    )
    settings = await db.find_one_multi(
        "chat_bot_settings",
        {"chat_id": chat["id"], "bot_name": "theo"},
    )

    assert chat["telegram_chat_id"] == -100123456789
    assert membership["status"] == "active"
    assert membership["enabled"] is True
    assert settings["settings"] == {"translation": "kjv"}


@pytest.mark.asyncio
async def test_user_service_tracks_private_theo_subscription():
    db = FakeSupabaseGateway()
    service = UserService(db)
    user = await service.create_user(display_name="Grace")

    subscription = await service.set_subscription(
        user["id"],
        "theo",
        "daily_devotional",
        enabled=True,
        timezone="Africa/Lagos",
    )

    assert subscription["user_id"] == user["id"]
    assert subscription["bot_name"] == "theo"
    assert subscription["subscription_type"] == "daily_devotional"
    assert subscription["enabled"] is True
    assert subscription["timezone"] == "Africa/Lagos"
