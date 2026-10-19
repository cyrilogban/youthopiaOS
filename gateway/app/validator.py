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


def _data_check_string(pairs: dict[str, str]) -> str:
    """Chain of `key=value` pairs sorted by key, '\n'-joined (Telegram's recipe)."""
    return "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))


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

    # 2. data-check-string: remaining fields sorted by key, 'key=value', \n-joined.
    #    Telegram's HMAC covers ALL fields except `hash` — and, since Bot API 8.0,
    #    the `signature` field IS one of them. (Only the separate Ed25519
    #    third-party check excludes `signature`.) Older clients sent no
    #    `signature` at all, so we also accept the legacy variant that drops it.
    variants = [_data_check_string(pairs)]
    if "signature" in pairs:
        legacy_pairs = dict(pairs)
        legacy_pairs.pop("signature")
        variants.append(_data_check_string(legacy_pairs))

    # 3-5. Try each trusted token (five doors -> five possible signers).
    for bot_name, token in bot_tokens.items():
        secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
        for data_check_string in variants:
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


def debug_conventions(raw_init_data: str, bot_tokens: dict[str, str]) -> str:
    """TEMPORARY DIAGNOSTIC (remove once prod verification is fixed).

    Reports whether the received hash matches each token under the decoded vs
    raw data-check-string convention, each with `signature` included or dropped.
    Lets us see, from a live failure, exactly which convention is in play.
    """
    orig_keys = [k for k, _ in parse_qsl(raw_init_data, keep_blank_values=True)]

    decoded = dict(parse_qsl(raw_init_data, keep_blank_values=True))
    received_hash = decoded.get("hash", "")
    decoded.pop("hash", None)
    decoded_with_sig = dict(decoded)
    decoded.pop("signature", None)

    raw_pairs: dict[str, str] = {}
    for chunk in raw_init_data.split("&"):
        if "=" in chunk:
            key, value = chunk.split("=", 1)
            raw_pairs[key] = value
    raw_pairs.pop("hash", None)
    raw_with_sig = dict(raw_pairs)
    raw_pairs.pop("signature", None)

    candidates = {
        "dec+sig": _data_check_string(decoded_with_sig),
        "dec": _data_check_string(decoded),
        "raw+sig": _data_check_string(raw_with_sig),
        "raw": _data_check_string(raw_pairs),
    }

    marks = []
    for name, token in bot_tokens.items():
        secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
        hits = []
        for label, dcs in candidates.items():
            computed = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
            if computed == received_hash:
                hits.append(label)
        marks.append(f"{name}={'|'.join(hits) if hits else 'N'}")
    return f"keys={sorted(orig_keys)} recv={received_hash[:10]} toks={len(bot_tokens)} " + " ".join(marks)
