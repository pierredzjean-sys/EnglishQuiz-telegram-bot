#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import random
from telegram import Bot, Poll
from telegram.ext import ApplicationBuilder, PollHandler, ContextTypes

# ======================= CONFIG =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")  # ID numérique du groupe (-1001234567890)
DELAY_AFTER_POLL = int(os.getenv("DELAY_AFTER_POLL", "10"))  # secondes avant afficher la réponse
TEST_MODE = True
TEST_INTERVAL_MINUTES = 2

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
    "cybersecurity":[
        {"question":"Qu’est-ce que le phishing ?",
         "options":["Un virus informatique","Un mail trompeur pour voler des infos","Un antivirus","Un pare-feu"],
         "answer":1,"lesson":"Le phishing vise à voler des données via de faux messages."},
        {"question":"Quel est le mot de passe le plus sécurisé ?",
         "options":["123456","password","M@n!2025#","abcdef"],
         "answer":2,"lesson":"Mot de passe robuste : lettres, chiffres, symboles, au moins 12 caractères."}
    ]
}

# ======================= GLOBAL =======================
current_quiz = {}  # poll_id : {quiz info, message_id, chat_id, answered_users}

# ======================= FONCTIONS =======================
async def send_quiz(bot, chat_id, theme):
    q = random.choice(QUIZ_DATA[theme])
    poll_message = await bot.send_poll(
        chat_id=chat_id,
        question=q["question"],
        options=q["options"],
        type=Poll.QUIZ,
        correct_option_id=q["answer"],
        is_anonymous=False  # permet de voir qui répond
    )
    current_quiz[poll_message.poll.id] = {
        "quiz": q,
        "message_id": poll_message.message_id,
        "chat_id": chat_id,
        "answered_users": {}
    }

async def handle_poll_answer(update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = update.poll_answer.poll_id
    user = update.poll_answer.user
    option_ids = update.poll_answer.option_ids
    if poll_id in current_quiz:
        quiz_entry = current_quiz[poll_id]
        quiz_entry["answered_users"][user.id] = option_ids[0]
        quiz = quiz_entry["quiz"]
        selected = option_ids[0]
        print(f"{user.first_name} a choisi {quiz['options'][selected]} à la question : {quiz['question']}")

async def reveal_answers(bot):
    while True:
        for poll_id, entry in list(current_quiz.items()):
            if entry["answered_users"]:
                await asyncio.sleep(DELAY_AFTER_POLL)
                quiz = entry["quiz"]
                chat_id = entry["chat_id"]
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ Réponse : {quiz['options'][quiz['answer']]}\n📘 Cours : {quiz['lesson']}"
                )
                current_quiz.pop(poll_id)  # supprimer après affichage
        await asyncio.sleep(1)

async def quiz_loop(bot):
    last_theme = "cybersecurity"
    while True:
        theme = "english" if last_theme=="cybersecurity" else "cybersecurity"
        last_theme = theme
        await send_quiz(bot, GROUP_ID, theme)
        interval = TEST_INTERVAL_MINUTES*60 if TEST_MODE else 24*60*60
        await asyncio.sleep(interval)

# ======================= MAIN =======================
async def main():
    print(f"🧪 Test mode ON: quiz toutes les {TEST_INTERVAL_MINUTES} min" if TEST_MODE else "Mode production activé")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(PollHandler(handle_poll_answer))
    bot = app.bot

    # lancer les deux boucles simultanément
    await asyncio.gather(
        quiz_loop(bot),
    reveal_answers(bot)
    )

if __name__=="__main__":
    asyncio.run(main())
