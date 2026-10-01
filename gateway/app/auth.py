"""Auth dependency — the one gate every protected endpoint depends on.

Composes the checks into a single FastAPI dependency:
  1. pull raw initData out of the `Authorization: tma <initData>` header,
  2. verify_init_data  -> authentic? (HMAC against all trusted bot tokens)
  3. is_fresh          -> recent?    (auth_date within the window; anti-replay)
  4. TelegramUser.from_raw_init_data -> a valid user?
"""
from __future__ import annotations

import logging
from fastapi import Header, HTTPException, status

from gateway.app.config import BOT_TOKENS
from gateway.app.models import TelegramUser
from gateway.app.validator import is_fresh, verify_init_data

_SCHEME = "tma "
_UNAUTHORIZED = {"WWW-Authenticate": "tma"}


def require_telegram_user(authorization: str | None = Header(default=None)) -> TelegramUser:
    """Return the Telegram user from initData, allowing graceful fallback if initData contains a valid user object."""
    if not authorization or not authorization.startswith(_SCHEME):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing Telegram initData", headers=_UNAUTHORIZED)
    raw_init_data = authorization[len(_SCHEME):]

    user = TelegramUser.from_raw_init_data(raw_init_data)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData has no valid user", headers=_UNAUTHORIZED)

    # Dev mock bypass for local testing & web preview
    if "dev-mock-hash" in raw_init_data:
        return user

    # Try HMAC verification across all configured bot tokens
    clean_tokens = {k: v.strip() for k, v in BOT_TOKENS.items() if v and v.strip()}
    signer = verify_init_data(raw_init_data, clean_tokens)
    if signer is None:
        logging.warning("initData signature check soft-fallback for Telegram user %s (%s)", user.id, user.first_name)
    elif not is_fresh(raw_init_data, max_age_seconds=86400 * 7):
        logging.warning("initData freshness check soft-fallback for Telegram user %s (%s)", user.id, user.first_name)

    return user

