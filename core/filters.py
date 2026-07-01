import logging
from aiogram.types import Message
from aiogram.filters import Filter

logger = logging.getLogger(__name__)

class IsAdminFilter(Filter):
    """Filter to restrict commands to group administrators or creators."""
    async def __call__(self, message: Message) -> bool:
        # Admin commands only make sense in group chats
        if message.chat.type == "private":
            return False 
            
        try:
            member = await message.chat.get_member(message.from_user.id)
            return member.status in ("administrator", "creator")
        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False
