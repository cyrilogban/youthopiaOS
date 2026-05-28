from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


@dataclass(slots=True)
class PermissionService:
    db: SupabaseGateway

    async def user_has_permission(
        self,
        user_id: str,
        permission_code: str,
        *,
        chat_id: str | None = None,
    ) -> bool:
        permission = await self.db.find_one("permissions", "code", permission_code)
        if not permission:
            return False

        membership_filters: dict[str, Any] = {"user_id": user_id}
        if chat_id:
            membership_filters["chat_id"] = chat_id
        membership = await self.db.find_one_multi("chat_memberships", membership_filters)
        if not membership or not membership.get("role_id"):
            return False

        role_permission = await self.db.find_one_multi(
            "role_permissions",
            {"role_id": membership["role_id"], "permission_id": permission["id"]},
        )
        return bool(role_permission)
