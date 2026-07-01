from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, PollAnswer
from aiogram import Bot
from shared.services.container import ServiceContainer
import random
import asyncio
import datetime
import logging

logger = logging.getLogger(__name__)

quiz_router = Router()

# In-memory tracking for active quiz polls
# poll_id (str) -> {question_id, base_xp, is_group, chat_id, message_id, votes, max_votes, closed}
ACTIVE_POLLS = {}

# In-memory tracking for active group quizzes: chat_id (int) -> poll_id (str)
ACTIVE_GROUP_QUIZZES = {}

# Standard timing durations by difficulty (in seconds)
DIFFICULTY_TIMERS = {
    "easy": 60,
    "medium": 30,
    "hard": 20
}

# In-memory tracking for recently posted group questions: chat_id (int) -> list of question_id (str)
RECENT_GROUP_QUESTIONS = {}

# In-memory tracking for active speed races: f"{chat_id}_{message_id}" -> state_dict
ACTIVE_RACES = {}


@quiz_router.callback_query(F.data == "lusy_soon")
async def on_soon(callback: CallbackQuery):
    await callback.answer("This game mode is coming soon!", show_alert=True)


@quiz_router.callback_query(F.data == "lusy_play_quiz")
async def choose_difficulty(callback: CallbackQuery):
    try:
        chat_id = callback.message.chat.id
        if callback.message.chat.type != "private":
            if chat_id in ACTIVE_GROUP_QUIZZES:
                await callback.answer("⚠️ An active quiz is already running in this group! Complete it first.", show_alert=True)
                return

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_mc_easy"),
                InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_mc_medium")
            ],
            [
                InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_mc_hard")
            ]
        ])
        await callback.message.edit_text("<b>Choose your Bible Challenge Difficulty!</b>\nHarder questions reward more YP.", parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in choose_difficulty callback: {e}")
    finally:
        try:
            await callback.answer()
        except Exception:
            pass


@quiz_router.callback_query(F.data == "lusy_play_fill_blank")
async def choose_fill_blank_difficulty(callback: CallbackQuery):
    try:
        chat_id = callback.message.chat.id
        if callback.message.chat.type != "private":
            if chat_id in ACTIVE_GROUP_QUIZZES:
                await callback.answer("⚠️ An active quiz is already running in this group! Complete it first.", show_alert=True)
                return

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_fb_easy"),
                InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_fb_medium")
            ],
            [
                InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_fb_hard")
            ]
        ])
        await callback.message.edit_text("<b>Choose Verse Completion Difficulty!</b>\nHarder questions reward more YP.", parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in choose_fill_blank_difficulty callback: {e}")
    finally:
        try:
            await callback.answer()
        except Exception:
            pass


@quiz_router.callback_query(F.data.startswith("lusy_quiz_diff_"))
async def start_quiz(callback: CallbackQuery, services: ServiceContainer):
    answered = False
    try:
        parts = callback.data.split("_")
        difficulty = parts[-1] # easy, medium, or hard
        game_mode_code = parts[3] if len(parts) >= 5 else "mc"
        if game_mode_code == "fb":
            game_type = "fill_in_the_blank"
        elif game_mode_code == "vs":
            game_type = "verse_completion"
        else:
            game_type = "multiple_choice"
        
        duration = DIFFICULTY_TIMERS.get(difficulty.lower(), 20)
        chat_id = callback.message.chat.id
        is_group = callback.message.chat.type != "private"
        
        if is_group and chat_id in ACTIVE_GROUP_QUIZZES:
            await callback.answer("⚠️ An active quiz is already running in this group!", show_alert=True)
            answered = True
            return

        user = await services.identity.resolve_telegram_user(callback.from_user)
        user_id = user["id"]
        
        # 1. Fetch questions matching this difficulty and game type
        questions_resp = await services.quizzes.get_questions_by_difficulty(difficulty, game_type=game_type)
        
        if not questions_resp:
            if game_type == "fill_in_the_blank":
                label = "Verse Completion"
            elif game_type == "verse_completion":
                label = "Verse Scramble"
            else:
                label = "Bible Challenge"
            await callback.message.edit_text(f"No {difficulty} {label} questions found in the database yet! Please try another difficulty.")
            await callback.answer()
            answered = True
            return

        # 1b. Filter out already answered questions
        if not is_group:
            # Check private game history
            history = await services.quizzes.get_game_history(user_id)
            answered_ids = { h["question_id"] for h in history }
        else:
            # Check group's recently posted questions
            answered_ids = set(RECENT_GROUP_QUESTIONS.get(chat_id, []))

        eligible_questions = [q for q in questions_resp if q["id"] not in answered_ids]

        if not eligible_questions:
            if not is_group:
                # Tell the DM user they finished the difficulty!
                fb_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_fb_easy"),
                        InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_fb_medium")
                    ],
                    [
                        InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_fb_hard")
                    ]
                ])
                vs_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_vs_easy"),
                        InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_vs_medium")
                    ],
                    [
                        InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_vs_hard")
                    ]
                ])
                mc_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_mc_easy"),
                        InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_mc_medium")
                    ],
                    [
                        InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_mc_hard")
                    ]
                ])
                if game_type == "fill_in_the_blank":
                    difficulty_markup = fb_markup
                    label = "Verse Completion"
                elif game_type == "verse_completion":
                    difficulty_markup = vs_markup
                    label = "Verse Scramble"
                else:
                    difficulty_markup = mc_markup
                    label = "Bible Challenge"
                await callback.message.edit_text(
                    f"🏆 <b>Difficulty Completed!</b>\n\nWow! You have successfully answered all <b>{difficulty.capitalize()}</b> {label} questions in YouThopia!\n\nTry another difficulty level to continue earning YP.",
                    parse_mode="HTML",
                    reply_markup=difficulty_markup
                )
                await callback.answer()
                answered = True
                return
            else:
                # In group, if all questions were shown recently, reset group history so they can replay them!
                RECENT_GROUP_QUESTIONS[chat_id] = []
                eligible_questions = questions_resp
            
        # 2. Pick a random question from eligible list
        question_record = random.choice(eligible_questions)
        q_id = question_record["id"]
        content = question_record.get("content", {})
        text = content.get("text", "Unknown Question")
        options = content.get("options", [])
        correct_text = question_record.get("correct_answer")
        explanation = question_record.get("explanation", "")
        
        # Find the index of the correct answer
        correct_idx = 0
        if correct_text in options:
            correct_idx = options.index(correct_text)
            
        # Delete the difficulty menu message safely
        try:
            await callback.message.delete()
        except Exception:
            try:
                await callback.message.edit_text("<b>Game started!</b>", parse_mode="HTML")
            except Exception:
                pass
                
        is_race = (game_mode_code == "rc")
        if is_race:
            # Send a Trivia Race!
            # Format the options as inline keyboard buttons
            choices_buttons = []
            row = []
            for idx, opt in enumerate(options):
                row.append(InlineKeyboardButton(text=opt, callback_data=f"lusy_race_choice_{idx}"))
                if len(row) == 2:
                    choices_buttons.append(row)
                    row = []
            if row:
                choices_buttons.append(row)
                
            xp_reward = 15 if difficulty == "easy" else (25 if difficulty == "medium" else 35)
            
            race_text = (
                "⚡ <b>BIBLE TRIVIA RACE!</b>\n"
                f"<i>({difficulty.upper()} difficulty — First correct answer wins <b>{xp_reward} YP</b>!)</i>\n"
                "⚠️ <i>Warning: An incorrect guess eliminates you from this round!</i>\n\n"
                f"<b>Question:</b>\n"
                f"<blockquote>{text}</blockquote>"
            )
            
            sent_msg = await callback.message.answer(
                text=race_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=choices_buttons)
            )
            
            if is_group:
                ACTIVE_GROUP_QUIZZES[chat_id] = f"race_{sent_msg.message_id}"
                
            import time
            race_key = f"{chat_id}_{sent_msg.message_id}"
            ACTIVE_RACES[race_key] = {
                "question_id": q_id,
                "correct_idx": correct_idx,
                "base_xp": xp_reward,
                "is_group": is_group,
                "chat_id": chat_id,
                "message_id": sent_msg.message_id,
                "locked_out": set(),
                "start_time": time.time(),
                "closed": False,
                "explanation": explanation,
                "text": text,
                "difficulty": difficulty
            }
            
            asyncio.create_task(race_timeout_task(chat_id, sent_msg.message_id, services, callback.bot, duration))
            return

        # Send a native Telegram Quiz Poll!
        if game_type == "fill_in_the_blank":
            prefix = "📖 [FILL IN THE BLANK]"
        elif game_type == "verse_completion":
            prefix = "🔠 [VERSE SCRAMBLE]\nUnscramble to find the correct reference:"
        else:
            prefix = f"[{difficulty.upper()}]"
            
        sent_poll = await callback.message.answer_poll(
            question=f"{prefix} {text}",
            options=options,
            type="quiz",
            correct_option_id=correct_idx,
            explanation=explanation if explanation else None,
            is_anonymous=False, # Must be false so we know WHO answered it!
            open_period=duration
        )
        
        if is_group:
            # Send a self-destructing instruction message
            if game_type == "fill_in_the_blank":
                label = "Verse Completion"
            elif game_type == "verse_completion":
                label = "Verse Scramble"
            else:
                label = "Bible Challenge"
            guide_text = (
                f"⚡ <b>{label} Started!</b>\n"
                "• Tap your answer to vote.\n"
                f"• The poll closes after 5 votes or {duration} seconds.\n"
                "• Winners will get their YP added automatically!\n\n"
                f"<i>🧹 This guide will self-destruct in {duration + 5} seconds...</i>"
            )
            try:
                guide_msg = await callback.message.answer(text=guide_text, parse_mode="HTML")
                asyncio.create_task(self_destruct_message(callback.bot, chat_id, guide_msg.message_id, duration + 5))
            except Exception:
                pass
        
        if not is_group:
            # Save the mapping of poll_id -> question_id so we can award XP when they answer (only for DMs)
            await services.quizzes.track_private_poll(
                user_id,
                sent_poll.poll.id,
                q_id,
                question_record.get("base_xp", 10)
            )
        else:
            # Set active group quiz status
            ACTIVE_GROUP_QUIZZES[chat_id] = sent_poll.poll.id
            
            # Add to recently posted questions in this group
            if chat_id not in RECENT_GROUP_QUESTIONS:
                RECENT_GROUP_QUESTIONS[chat_id] = []
            RECENT_GROUP_QUESTIONS[chat_id].append(q_id)
            if len(RECENT_GROUP_QUESTIONS[chat_id]) > 15:
                RECENT_GROUP_QUESTIONS[chat_id].pop(0)
        
        # Track globally in memory
        ACTIVE_POLLS[sent_poll.poll.id] = {
            "question_id": q_id,
            "game_type": game_type,
            "base_xp": question_record.get("base_xp", 10),
            "is_group": is_group,
            "chat_id": chat_id,
            "message_id": sent_poll.message_id,
            "user_id": None if is_group else user_id,
            "duration": duration,
            "votes": {}, # user_id -> { "display_name": str, "is_correct": bool }
            "max_votes": 5, # Close group poll after 5 votes
            "closed": False
        }
        
        # Schedule timeout fallback
        if is_group:
            asyncio.create_task(group_poll_timeout(sent_poll.poll.id, chat_id, sent_poll.message_id, services, callback.bot, duration))
        else:
            asyncio.create_task(dm_poll_timeout(sent_poll.poll.id, chat_id, sent_poll.message_id, services, callback.bot, duration))
            
    except Exception as e:
        logger.error(f"Error in start_quiz callback: {e}")
    finally:
        if not answered:
            try:
                await callback.answer()
            except Exception:
                pass


async def self_destruct_message(bot: Bot, chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


async def group_poll_timeout(poll_id: str, chat_id: int, message_id: int, services: ServiceContainer, bot: Bot, duration: int):
    # Wait for duration + 1s buffer for network latency
    await asyncio.sleep(duration + 1)
    poll_info = ACTIVE_POLLS.get(poll_id)
    if poll_info and not poll_info.get("closed", False):
        await close_and_reward_group_poll(poll_id, services, bot)


async def dm_poll_timeout(poll_id: str, chat_id: int, message_id: int, services: ServiceContainer, bot: Bot, duration: int):
    # Wait for duration + 1s buffer for network latency
    await asyncio.sleep(duration + 1)
    poll_info = ACTIVE_POLLS.get(poll_id)
    if poll_info and not poll_info.get("closed", False):
        poll_info["closed"] = True
        
        # We no longer delete the poll message; we let it expire natively
            
        user_id = poll_info.get("user_id")
        if user_id:
            await services.quizzes.clear_private_poll_tracking(user_id)
            
        game_type = poll_info.get("game_type")
        if game_type == "fill_in_the_blank":
            next_callback = "lusy_play_fill_blank"
            game_label = "Verse Completion"
        elif game_type == "verse_completion":
            next_callback = "lusy_play_scramble"
            game_label = "Verse Scramble"
        else:
            next_callback = "lusy_play_quiz"
            game_label = "Bible Challenge"
            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Next Question ➡️", callback_data=next_callback)]
        ])
        
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"⏰ <b>Time's up!</b> You didn't answer the {game_label} within {duration} seconds. (0 YP earned)\n\nReady to try again?",
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception:
            pass
            
        if poll_id in ACTIVE_POLLS:
            del ACTIVE_POLLS[poll_id]


async def close_and_reward_group_poll(poll_id: str, services: ServiceContainer, bot: Bot):
    poll_info = ACTIVE_POLLS.get(poll_id)
    if not poll_info or poll_info.get("closed", False):
        return
        
    poll_info["closed"] = True
    chat_id = poll_info["chat_id"]
    message_id = poll_info["message_id"]
    question_id = poll_info["question_id"]
    base_xp = poll_info["base_xp"]
    votes = poll_info["votes"]
    
    # 1. Stop the poll on Telegram (locks it natively but keeps it in the chat)
    try:
        await bot.stop_poll(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
        
    # 2. Fetch correct answer details for display
    q_resp = await services.quizzes.get_question_by_id(question_id)
    correct_text = "Unknown"
    if q_resp:
        correct_text = q_resp.get("correct_answer", "Unknown")
        
    # 3. Award XP and compile winners list
    winners = []
    
    for voter_id, vote in votes.items():
        is_correct = vote["is_correct"]
        xp_earned = base_xp if is_correct else 0
        display_name = vote["display_name"]
        
        # Log to game history
        await services.quizzes.save_game_result(
            voter_id,
            question_id,
            is_correct,
            xp_earned
        )
        
        if is_correct:
            # Award YP
            await services.xp.award_xp(voter_id, xp_earned, "lusy", f"Group Bible Quiz: {question_id}")
            winners.append(display_name)
            
    # 4. Format and send summary message in the group
    game_type = poll_info.get("game_type")
    if game_type == "fill_in_the_blank":
        next_callback = "lusy_play_fill_blank"
        title = "Verse Completion"
    elif game_type == "verse_completion":
        next_callback = "lusy_play_scramble"
        title = "Verse Scramble"
    else:
        next_callback = "lusy_play_quiz"
        title = "Quiz"
        
    leaderboard_text = f"<b>🏆 {title} Completed!</b>\n"
    leaderboard_text += f"Correct Answer: <b>{correct_text}</b>\n\n"
    
    if winners:
        leaderboard_text += f"<b>Winners (+{base_xp} YP):</b>\n"
        medals = ["🥇", "🥈", "🥉"]
        for idx, winner in enumerate(winners):
            medal = medals[idx] if idx < len(medals) else "🔹"
            leaderboard_text += f"{medal} {winner}\n"
    else:
        leaderboard_text += "No correct answers this time! 😢\n"
        
    leaderboard_text += f"\n<i>Total participants: {len(votes)}</i>\n\n"
    leaderboard_text += "Ready for the next round? Tap below!"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Next Question ➡️", callback_data=next_callback)]
    ])
    
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=leaderboard_text,
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception:
        pass
    
    # 5. Clear state
    if chat_id in ACTIVE_GROUP_QUIZZES:
        del ACTIVE_GROUP_QUIZZES[chat_id]
    if poll_id in ACTIVE_POLLS:
        del ACTIVE_POLLS[poll_id]


@quiz_router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, services: ServiceContainer, bot: Bot):
    user = await services.identity.resolve_telegram_user(poll_answer.user)
    user_id = user["id"]
    
    poll_id = poll_answer.poll_id
    poll_info = ACTIVE_POLLS.get(poll_id)
    
    if not poll_info or poll_info.get("closed", False):
        return
        
    is_group = poll_info.get("is_group", False)
    question_id = poll_info["question_id"]
    base_xp = poll_info["base_xp"]
    
    # Fetch correct answer index
    q_resp = await services.quizzes.get_question_by_id(question_id)
    if not q_resp:
        return
        
    content = q_resp.get("content", {})
    options = content.get("options", [])
    correct_text = q_resp.get("correct_answer")
    correct_idx = options.index(correct_text) if correct_text in options else 0
    
    is_correct = correct_idx in poll_answer.option_ids
    
    if not is_group:
        # Private poll flow: award instantly and send DM
        poll_info["closed"] = True
        xp_awarded = base_xp if is_correct else 0
        await services.quizzes.save_game_result(
            user_id,
            question_id,
            is_correct,
            xp_awarded
        )
        if is_correct:
            await services.xp.award_xp(user_id, xp_awarded, "lusy", f"Bible Quiz: {question_id}")
            
        await services.quizzes.clear_private_poll_tracking(user_id)
        
        if poll_id in ACTIVE_POLLS:
            del ACTIVE_POLLS[poll_id]
            
        result_text = f"Correct! 🎉 +{xp_awarded} YP!" if is_correct else "Incorrect! ❌"
        
        game_type = poll_info.get("game_type")
        if game_type == "fill_in_the_blank":
            next_callback = "lusy_play_fill_blank"
        elif game_type == "verse_completion":
            next_callback = "lusy_play_scramble"
        else:
            next_callback = "lusy_play_quiz"
            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Next Question ➡️", callback_data=next_callback)]
        ])
        await bot.send_message(
            chat_id=poll_answer.user.id,
            text=f"<b>{result_text}</b>\n\nDo you want to play another one?",
            parse_mode="HTML",
            reply_markup=markup
        )
    else:
        # Group poll flow: Accumulate votes in memory
        display_name = poll_answer.user.first_name or poll_answer.user.username or "Anonymous"
        poll_info["votes"][user_id] = {
            "display_name": display_name,
            "is_correct": is_correct
        }
        
        # Check if vote limit reached (e.g. 5 votes)
        if len(poll_info["votes"]) >= poll_info.get("max_votes", 5):
            await close_and_reward_group_poll(poll_id, services, bot)


async def on_quiz_command(message: Message, services: ServiceContainer):
    chat_id = message.chat.id
    if message.chat.type != "private":
        if chat_id in ACTIVE_GROUP_QUIZZES:
            await message.answer("⚠️ <b>Quiz in Progress!</b>\nAn active quiz is already running in this group. Answer the current quiz first!")
            return

    # Show difficulty selection menu
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_mc_easy"),
            InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_mc_medium")
        ],
        [
            InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_mc_hard")
        ]
    ])
    await message.answer("<b>Choose your Bible Challenge Difficulty!</b>\nHarder questions reward more YP.", parse_mode="HTML", reply_markup=markup)


async def on_fillblank_command(message: Message, services: ServiceContainer):
    chat_id = message.chat.id
    if message.chat.type != "private":
        if chat_id in ACTIVE_GROUP_QUIZZES:
            await message.answer("⚠️ <b>Quiz in Progress!</b>\nAn active quiz is already running in this group. Answer the current quiz first!")
            return

    # Show difficulty selection menu for Verse Completion
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_fb_easy"),
            InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_fb_medium")
        ],
        [
            InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_fb_hard")
        ]
    ])
    await message.answer(
        "📖 <b>Choose Verse Completion Difficulty!</b>\n"
        "Fill in the missing words of scripture. Harder questions reward more YP.",
        parse_mode="HTML",
        reply_markup=markup
    )


@quiz_router.callback_query(F.data == "lusy_play_race")
async def choose_race_difficulty(callback: CallbackQuery):
    try:
        chat_id = callback.message.chat.id
        if callback.message.chat.type != "private":
            if chat_id in ACTIVE_GROUP_QUIZZES:
                await callback.answer("⚠️ An active quiz/race is already running in this group! Complete it first.", show_alert=True)
                return

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Easy (15 YP)", callback_data="lusy_quiz_diff_rc_easy"),
                InlineKeyboardButton(text="Medium (25 YP)", callback_data="lusy_quiz_diff_rc_medium")
            ],
            [
                InlineKeyboardButton(text="Hard (35 YP)", callback_data="lusy_quiz_diff_rc_hard")
            ]
        ])
        await callback.message.edit_text(
            "⚡ <b>Choose Trivia Race Difficulty!</b>\n"
            "Be the FIRST to answer correctly. Wrong answers eliminate you from the round! Harder questions reward more YP.",
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error in choose_race_difficulty callback: {e}")
    finally:
        try:
            await callback.answer()
        except Exception:
            pass


async def on_race_command(message: Message, services: ServiceContainer):
    chat_id = message.chat.id
    if message.chat.type != "private":
        if chat_id in ACTIVE_GROUP_QUIZZES:
            await message.answer("⚠️ <b>Game in Progress!</b>\nAn active quiz/race is already running in this group. Complete it first!")
            return

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Easy (15 YP)", callback_data="lusy_quiz_diff_rc_easy"),
            InlineKeyboardButton(text="Medium (25 YP)", callback_data="lusy_quiz_diff_rc_medium")
        ],
        [
            InlineKeyboardButton(text="Hard (35 YP)", callback_data="lusy_quiz_diff_rc_hard")
        ]
    ])
    await message.answer(
        "⚡ <b>Choose Trivia Race Difficulty!</b>\n"
        "First correct answer wins YP! Wrong answers eliminate you. Harder questions reward more YP.",
        parse_mode="HTML",
        reply_markup=markup
    )


async def race_timeout_task(chat_id: int, message_id: int, services: ServiceContainer, bot: Bot, duration: int):
    # Wait for duration (e.g., 20 seconds) plus 1s buffer
    await asyncio.sleep(duration + 1)
    race_key = f"{chat_id}_{message_id}"
    race_info = ACTIVE_RACES.get(race_key)
    if race_info and not race_info.get("closed", False):
        race_info["closed"] = True
        
        # Resolve correct answer text
        q_resp = await services.quizzes.get_question_by_id(race_info["question_id"])
        correct_text = q_resp.get("correct_answer", "Unknown") if q_resp else "Unknown"
        explanation = race_info.get("explanation", "")
        
        timeout_text = (
            "⚡ <b>BIBLE TRIVIA RACE!</b>\n"
            f"<i>({race_info['difficulty'].upper()} difficulty)</i>\n\n"
            f"<b>Question:</b>\n"
            f"<blockquote>{race_info['text']}</blockquote>\n\n"
            "⏰ <b>Time's Up!</b> Nobody answered correctly in time.\n"
            f"The correct answer was: <b>{correct_text}</b>\n"
        )
        if explanation:
            timeout_text += f"💡 <i>{explanation}</i>\n"
            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Next Race ⚡", callback_data="lusy_play_race")]
        ])
        
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=timeout_text,
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception:
            pass
            
        # Clean up state
        if chat_id in ACTIVE_GROUP_QUIZZES:
            del ACTIVE_GROUP_QUIZZES[chat_id]
        if race_key in ACTIVE_RACES:
            del ACTIVE_RACES[race_key]


@quiz_router.callback_query(F.data.startswith("lusy_race_choice_"))
async def handle_race_choice(callback: CallbackQuery, services: ServiceContainer):
    user = await services.identity.resolve_telegram_user(callback.from_user)
    user_id = user["id"]
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    race_key = f"{chat_id}_{message_id}"
    
    race_info = ACTIVE_RACES.get(race_key)
    if not race_info or race_info.get("closed", False):
        try:
            await callback.answer("This race has already ended!", show_alert=True)
        except Exception:
            pass
        return
        
    if user_id in race_info["locked_out"]:
        try:
            await callback.answer("❌ You are eliminated from this round!", show_alert=True)
        except Exception:
            pass
        return
        
    choice_idx = int(callback.data.split("_")[-1])
    is_correct = (choice_idx == race_info["correct_idx"])
    
    if is_correct:
        # Secure the lock instantly to prevent double wins
        race_info["closed"] = True
        
        import time
        time_taken = round(time.time() - race_info["start_time"], 2)
        base_xp = race_info["base_xp"]
        question_id = race_info["question_id"]
        
        # Award YP
        await services.quizzes.save_game_result(user_id, question_id, True, base_xp)
        await services.xp.award_xp(user_id, base_xp, "lusy", f"Trivia Race Winner: {question_id}")
        
        # Get correct answer text
        q_resp = await services.quizzes.get_question_by_id(question_id)
        correct_text = q_resp.get("correct_answer", "Unknown") if q_resp else "Unknown"
        explanation = race_info.get("explanation", "")
        
        winner_name = callback.from_user.first_name or callback.from_user.username or "Anonymous"
        
        win_text = (
            "⚡ <b>BIBLE TRIVIA RACE!</b>\n"
            f"<i>({race_info['difficulty'].upper()} difficulty)</i>\n\n"
            f"<b>Question:</b>\n"
            f"<blockquote>{race_info['text']}</blockquote>\n"
            f"🏆 <b>Winner:</b> {winner_name} (+{base_xp} YP) in <b>{time_taken}s</b>!\n"
            f"Correct Answer: <b>{correct_text}</b>\n"
        )
        if explanation:
            win_text += f"💡 <i>{explanation}</i>\n"
            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Next Race ⚡", callback_data="lusy_play_race")]
        ])
        
        try:
            await callback.message.edit_text(
                text=win_text,
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception:
            pass
            
        # Clean up
        if chat_id in ACTIVE_GROUP_QUIZZES:
            del ACTIVE_GROUP_QUIZZES[chat_id]
        if race_key in ACTIVE_RACES:
            del ACTIVE_RACES[race_key]
            
        try:
            await callback.answer("🏆 You won the race!", show_alert=False)
        except Exception:
            pass
            
    else:
        # Eliminate the user
        race_info["locked_out"].add(user_id)
        try:
            await callback.answer("❌ Incorrect answer! You are eliminated from this round.", show_alert=True)
        except Exception:
            pass


@quiz_router.callback_query(F.data == "lusy_play_scramble")
async def choose_scramble_difficulty(callback: CallbackQuery):
    try:
        chat_id = callback.message.chat.id
        if callback.message.chat.type != "private":
            if chat_id in ACTIVE_GROUP_QUIZZES:
                await callback.answer("⚠️ An active quiz/race is already running in this group! Complete it first.", show_alert=True)
                return

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_vs_easy"),
                InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_vs_medium")
            ],
            [
                InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_vs_hard")
            ]
        ])
        await callback.message.edit_text(
            "🔠 <b>Choose Verse Scramble Difficulty!</b>\n"
            "Unscramble the verse to find the correct reference. Harder questions reward more YP.",
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error in choose_scramble_difficulty callback: {e}")
    finally:
        try:
            await callback.answer()
        except Exception:
            pass


async def on_scramble_command(message: Message, services: ServiceContainer):
    chat_id = message.chat.id
    if message.chat.type != "private":
        if chat_id in ACTIVE_GROUP_QUIZZES:
            await message.answer("⚠️ <b>Quiz in Progress!</b>\nAn active quiz is already running in this group. Answer the current quiz first!")
            return

    # Show difficulty selection menu for Verse Scramble
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_vs_easy"),
            InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_vs_medium")
        ],
        [
            InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_vs_hard")
        ]
    ])
    await message.answer(
        "🔠 <b>Choose Verse Scramble Difficulty!</b>\n"
        "Unscramble the verse to find the correct reference. Harder questions reward more YP.",
        parse_mode="HTML",
        reply_markup=markup
    )