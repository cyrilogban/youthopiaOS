from __future__ import annotations

from shared.config.settings import settings
from shared.db.supabase import SupabaseGateway


def get_supabase_gateway() -> SupabaseGateway:
    return SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_supabase_client():
    return get_supabase_gateway().connect().client
