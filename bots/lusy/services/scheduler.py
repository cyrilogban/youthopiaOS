from __future__ import annotations

import logging
import random
import asyncio
from typing import Any
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shared.services.container import ServiceContainer
from bots.lusy.handlers.quizzes import ACTIVE_GROUP_QUIZZES, ACTIVE_POLLS, ACTIVE_RACES, self_destruct_message

logger = logging.getLogger(__name__)

GAME_MODES = ["multiple_choice", "fill_in_the_blank", "verse_completion", "trivia_race"]
DIFFICULTIES = ["easy", "medium", "hard"]


async def start_auto_game_scheduler(bot: Bot, services: ServiceContainer) -> None:
    """
    Background loop that triggers Auto Game drops 10-15 times per day (approx. every 60-90 minutes).
    """
    logger.info("🎮 Starting Lusy Auto Game Scheduler...")
    await asyncio.sleep(60)

    while True:
        try:
            await trigger_auto_game_cycle(bot, services)
        except Exception as e:
            logger.error(f"Error in trigger_auto_game_cycle: {e}")

        # Sleep between 60 to 90 minutes for 10-15 drops daily
        next_interval = random.randint(3600, 5400)
        await asyncio.sleep(next_interval)


async def trigger_auto_game_cycle(bot: Bot, services: ServiceContainer) -> None:
    """
    Finds active groups where auto_game is enabled and drops a casual question.
    """
    try:
        active_subs = await services.chats.get_active_subscriptions("lusy", "auto_game")
    except Exception as e:
        logger.error(f"Failed to fetch auto_game subscriptions: {e}")
        return

    if not active_subs:
        return

    for sub in active_subs:
        try:
            telegram_chat_id_str = sub.get("chat_id")
            if not telegram_chat_id_str:
                continue

            chat_id = int(telegram_chat_id_str)

            # Skip if a manual quiz is ALREADY running in this group
            if chat_id in ACTIVE_GROUP_QUIZZES:
                logger.info(f"Skipping Auto Game for group {chat_id}: quiz in progress.")
                continue

            # Pick a random game mode and difficulty from Lusy's existing catalog
            game_type = random.choice(GAME_MODES)
            difficulty = random.choice(DIFFICULTIES)

            # Fetch question matching mode & difficulty from Supabase
            questions = await services.quizzes.get_questions_by_difficulty(difficulty, game_type=game_type)
            if not questions:
                questions = await services.quizzes.get_questions_by_difficulty(difficulty, game_type="multiple_choice")
                game_type = "multiple_choice"

            if not questions:
                continue

            question_record = random.choice(questions)
            q_id = question_record["id"]
            content = question_record.get("content", {})
            text = content.get("text", "Bible Question")
            options = content.get("options", [])
            correct_text = question_record.get("correct_answer")
            explanation = question_record.get("explanation", "")

            correct_idx = options.index(correct_text) if correct_text in options else 0

            # Mode 1: Trivia Race
            if game_type == "trivia_race":
                choices_buttons = []
                row = []
                for idx, opt in enumerate(options):
                    row.append(InlineKeyboardButton(text=opt, callback_data=f"lusy_race_choice_{idx}"))
                    if len(row) == 2:
                        choices_buttons.append(row)
                        row = []
                if row:
                    choices_buttons.append(row)
                choices_buttons.append([InlineKeyboardButton(text="🛑 Quit Game", callback_data=f"lusy_quit_game_{chat_id}")])

                race_text = (
                    "🎮 <b>CASUAL AUTO GAME!</b>\n"
                    f"⚡ <b>BIBLE TRIVIA RACE!</b> <i>({difficulty.upper()})</i>\n"
                    "<i>(First correct answer wins YP! Card self-destructs in 5 mins)</i>\n\n"
                    f"<b>Question:</b>\n"
                    f"<blockquote>{text}</blockquote>"
                )

                sent_msg = await bot.send_message(
                    chat_id=chat_id,
                    text=race_text,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=choices_buttons)
                )

                ACTIVE_GROUP_QUIZZES[chat_id] = f"race_{sent_msg.message_id}"
                import time
                race_key = f"{chat_id}_{sent_msg.message_id}"
                ACTIVE_RACES[race_key] = {
                    "question_id": q_id,
                    "correct_idx": correct_idx,
                    "base_xp": 20,
                    "is_group": True,
                    "chat_id": chat_id,
                    "message_id": sent_msg.message_id,
                    "host_id": None,
                    "locked_out": set(),
                    "start_time": time.time(),
                    "closed": False,
                    "explanation": explanation,
                    "text": text,
                    "difficulty": difficulty
                }

                asyncio.create_task(self_destruct_message(bot, chat_id, sent_msg.message_id, 300))

            # Mode 2: Native Quiz Polls
            else:
                if game_type == "fill_in_the_blank":
                    prefix = "📖 [AUTO GAME: FILL IN THE BLANK]"
                elif game_type == "verse_completion":
                    prefix = "🔠 [AUTO GAME: VERSE SCRAMBLE]"
                else:
                    prefix = f"🎮 [AUTO GAME: {difficulty.upper()}]"

                sent_poll = await bot.send_poll(
                    chat_id=chat_id,
                    question=f"{prefix} {text}",
                    options=options,
                    type="quiz",
                    correct_option_id=correct_idx,
                    explanation=explanation if explanation else None,
                    is_anonymous=False,
                    open_period=60
                )

                ACTIVE_GROUP_QUIZZES[chat_id] = sent_poll.poll.id
                ACTIVE_POLLS[sent_poll.poll.id] = {
                    "question_id": q_id,
                    "game_type": game_type,
                    "base_xp": 15,
                    "is_group": True,
                    "chat_id": chat_id,
                    "message_id": sent_poll.message_id,
                    "host_id": None,
                    "user_id": None,
                    "duration": 60,
                    "votes": {},
                    "max_votes": 5,
                    "closed": False
                }

                asyncio.create_task(self_destruct_message(bot, chat_id, sent_poll.message_id, 300))

        except Exception as e:
            logger.error(f"Error dropping Auto Game for chat {sub.get('chat_id')}: {e}")
