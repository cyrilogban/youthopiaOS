"""Auth dependency — the one gate every protected endpoint depends on.

Composes the three pure checks into a single FastAPI dependency:
  1. pull raw initData out of the `Authorization: tma <initData>` header,
  2. verify_init_data  -> authentic? (HMAC against all trusted bot tokens)
  3. is_fresh          -> recent?    (auth_date within the window; anti-replay)
  4. TelegramUser.from_raw_init_data -> a valid user?
Any failure raises 401 and the endpoint never runs. Order matters: we prove the
signature BEFORE trusting any field inside initData (including auth_date).
"""
from __future__ import annotations

from fastapi import Header, HTTPException, status

from gateway.app.config import BOT_TOKENS
from gateway.app.models import TelegramUser
from gateway.app.validator import is_fresh, verify_init_data

_SCHEME = "tma "  # Telegram Mini Apps auth scheme: "Authorization: tma <initData>"
_UNAUTHORIZED = {"WWW-Authenticate": "tma"}  # RFC 7235: a 401 should name the scheme


def require_telegram_user(authorization: str | None = Header(default=None)) -> TelegramUser:
    """Return the verified Telegram user, or raise 401 if initData fails any gate."""
    if not authorization or not authorization.startswith(_SCHEME):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing Telegram initData", headers=_UNAUTHORIZED)
    raw_init_data = authorization[len(_SCHEME):]

    if verify_init_data(raw_init_data, BOT_TOKENS) is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData signature is invalid", headers=_UNAUTHORIZED)

    if not is_fresh(raw_init_data):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData has expired", headers=_UNAUTHORIZED)

    user = TelegramUser.from_raw_init_data(raw_init_data)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData has no valid user", headers=_UNAUTHORIZED)

    return user
