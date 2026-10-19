import time
import urllib.parse
import hmac
import hashlib
import json
import pytest
from fastapi import HTTPException

from gateway.app.auth import require_telegram_user

# A hermetic token so auth tests never depend on real .env secrets.
TEST_TOKEN = "123456:TEST-BOT-TOKEN"


@pytest.fixture(autouse=True)
def _isolated_auth_env(monkeypatch):
    """Pin one trusted token and force development mode for every test."""
    monkeypatch.setattr("gateway.app.auth.BOT_TOKENS", {"test": TEST_TOKEN})
    monkeypatch.setattr("gateway.app.auth.IS_PRODUCTION", False)


def _create_valid_init_data(bot_token: str, user_dict: dict, auth_date: int | None = None) -> str:
    if auth_date is None:
        auth_date = int(time.time())

    params = {
        "auth_date": str(auth_date),
        "user": json.dumps(user_dict),
    }
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    hash_val = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    params["hash"] = hash_val
    return urllib.parse.urlencode(params)


def test_require_telegram_user_missing_header():
    with pytest.raises(HTTPException) as exc_info:
        require_telegram_user(None)
    assert exc_info.value.status_code == 401
    assert "Missing Telegram initData" in exc_info.value.detail


def test_require_telegram_user_no_valid_user():
    # Syntactically fine initData but no user object -> reject.
    header = "tma auth_date=1700000000&hash=whatever"
    with pytest.raises(HTTPException) as exc_info:
        require_telegram_user(header)
    assert exc_info.value.status_code == 401


def test_require_telegram_user_invalid_signature():
    # Valid-looking user payload but forged hash -> hard reject (no soft fallback).
    raw_data = f"user=%7B%22id%22%3A12345%2C%22first_name%22%3A%22Test%22%7D&auth_date={int(time.time())}&hash=invalidhash"
    with pytest.raises(HTTPException) as exc_info:
        require_telegram_user(f"tma {raw_data}")
    assert exc_info.value.status_code == 401


def test_verify_init_data_signs_with_signature_field():
    """Bot API 8.0+ payloads carry a `signature` field that IS part of the HMAC."""
    from gateway.app.validator import verify_init_data

    params = {
        "auth_date": str(int(time.time())),
        "chat_instance": "1234567890123456789",
        "chat_type": "private",
        "user": json.dumps({"id": 12345, "first_name": "Test"}),
        "signature": "TG_ed25519_signature_value-with_dash_and_underscore",
    }
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", TEST_TOKEN.encode(), hashlib.sha256).digest()
    params["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    raw_data = urllib.parse.urlencode(params)
    assert verify_init_data(raw_data, {"test": TEST_TOKEN}) == "test"


def test_require_telegram_user_stale_init_data():
    stale_date = int(time.time()) - (86400 + 3600)  # 25 hours ago
    raw_data = _create_valid_init_data(TEST_TOKEN, {"id": 12345, "first_name": "Test"}, auth_date=stale_date)
    with pytest.raises(HTTPException) as exc_info:
        require_telegram_user(f"tma {raw_data}")
    assert exc_info.value.status_code == 401


def test_require_telegram_user_valid_signed_and_fresh():
    raw_data = _create_valid_init_data(TEST_TOKEN, {"id": 999, "first_name": "AuthenticUser"})
    user = require_telegram_user(f"tma {raw_data}")
    assert user.id == 999
    assert user.first_name == "AuthenticUser"


def test_require_telegram_user_dev_mock_bypass_in_development():
    header = "tma user=%7B%22id%22%3A777%2C%22first_name%22%3A%22DevUser%22%7D&hash=dev-mock-hash"
    user = require_telegram_user(header)
    assert user.id == 777
    assert user.first_name == "DevUser"


def test_require_telegram_user_dev_mock_bypass_rejected_in_production(monkeypatch):
    monkeypatch.setattr("gateway.app.auth.IS_PRODUCTION", True)
    header = f"tma user=%7B%22id%22%3A777%2C%22first_name%22%3A%22DevUser%22%7D&auth_date={int(time.time())}&hash=dev-mock-hash"
    with pytest.raises(HTTPException) as exc_info:
        require_telegram_user(header)
    assert exc_info.value.status_code == 401
