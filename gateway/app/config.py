"""Gateway configuration — the set of bot tokens the gateway trusts.

All five bots are doors into the one Mini App, so a given piece of initData
could have been signed by ANY of their tokens. The validator (next step) tries
each trusted token until one verifies. This module's only job is to hand the
validator that set.

Secrets come from the existing shared settings (loaded once from the repo-root
.env). We do NOT re-read the environment here — single source of truth.
"""
from shared.config.settings import settings

# bot name -> token, for every bot that actually has a token configured.
# Blank tokens (bot not set up yet) are excluded so the gateway never tries to
# validate initData against an empty secret.
BOT_TOKENS: dict[str, str] = {
    name: token
    for name, token in {
        "theo": settings.THEO_BOT_TOKEN,
        "lusy": settings.LUSY_BOT_TOKEN,
        "pete": settings.PETE_BOT_TOKEN,
        "eddy": settings.EDDY_BOT_TOKEN,
        "susy": settings.SUSY_BOT_TOKEN,
    }.items()
    if token
}
