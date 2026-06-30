from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, PollAnswer
from aiogram import Bot
from shared.services.container import ServiceContainer
import random
import asyncio
import datetime

quiz_router = Router()

# In-memory tracking for active quiz polls
# poll_id (str) -> {question_id, base_xp, is_group, chat_id, message_id, votes, max_votes, closed}
ACTIVE_POLLS = {}

# In-memory tracking for active group quizzes: chat_id (int) -> poll_id (str)
ACTIVE_GROUP_QUIZZES = {}


@quiz_router.callback_query(F.data == "lusy_soon")
async def on_soon(callback: CallbackQuery):
    await callback.answer("This game mode is coming soon!", show_alert=True)


@quiz_router.callback_query(F.data == "lusy_play_quiz")
async def choose_difficulty(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if callback.message.chat.type != "private":
        if chat_id in ACTIVE_GROUP_QUIZZES:
            await callback.answer("⚠️ An active quiz is already running in this group! Complete it first.", show_alert=True)
            return

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_easy"),
            InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_medium")
        ],
        [
            InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_hard")
        ]
    ])
    await callback.message.edit_text("<b>Choose your Difficulty Level!</b>\nHarder questions reward more YP.", parse_mode="HTML", reply_markup=markup)
    await callback.answer()


@quiz_router.callback_query(F.data.startswith("lusy_quiz_diff_"))
async def start_quiz(callback: CallbackQuery, services: ServiceContainer):
    difficulty = callback.data.split("_")[-1] # easy, medium, or hard
    chat_id = callback.message.chat.id
    is_group = callback.message.chat.type != "private"
    
    if is_group and chat_id in ACTIVE_GROUP_QUIZZES:
        await callback.answer("⚠️ An active quiz is already running in this group!", show_alert=True)
        return

    user = await services.identity.resolve_telegram_user(callback.from_user)
    user_id = user["id"]
    
    # 1. Fetch questions matching this difficulty
    questions_resp = await services.supabase.find_many("lusy_questions", {"game_type": "multiple_choice", "difficulty": difficulty, "is_active": True})
    
    if not questions_resp:
        await callback.message.edit_text(f"No {difficulty} quiz questions found in the database yet! Please try another difficulty.")
        await callback.answer()
        return
        
    # 2. Pick a random question
    question_record = random.choice(questions_resp)
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
            await callback.message.edit_text("<b>Quiz started! Check the poll below.</b>", parse_mode="HTML")
        except Exception:
            pass
        
    # Send a native Telegram Quiz Poll!
    sent_poll = await callback.message.answer_poll(
        question=f"[{difficulty.upper()}] {text}",
        options=options,
        type="quiz",
        correct_option_id=correct_idx,
        explanation=explanation if explanation else None,
        is_anonymous=False # Must be false so we know WHO answered it!
    )
    
    if not is_group:
        # Save the mapping of poll_id -> question_id so we can award XP when they answer (only for DMs)
        await services.supabase.upsert(
            "bot_user_state",
            {
                "user_id": user_id,
                "bot_name": "lusy_poll_tracking",
                "state": {"poll_id": sent_poll.poll.id, "question_id": q_id, "base_xp": question_record.get("base_xp", 10)}
            },
            on_conflict="user_id, bot_name"
        )
    else:
        # Set active group quiz status
        ACTIVE_GROUP_QUIZZES[chat_id] = sent_poll.poll.id
    
    # Track globally in memory
    ACTIVE_POLLS[sent_poll.poll.id] = {
        "question_id": q_id,
        "base_xp": question_record.get("base_xp", 10),
        "is_group": is_group,
        "chat_id": chat_id,
        "message_id": sent_poll.message_id,
        "votes": {}, # user_id -> { "display_name": str, "is_correct": bool }
        "max_votes": 5, # Close group poll after 5 votes
        "closed": False
    }
    
    # Schedule timeout fallback for group polls (e.g. 5 minutes)
    if is_group:
        asyncio.create_task(group_poll_timeout(sent_poll.poll.id, chat_id, sent_poll.message_id, services, callback.bot))
        
    await callback.answer()


async def group_poll_timeout(poll_id: str, chat_id: int, message_id: int, services: ServiceContainer, bot: Bot):
    # Wait for 5 minutes (300 seconds)
    await asyncio.sleep(300)
    poll_info = ACTIVE_POLLS.get(poll_id)
    if poll_info and not poll_info.get("closed", False):
        await close_and_reward_group_poll(poll_id, services, bot)


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
    
    # 1. Stop the poll on Telegram
    try:
        await bot.stop_poll(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
        
    # 2. Fetch correct answer details for display
    q_resp = await services.supabase.find_one("lusy_questions", "id", question_id)
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
        await services.supabase.insert("lusy_game_history", {
            "user_id": voter_id,
            "question_id": question_id,
            "is_correct": is_correct,
            "xp_earned": xp_earned,
            "answered_at": datetime.datetime.utcnow().isoformat()
        })
        
        if is_correct:
            # Award YP
            await services.xp.award_xp(voter_id, xp_earned, "lusy", f"Group Bible Quiz: {question_id}")
            winners.append(display_name)
            
    # 4. Format and send summary message in the group
    leaderboard_text = "<b>🏆 Quiz Completed!</b>\n"
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
        [InlineKeyboardButton(text="Next Question ➡️", callback_data="lusy_play_quiz")]
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
    q_resp = await services.supabase.find_one("lusy_questions", "id", question_id)
    if not q_resp:
        return
        
    content = q_resp.get("content", {})
    options = content.get("options", [])
    correct_text = q_resp.get("correct_answer")
    correct_idx = options.index(correct_text) if correct_text in options else 0
    
    is_correct = correct_idx in poll_answer.option_ids
    
    if not is_group:
        # Private poll flow: award instantly and send DM
        xp_awarded = base_xp if is_correct else 0
        await services.supabase.insert("lusy_game_history", {
            "user_id": user_id,
            "question_id": question_id,
            "is_correct": is_correct,
            "xp_earned": xp_awarded,
            "answered_at": datetime.datetime.utcnow().isoformat()
        })
        if is_correct:
            await services.xp.award_xp(user_id, xp_awarded, "lusy", f"Bible Quiz: {question_id}")
            
        def _delete_state():
            services.supabase.client.table("bot_user_state").delete().eq("user_id", user_id).eq("bot_name", "lusy_poll_tracking").execute()
        await asyncio.to_thread(_delete_state)
        
        if poll_id in ACTIVE_POLLS:
            del ACTIVE_POLLS[poll_id]
            
        result_text = f"Correct! 🎉 +{xp_awarded} YP!" if is_correct else "Incorrect! ❌"
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Next Question ➡️", callback_data="lusy_play_quiz")]
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
            InlineKeyboardButton(text="Easy (10 YP)", callback_data="lusy_quiz_diff_easy"),
            InlineKeyboardButton(text="Medium (15 YP)", callback_data="lusy_quiz_diff_medium")
        ],
        [
            InlineKeyboardButton(text="Hard (20 YP)", callback_data="lusy_quiz_diff_hard")
        ]
    ])
    await message.answer("<b>Choose your Difficulty Level!</b>\nHarder questions reward more YP.", parse_mode="HTML", reply_markup=markup)