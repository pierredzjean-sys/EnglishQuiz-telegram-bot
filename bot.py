#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram Quiz Auto-publiante (Version test)
- Quiz anglais et cybersécurité
- Publie toutes les 2 minutes en mode test
"""

import os
import asyncio
import random
from telegram.ext import ApplicationBuilder

# ======================= CONFIG =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ex: "@moncanaledu" ou ID numérique -100...
DELAY_SECONDS = int(os.getenv("DELAY_SECONDS", "300"))
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

# ======================= FONCTIONS =======================
async def send_quiz(app, chat_id, theme, delay):
    q = random.choice(QUIZ_DATA[theme])
    await app.bot.send_poll(
        chat_id=chat_id,
        question=q["question"],
        options=q["options"],
        type="quiz",
        correct_option_id=q["answer"],
        is_anonymous=False
    )
    await asyncio.sleep(delay)
    await app.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Réponse : {q['options'][q['answer']]}\n📘 Cours : {q['lesson']}"
    )

async def test_cycle(context):
    """Alterne les thèmes pour le test."""
    last = context.job.data.get("last_theme", "cybersecurity")
    new_theme = "english" if last=="cybersecurity" else "cybersecurity"
    context.job.data["last_theme"] = new_theme
    await send_quiz(context.application, CHANNEL_ID, new_theme, DELAY_SECONDS)

# ======================= MAIN =======================
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    if TEST_MODE:
        print(f"🧪 Test mode ON: quiz toutes les {TEST_INTERVAL_MINUTES} min")
        job_queue = app.job_queue
        job_queue.run_repeating(
            test_cycle,
            interval=TEST_INTERVAL_MINUTES*60,
            first=5,
            data={"last_theme":"cybersecurity"}
        )
    await app.run_polling(close_loop=False)

if __name__=="__main__":
    import asyncio
    asyncio.run(main())
