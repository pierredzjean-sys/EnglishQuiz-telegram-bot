#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import random
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, PollAnswerHandler

# ======================= CONFIG =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1002882014486
QUIZ_DURATION = 20  # secondes

# ======================= QUIZ DATA =======================
QUIZ_DATA = {
    "english": [
        {"question":"Choose the correct form: She ____ to school every day.",
         "options":["go","goes","going","gone"],
         "answer":1,"lesson":"Avec 'she/he/it', on ajoute -s : She goes to school."},
        {"question":"What is the opposite of 'difficult'?",
         "options":["Hard","Easy","Complicated","Tough"],
         "answer":1,"lesson":"Le contraire de 'difficult' est 'easy'."}
    ],
    "cyber": [
        {"question":"Qu’est-ce que le phishing ?",
         "options":["Un virus informatique","Un mail trompeur pour voler des infos","Un antivirus","Un pare-feu"],
         "answer":1,"lesson":"Le phishing vise à voler des données via de faux messages."},
        {"question":"Quel est le mot de passe le plus sécurisé ?",
         "options":["123456","password","M@n!2025#","abcdef"],
         "answer":2,"lesson":"Mot de passe robuste : lettres, chiffres, symboles, au moins 12 caractères."}
    ]
}

# ======================= VARIABLES =======================
current_quiz = None
quiz_answers = {}
quiz_task = None

# ======================= FONCTIONS =======================
async def send_quiz(bot, chat_id, theme, started_by):
    global current_quiz, quiz_answers, quiz_task

    q = random.choice(QUIZ_DATA[theme])
    quiz_answers = {}  # reset des réponses

    poll_message = await bot.send_poll(
        chat_id=chat_id,
        question=f"⏳ {QUIZ_DURATION}s - {q['question']}\n👨‍🏫 Lancé par: {started_by}",
        options=q["options"],
        type="quiz",
        correct_option_id=q["answer"],
        is_anonymous=False
    )

    current_quiz = {"question": q, "message_id": poll_message.message_id, "chat_id": chat_id}

    # Timer automatique
    quiz_task = asyncio.create_task(end_quiz(bot))

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global quiz_answers, current_quiz
    if not current_quiz:
        return

    user = update.effective_user
    ans = update.poll_answer.option_ids[0] if update.poll_answer.option_ids else None
    quiz_answers[user.full_name] = ans

async def end_quiz(bot: Bot, forced=False):
    global current_quiz, quiz_answers, quiz_task
    if not current_quiz:
        return

    q = current_quiz["question"]
    chat_id = current_quiz["chat_id"]

    # ✅ Déterminer les gagnants
    correct_id = q["answer"]
    winners = [name for name, ans in quiz_answers.items() if ans == correct_id]

    # 🏆 Classement (les premiers à répondre juste sont devant)
    classement = "\n".join([f"{i+1}. {name}" for i, name in enumerate(winners)]) if winners else "❌ Personne n’a trouvé."

    # Envoi du résultat
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

# ======================= COMMANDES =======================
async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = await context.bot.get_chat(GROUP_ID)
    member = await chat.get_member(update.effective_user.id)
    if not (member.status in ["administrator", "creator"]):
        await update.message.reply_text("❌ Seuls les administrateurs peuvent lancer un quiz.")
        return

    theme = context.args[0].lower() if context.args else random.choice(list(QUIZ_DATA.keys()))
    if theme not in QUIZ_DATA:
        await update.message.reply_text("⚠️ Thème inconnu. Utilise /quiz english ou /quiz cyber.")
        return
        await send_quiz(context.bot, update.effective_chat.id, theme, update.effective_user.full_name)

async def stop_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = await context.bot.get_chat(GROUP_ID)
    member = await chat.get_member(update.effective_user.id)
    if not (member.status in ["administrator", "creator"]):
        await update.message.reply_text("❌ Seuls les administrateurs peuvent arrêter un quiz.")
        return

    await end_quiz(context.bot, forced=True)

# ======================= MAIN =======================
async def main():
    print("🤖 Bot prêt : /quiz, /quiz english, /quiz cyber, /stopquiz")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CommandHandler("stopquiz", stop_quiz_command))
    app.add_handler(PollAnswerHandler(handle_poll_answer))

    await app.run_polling()

if __name__=="__main__":
    asyncio.run(main())
        
