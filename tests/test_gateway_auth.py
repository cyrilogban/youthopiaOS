import time
import urllib.parse
import hmac
import hashlib
import pytest
from fastapi import HTTPException

from gateway.app.auth import require_telegram_user
from gateway.app.config import BOT_TOKENS


def _create_valid_init_data(bot_token: str, user_dict: dict, auth_date: int | None = None) -> str:
    if auth_date is None:
        auth_date = int(time.time())
    
    import json
    user_str = json.dumps(user_dict)
    params = {
        "auth_date": str(auth_date),
        "user": user_str,
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


def test_require_telegram_user_invalid_signature():
    # Valid user payload but forged hash
    raw_data = "user=%7B%22id%22%3A12345%2C%22first_name%22%3A%22Test%22%7D&auth_date=1700000000&hash=invalidhash"
    header = f"tma {raw_data}"
    with pytest.raises(HTTPException) as exc_info:
        require_telegram_user(header)
    assert exc_info.value.status_code == 401
    assert "Invalid Telegram initData signature" in exc_info.value.detail


def test_require_telegram_user_stale_init_data():
    bot_token = list(BOT_TOKENS.values())[0] if BOT_TOKENS else "test_bot_token"
    stale_date = int(time.time()) - (86400 + 3600)  # 25 hours ago
    raw_data = _create_valid_init_data(bot_token, {"id": 12345, "first_name": "Test"}, auth_date=stale_date)
    header = f"tma {raw_data}"
    with pytest.raises(HTTPException) as exc_info:
        require_telegram_user(header)
    assert exc_info.value.status_code == 401
    assert "Stale Telegram initData" in exc_info.value.detail


def test_require_telegram_user_valid_signed_and_fresh():
    bot_token = list(BOT_TOKENS.values())[0] if BOT_TOKENS else "test_bot_token"
    raw_data = _create_valid_init_data(bot_token, {"id": 999, "first_name": "AuthenticUser"})
    header = f"tma {raw_data}"
    user = require_telegram_user(header)
    assert user.id == 999
    assert user.first_name == "AuthenticUser"


def test_require_telegram_user_dev_mock_bypass():
    header = "tma user=%7B%22id%22%3A777%2C%22first_name%22%3A%22DevUser%22%7D&hash=dev-mock-hash"
    user = require_telegram_user(header)
    assert user.id == 777
    assert user.first_name == "DevUser"
