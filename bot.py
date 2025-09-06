#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes, PollAnswerHandler
)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "-1002882014486"))  # Ton groupe
QUIZ_DURATION = 20  # en secondes

# ================= QUIZ DATA =================
QUIZ_DATA = [
    {
        "question": "Choose the correct form: She ____ to school every day.",
        "options": ["go", "goes", "going", "gone"],
        "answer": 1,
        "lesson": "Avec 'she/he/it', on ajoute -s : She goes to school."
    },
    {
        "question": "What is the opposite of 'difficult'?",
        "options": ["Hard", "Easy", "Complicated", "Tough"],
        "answer": 1,
        "lesson": "Le contraire de 'difficult' est 'easy'."
    },
    {
        "question": "Complete: If I ____ time, I will help you.",
        "options": ["have", "had", "will have", "having"],
        "answer": 0,
        "lesson": "Conditionnel réel (1st conditional) : If + present simple, will + base verbale."
    }
    # 👉 Ajoute ici plus de questions A1 → C1
]

# ================= ETAT GLOBAL =================
active_session = False
scores = {}
current_poll_id = None
current_correct = None


# ================= FONCTIONS =================
async def start_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_session, scores

    if active_session:
        await update.message.reply_text("⚠️ Une session est déjà en cours.")
        return

    try:
        n = int(context.args[0]) if context.args else 5
    except ValueError:
        n = 5

    scores = {}
    active_session = True
    await update.message.reply_text(f"🎯 Session démarrée avec {n} questions !")

    for i in range(n):
        if not active_session:
            break
        await send_quiz(context)
        await asyncio.sleep(QUIZ_DURATION + 5)  # temps du quiz + pause entre les questions

    if active_session:
        await stop_session(update, context)


async def stop_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_session
    if not active_session:
        await update.message.reply_text("⚠️ Pas de session en cours.")
        return

    active_session = False
    if scores:
        classement = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        msg = "🏆 Résultats finaux :\n\n"
        for i, (user, pts) in enumerate(classement, 1):
            msg += f"{i}. {user} — {pts} pts\n"
    else:
        msg = "Aucun participant n’a répondu 😅."

    await context.bot.send_message(GROUP_ID, msg)


async def send_quiz(context: ContextTypes.DEFAULT_TYPE):
    global current_poll_id, current_correct

    q = random.choice(QUIZ_DATA)
    poll = await context.bot.send_poll(
        chat_id=GROUP_ID,
        question=q["question"],
        options=q["options"],
        type="quiz",
        correct_option_id=q["answer"],
        is_anonymous=False
    )
    current_poll_id = poll.poll.id
    current_correct = q["answer"]

    # Affichage du compte à rebours
    for sec in range(QUIZ_DURATION, 0, -5):
        await asyncio.sleep(5)
        await context.bot.send_message(GROUP_ID, f"⏳ Il reste {sec} sec...")

    # Réponse
    await context.bot.send_message(
        GROUP_ID,
        f"✅ Réponse : {q['options'][q['answer']]}\n📘 Cours : {q['lesson']}"
    )


async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global scores
    answer = update.poll_answer
    user = answer.user.first_name

    if answer.option_ids and answer.option_ids[0] == current_correct:
        scores[user] = scores.get(user, 0) + 1


# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("startsession", start_session))
    app.add_handler(CommandHandler("stopsession", stop_session))
    app.add_handler(PollAnswerHandler(receive_poll_answer))
    print("🤖 Bot prêt : /startsession [n], /stopsession")
    app.run_polling()


if name == "__main__":
    main()
