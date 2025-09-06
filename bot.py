#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import random
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, PollAnswerHandler

# ======================= CONFIG =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1002882014486
QUIZ_DURATION = 20  # secondes
TIMER_INTERVAL = 5  # intervalle compte à rebours

# ======================= QUIZ DATA =======================
QUIZ_DATA = {
    "A1": [
        {"question":"What is the plural of 'cat'?",
         "options":["cats","cat","cates","catt"],
         "answer":0,"lesson":"Plural of most nouns: add -s → cats."},
        {"question":"Choose the correct form: I ____ a book.",
         "options":["am read","reads","read","reading"],
         "answer":2,"lesson":"Use simple present for 'I': I read a book."}
    ],
    "A2": [
        {"question":"Select the correct word: She ___ happy.",
         "options":["is","are","am","be"],
         "answer":0,"lesson":"Use 'is' for third person singular."},
    ],
    "B1": [
        {"question":"I have been living here ____ 2010.",
         "options":["since","for","from","at"],
         "answer":0,"lesson":"Use 'since' to indicate the starting point in time."},
    ],
    "B2": [
        {"question":"Choose the correct sentence:",
         "options":["He suggested to go","He suggested going","He suggested go","He suggested went"],
         "answer":1,"lesson":"After 'suggest', use gerund (verb+ing)."},
    ],
    "C1": [
        {"question":"Identify the correct idiom meaning 'very easy':",
         "options":["A piece of cake","Break a leg","Hit the sack","Let the cat out of the bag"],
         "answer":0,"lesson":"'A piece of cake' means something is very easy."},
    ]
}

# ======================= VARIABLES =======================
current_quiz = None
quiz_answers = {}
quiz_task = None
session_task = None
session_running = False

# ======================= FONCTIONS =======================
async def send_quiz(bot, chat_id, q):
    """Envoie une question avec compte à rebours et collecte des réponses."""
    global current_quiz, quiz_answers, quiz_task
    quiz_answers = {}

    poll_message = await bot.send_poll(
        chat_id=chat_id,
        question=f"⏳ {QUIZ_DURATION}s - {q['question']}",
        options=q["options"],
        type="quiz",
        correct_option_id=q["answer"],
        is_anonymous=False
    )

    current_quiz = {"question": q, "message_id": poll_message.message_id, "chat_id": chat_id}
    quiz_task = asyncio.create_task(countdown(bot, chat_id, poll_message.message_id, q))

async def countdown(bot, chat_id, message_id, q):
    """Compte à rebours visible toutes les TIMER_INTERVAL secondes."""
    global current_quiz, quiz_answers, quiz_task
    remaining = QUIZ_DURATION
    try:
        while remaining > 0:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"⏳ {remaining}s - {q['question']}"
            )
            await asyncio.sleep(TIMER_INTERVAL)
            remaining -= TIMER_INTERVAL
        await end_quiz(bot)
    except asyncio.CancelledError:
        pass

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collecte les réponses des utilisateurs."""
    global quiz_answers, current_quiz
    if not current_quiz:
        return
    user = update.effective_user
    ans = update.poll_answer.option_ids[0] if update.poll_answer.option_ids else None
    quiz_answers[user.full_name] = ans

async def end_quiz(bot: Bot, forced=False):
    """Affiche la réponse, le mini-cours et le classement."""
    global current_quiz, quiz_answers, quiz_task, session_running, session_task
    if not current_quiz:
        return

    q = current_quiz["question"]
    chat_id = current_quiz["chat_id"]

    correct_id = q["answer"]
    winners = [name for name, ans in quiz_answers.items() if ans == correct_id]
    classement = "\n".join([f"{i+1}.{name}" for i, name in enumerate(winners)]) if winners else "❌ Personne n’a trouvé."

    await bot.send_message(
        chat_id=chat_id,
        text=f"✅ Réponse correcte : {q['options'][q['answer']]}\n"
             f"📘 Cours : {q['lesson']}\n\n"
             f"🏆 Classement :\n{classement}"
    )

    current_quiz = None
    quiz_answers = {}
    if quiz_task:
        quiz_task.cancel()
        quiz_task = None

    # Passer à la prochaine question si session active
    if session_running and session_task and not forced:
        session_task.get_loop().call_soon_threadsafe(lambda: None)  # pour relancer la boucle

# ======================= SESSION =======================
async def session(bot: Bot, chat_id, n_questions):
    """Lance n_questions consécutives de niveaux variés."""
    global session_running, session_task
    session_running = True
    session_task = asyncio.current_task()

    levels = list(QUIZ_DATA.keys())
    for i in range(n_questions):
        if not session_running:
            break
        level = random.choice(levels)
        question = random.choice(QUIZ_DATA[level])
        await send_quiz(bot, chat_id, question)
        # Attendre que la question se termine
        while current_quiz:
            await asyncio.sleep(1)

    session_running = False

# ======================= COMMANDES =======================
async def start_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande admin: /startsession [nombre]"""
    global session_running
    chat = await context.bot.get_chat(GROUP_ID)
    member = await chat.get_member(update.effective_user.id)
    if not member.status in ["administrator", "creator"]:
        await update.message.reply_text("❌ Seuls les admins peuvent lancer une session.")
        return

    if session_running:
        await update.message.reply_text("⚠️ Une session est déjà en cours.")
        return

    try:
        n_questions = int(context.args[0]) if context.args else 5
    except:
        n_questions = 5

    await update.message.reply_text(f"✅ Session de {n_questions} questions lancée !")
    asyncio.create_task(session(context.bot, update.effective_chat.id, n_questions))

async def stop_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande admin: /stopsession"""
    global session_running, current_quiz
    chat = await context.bot.get_chat(GROUP_ID)
    member = await chat.get_member(update.effective_user.id)
    if not member.status in ["administrator", "creator"]:
        await update.message.reply_text("❌ Seuls les admins peuvent arrêter la session.")
        return

    session_running = False
    if current_quiz:
        await end_quiz(context.bot, forced=True)
    await update.message.reply_text("⏹️ Session arrêtée !")

# ======================= MAIN =======================
def main():
    print("🤖 Bot prêt : /startsession [n], /stopsession")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("startsession", start_session))
    app.add_handler(CommandHandler("stopsession", stop_session))
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.run_polling()

if __name__=="__main__":
    main()
