"""initData validator — the cryptographic core of the trust boundary.

Pure function: given the raw initData string Telegram handed the Mini App and
the bot tokens we trust, decide whether the signature is authentic and, if so,
which bot signed it. No FastAPI, no I/O, no globals — just input -> output, so
it is trivial to unit-test.

Telegram's recipe (core.telegram.org/bots/webapps#validating-data):
  1. Split initData into key=value pairs; set `hash` aside.
  2. data-check-string = remaining pairs, sorted by key, joined by '\n'.
  3. secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token)
  4. computed   = HMAC_SHA256(key=secret_key,   msg=data-check-string)  (hex)
  5. Constant-time compare `computed` against the received `hash`.
Five bots can each launch the one Mini App, so we try each trusted token until
one verifies (the "five-doors" problem).
"""
from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import parse_qsl


def verify_init_data(raw_init_data: str, bot_tokens: dict[str, str]) -> str | None:
    """Return the name of the bot that signed `raw_init_data`, or None if the
    signature verifies against no trusted token.

    A truthy return means authentic and untampered; None means reject.
    """
    # 1. Parse into key/value pairs (URL-decoded). keep_blank_values so we
    #    reconstruct EXACTLY what Telegram signed — a dropped empty field would
    #    change the data-check-string and break an otherwise-valid signature.
    pairs = dict(parse_qsl(raw_init_data, keep_blank_values=True))

    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return None  # no signature present -> cannot be trusted

    pairs.pop("signature", None)  # newer 3rd-party field; not part of the HMAC

    # 2. data-check-string: remaining fields sorted by key, 'key=value', \n-joined.
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))

    # 3-5. Try each trusted token (five doors -> five possible signers).
    for bot_name, token in bot_tokens.items():
        secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
        computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(computed, received_hash):
            return bot_name  # authentic — and we now know which door

    return None  # matched no trusted token -> forged or corrupt


def is_fresh(raw_init_data: str, max_age_seconds: int = 86400, now_ts: float | None = None) -> bool:
    """Return True if initData's auth_date is recent enough to accept.

    The HMAC proves Telegram signed the data; it does NOT prove the data is
    recent. Without this check, an attacker could replay a validly-signed
    initData captured long ago. Reject anything older than max_age_seconds
    (default 24h). We bound only the upper age: a future-dated but authentic
    payload is not a replay threat, and a lower bound would false-reject under
    minor clock skew. `now_ts` is injectable so the check is unit-testable.
    """
    pairs = dict(parse_qsl(raw_init_data, keep_blank_values=True))
    raw_auth_date = pairs.get("auth_date")
    if not raw_auth_date:
        return False  # no timestamp -> cannot establish freshness -> reject
    try:
        auth_date = int(raw_auth_date)
    except ValueError:
        return False
    now = now_ts if now_ts is not None else time.time()
    return (now - auth_date) <= max_age_seconds
