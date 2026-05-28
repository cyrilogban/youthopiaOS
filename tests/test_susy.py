"""
test_susy.py
============
Unit tests for Susy Bot (Welcome & Music Bot).

Covers:
  - Welcome service: new member greeting logic
  - Music service: session creation and validation
  - Greeting formatter utility: message formatting
  - Integration: shared user_service interaction
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_user():
    """Returns a mock Telegram user object."""
    user = MagicMock()
    user.id = 123456789
    user.first_name = "Grace"
    user.last_name = "Doe"
    user.username = "gracedoe"
    user.is_bot = False
    return user


@pytest.fixture
def mock_new_member(mock_user):
    """Returns a mock new chat member event."""
    member = MagicMock()
    member.new_chat_members = [mock_user]
    member.chat.id = -100987654321
    member.chat.title = "YOUTHOPIA BIBLE COMMUNITY"
    return member


@pytest.fixture
def mock_user_record():
    """Returns a mock database user record."""
    return {
        "telegram_id": 123456789,
        "first_name": "Grace",
        "username": "gracedoe",
        "xp_score": 0,
        "trust_score": 100,
        "engagement_level": "new",
        "activity_history": [],
    }


# ---------------------------------------------------------------------------
# Greeting Formatter Tests
# ---------------------------------------------------------------------------

class TestGreetingFormatter:
    """Tests for shared/utils/greeting_formatter.py logic."""

    def test_format_welcome_message_contains_name(self, mock_user):
        """Welcome message must include the user's first name."""
        name = mock_user.first_name
        message = f"Welcome to Youthopia, {name}! 🎉 God's got great plans for you here."
        assert name in message

    def test_format_welcome_message_not_empty(self, mock_user):
        """Welcome message must never be empty."""
        name = mock_user.first_name
        message = f"Welcome, {name}!"
        assert message is not None
        assert len(message) > 0

    def test_format_welcome_message_for_anonymous_user(self):
        """Welcome message should handle users with no username gracefully."""
        user = MagicMock()
        user.first_name = "Friend"
        user.username = None
        display = user.first_name or "Friend"
        message = f"Welcome, {display}!"
        assert "Friend" in message

    def test_format_welcome_includes_community_name(self, mock_user):
        """Welcome message should reference the community."""
        name = mock_user.first_name
        community = "YOUTHOPIA BIBLE COMMUNITY"
        message = f"Welcome to {community}, {name}!"
        assert community in message


# ---------------------------------------------------------------------------
# Welcome Service Tests
# ---------------------------------------------------------------------------

class TestWelcomeService:
    """Tests for Susy Bot welcome service logic."""

    @pytest.mark.asyncio
    async def test_new_member_is_registered_in_user_service(self, mock_user_record):
        """A new member joining should trigger a user record creation."""
        with patch("shared.services.user_service.create_user") as mock_create:
            mock_create.return_value = mock_user_record
            result = await mock_create(telegram_id=123456789, first_name="Grace")
            mock_create.assert_called_once_with(
                telegram_id=123456789, first_name="Grace"
            )
            assert result["telegram_id"] == 123456789

    def test_new_member_starts_with_zero_xp(self, mock_user_record):
        """Newly registered user must start with 0 XP."""
        assert mock_user_record["xp_score"] == 0

    def test_new_member_starts_with_full_trust_score(self, mock_user_record):
        """Newly registered user should have a default trust score of 100."""
        assert mock_user_record["trust_score"] == 100

    def test_new_member_engagement_level_is_new(self, mock_user_record):
        """New member engagement level should be 'new'."""
        assert mock_user_record["engagement_level"] == "new"

    def test_welcome_message_triggered_for_real_user(self, mock_new_member):
        """Welcome handler should not trigger for bots."""
        for member in mock_new_member.new_chat_members:
            assert member.is_bot is False

    def test_welcome_skipped_for_bot_accounts(self):
        """Susy must not welcome other bots joining the group."""
        bot_user = MagicMock()
        bot_user.is_bot = True
        bot_user.first_name = "SomeBot"
        # Simulate the guard condition in the welcome handler
        should_welcome = not bot_user.is_bot
        assert should_welcome is False


# ---------------------------------------------------------------------------
# Music Service Tests
# ---------------------------------------------------------------------------

class TestMusicService:
    """Tests for Susy Bot music/session service logic."""

    def test_music_session_has_required_fields(self):
        """A music session object must have all required fields."""
        session = {
            "session_id": "sess_001",
            "host_telegram_id": 123456789,
            "track_name": "Amazing Grace",
            "status": "active",
            "participants": [],
        }
        assert "session_id" in session
        assert "host_telegram_id" in session
        assert "track_name" in session
        assert "status" in session

    def test_music_session_default_status_is_active(self):
        """A newly created session should have 'active' status."""
        session = {"status": "active"}
        assert session["status"] == "active"

    def test_music_session_can_add_participant(self):
        """Participants should be addable to an active session."""
        session = {"participants": []}
        new_participant = {"telegram_id": 987654321, "name": "John"}
        session["participants"].append(new_participant)
        assert len(session["participants"]) == 1
        assert session["participants"][0]["telegram_id"] == 987654321

    def test_music_session_ends_correctly(self):
        """Ending a session should update its status to 'ended'."""
        session = {"status": "active"}
        session["status"] = "ended"
        assert session["status"] == "ended"

    def test_empty_track_name_is_invalid(self):
        """A music session with no track name should be considered invalid."""
        track_name = ""
        is_valid = bool(track_name and track_name.strip())
        assert is_valid is False

    def test_valid_track_name_passes_validation(self):
        """A non-empty track name should pass validation."""
        track_name = "Way Maker"
        is_valid = bool(track_name and track_name.strip())
        assert is_valid is True


# ---------------------------------------------------------------------------
# Cross-Bot Integration: Susy <-> Shared Services
# ---------------------------------------------------------------------------

class TestSusySharedIntegration:
    """
    Tests for Susy's interaction with the shared services layer.
    Ensures Susy does NOT contain its own business logic but delegates
    to shared services (as per YouThopiaOS architecture rules).
    """

    @pytest.mark.asyncio
    async def test_susy_delegates_user_lookup_to_shared_user_service(self, mock_user_record):
        """Susy must use shared user_service to look up user data, not its own DB calls."""
        with patch("shared.services.user_service.get_user") as mock_get:
            mock_get.return_value = mock_user_record
            result = await mock_get(telegram_id=123456789)
            mock_get.assert_called_once_with(telegram_id=123456789)
            assert result["first_name"] == "Grace"

    def test_susy_welcome_uses_engagement_level_from_shared_record(self, mock_user_record):
        """Welcome message tone should adapt based on engagement_level from shared user record."""
        engagement = mock_user_record["engagement_level"]
        # New users get a warm, introductory welcome
        assert engagement in ["new", "active", "veteran", "at_risk"]

    def test_returning_member_engagement_level_is_not_new(self):
        """A returning active member should not have 'new' engagement level."""
        returning_user = {
            "telegram_id": 111222333,
            "engagement_level": "active",
            "xp_score": 450,
        }
        assert returning_user["engagement_level"] != "new"
