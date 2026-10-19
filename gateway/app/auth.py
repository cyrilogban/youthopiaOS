"""Auth dependency — the one gate every protected endpoint depends on.

Composes the checks into a single FastAPI dependency:
  1. pull raw initData out of the `Authorization: tma <initData>` header,
  2. TelegramUser.from_raw_init_data -> a valid user?
  3. verify_init_data  -> authentic? (HMAC against all trusted bot tokens)
  4. is_fresh          -> recent?    (auth_date within the window; anti-replay)

Verification is hard-enforced: a missing user, a forged signature, or stale
initData all raise 401. The single exception is the dev mock, which is honored
ONLY outside production so local preview works without a real Telegram launch.
"""
from __future__ import annotations

import logging
from fastapi import Header, HTTPException, status

from gateway.app.config import BOT_TOKENS, IS_PRODUCTION
from gateway.app.models import TelegramUser
from gateway.app.validator import is_fresh, verify_init_data

_SCHEME = "tma "
_UNAUTHORIZED = {"WWW-Authenticate": "tma"}

# Telegram re-issues initData on every launch, so an hour-scale window is plenty
# and shrinks the replay surface. Anything older is treated as stale.
_MAX_INIT_DATA_AGE_SECONDS = 86400

# Marker the client stamps on its fake dev initData (services/telegram.ts).
_DEV_MOCK_MARKER = "dev-mock-hash"


def require_telegram_user(authorization: str | None = Header(default=None)) -> TelegramUser:
    """Return the verified Telegram user behind `initData`, or raise 401."""
    if not authorization or not authorization.startswith(_SCHEME):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing Telegram initData", headers=_UNAUTHORIZED)
    raw_init_data = authorization[len(_SCHEME):]

    user = TelegramUser.from_raw_init_data(raw_init_data)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData has no valid user", headers=_UNAUTHORIZED)

    # Dev mock bypass — local preview only, never in production.
    if not IS_PRODUCTION and _DEV_MOCK_MARKER in raw_init_data:
        return user

    # Authentic? Try each trusted bot token (five doors -> five possible signers).
    clean_tokens = {k: v.strip() for k, v in BOT_TOKENS.items() if v and v.strip()}
    signer = verify_init_data(raw_init_data, clean_tokens)
    if signer is None:
        logging.warning("Rejected initData: invalid signature for Telegram user %s (%s)", user.id, user.first_name)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData signature is invalid", headers=_UNAUTHORIZED)

    # Recent? (anti-replay)
    if not is_fresh(raw_init_data, max_age_seconds=_MAX_INIT_DATA_AGE_SECONDS):
        logging.warning("Rejected initData: stale auth_date for Telegram user %s (%s)", user.id, user.first_name)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData is stale", headers=_UNAUTHORIZED)

    return user

