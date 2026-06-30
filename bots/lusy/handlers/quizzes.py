from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, PollAnswer
from shared.services.container import ServiceContainer
import random

quiz_router = Router()



@quiz_router.callback_query(F.data == "lusy_soon")
async def on_soon(callback: CallbackQuery):
    await callback.answer("This game mode is coming soon!", show_alert=True)

@quiz_router.callback_query(F.data == "lusy_play_quiz")
async def start_quiz(callback: CallbackQuery, services: ServiceContainer):
    user = await services.identity.resolve_telegram_user(callback.from_user)
    user_id = user["id"]
    
    # 1. Fetch all multiple choice questions
    # In a production app, we would do a complex SQL query to exclude already answered questions.
    # For now, let's fetch all active MCQs.
    questions_resp = await services.supabase.find_many("lusy_questions", {"game_type": "multiple_choice", "is_active": True})
    
    if not questions_resp:
        await callback.message.answer("No quiz questions found in the database yet!")
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
        
    # Send a native Telegram Quiz Poll!
    sent_poll = await callback.message.answer_poll(
        question=f"[{question_record.get('difficulty').upper()}] {text}",
        options=options,
        type="quiz",
        correct_option_id=correct_idx,
        explanation=explanation,
        is_anonymous=False # Must be false so we know WHO answered it!
    )
    
    # Save the mapping of poll_id -> question_id so we can award XP when they answer
    await services.supabase.upsert(
        "bot_user_state",
        {
            "user_id": user_id,
            "bot_name": "lusy_poll_tracking",
            "state": {"poll_id": sent_poll.poll.id, "question_id": q_id, "base_xp": question_record.get("base_xp", 10)}
        },
        on_conflict="user_id, bot_name"
    )
    
    await callback.answer()

@quiz_router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, services: ServiceContainer):
    # This triggers when a user selects an option in the poll!
    user = await services.identity.resolve_telegram_user(poll_answer.user)
    user_id = user["id"]
    
    # Find the tracked poll data
    state_record = await services.supabase.find_one_multi("bot_user_state", {"user_id": user_id, "bot_name": "lusy_poll_tracking"})
    if not state_record:
        return
        
    state = state_record.get("state", {})
    if state.get("poll_id") != poll_answer.poll_id:
        return # Not a poll we are currently tracking
        
    question_id = state.get("question_id")
    base_xp = state.get("base_xp", 10)
    
    # Fetch the original question to check the correct answer index
    q_resp = await services.supabase.find_one("lusy_questions", "id", question_id)
    if not q_resp:
        return
        
    content = q_resp.get("content", {})
    options = content.get("options", [])
    correct_text = q_resp.get("correct_answer")
    correct_idx = options.index(correct_text) if correct_text in options else 0
    
    # Did they get it right? (poll_answer.option_ids is a list of selected indexes)
    is_correct = correct_idx in poll_answer.option_ids
    xp_awarded = base_xp if is_correct else 0
    
    # Log it in the Game History!
    import datetime
    await services.supabase.insert("lusy_game_history", {
        "user_id": user_id,
        "question_id": question_id,
        "is_correct": is_correct,
        "xp_earned": xp_awarded,
        "answered_at": datetime.datetime.utcnow().isoformat()
    })
    
    # Award actual XP if correct
    if is_correct:
        await services.xp.add_xp(user_id, xp_awarded, "lusy", f"Bible Quiz: {question_id}")
        
    # Clear the tracking state so they can't double answer
    await services.supabase.client.table("bot_user_state").delete().eq("user_id", user_id).eq("bot_name", "lusy_poll_tracking").execute()