from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.identity import IdentityResolver
from core.permissions import PermissionService
from shared.db.mongo import TelemetryMongoGateway
from shared.db.supabase import SupabaseGateway
from shared.services.admin_service import AdminService
from shared.services.analytics_service import AnalyticsService
from shared.services.chat_service import ChatService
from shared.services.event_service import EventService
from shared.services.moderation_service import ModerationService
from shared.services.quiz_service import QuizService
from shared.services.rank_service import RankService
from shared.services.user_service import UserService
from shared.services.xp_service import XPService


@dataclass(slots=True)
class ServiceContainer:
    supabase: SupabaseGateway
    telemetry: TelemetryMongoGateway
    users: UserService
    identity: IdentityResolver
    permissions: PermissionService
    chats: ChatService
    xp: XPService
    events: EventService
    moderation: ModerationService
    analytics: AnalyticsService
    quizzes: QuizService
    admin: AdminService
    ranks: RankService = RankService()
    app_config: Any = None


def build_services(supabase: SupabaseGateway, telemetry: TelemetryMongoGateway) -> ServiceContainer:
    users = UserService(supabase)
    return ServiceContainer(
        supabase=supabase,
        telemetry=telemetry,
        users=users,
        identity=IdentityResolver(users),
        permissions=PermissionService(supabase),
        chats=ChatService(supabase),
        xp=XPService(supabase),
        events=EventService(supabase),
        moderation=ModerationService(supabase),
        analytics=AnalyticsService(supabase, telemetry),
        quizzes=QuizService(supabase),
        admin=AdminService(supabase),
        ranks=RankService(),
    )
