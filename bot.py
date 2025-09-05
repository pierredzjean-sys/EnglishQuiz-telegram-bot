#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import random
from telegram import Bot

# ======================= CONFIG =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ex: "@moncanaledu" ou ID numérique -100...
DELAY_SECONDS = int(os.getenv("DELAY_SECONDS", "300"))

# Mode test : quiz toutes les TEST_INTERVAL_MINUTES minutes
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
async def send_quiz(bot, chat_id, theme, delay):
    q = random.choice(QUIZ_DATA[theme])
    await bot.send_poll(
        chat_id=chat_id,
        question=q["question"],
        options=q["options"],
        type="quiz",
        correct_option_id=q["answer"],
        is_anonymous=False
    )
    await asyncio.sleep(delay)
    await bot.send_message(
        chat_id=chat_id,
        text=f"✅ Réponse : {q['options'][q['answer']]}\n📘 Cours : {q['lesson']}"
    )

async def quiz_loop():
    bot = Bot(token=BOT_TOKEN)
    last_theme = "cybersecurity"
    while True:
        # Alterner les thèmes
        theme = "english" if last_theme=="cybersecurity" else "cybersecurity"
        last_theme = theme
        await send_quiz(bot, CHANNEL_ID, theme, DELAY_SECONDS)
        # Intervalle en secondes : mode test ou production
        interval = TEST_INTERVAL_MINUTES*60 if TEST_MODE else 24*60*60
        await asyncio.sleep(interval)

# ======================= MAIN =======================
async def main():
    print(f"🧪 Test mode ON: quiz toutes les {TEST_INTERVAL_MINUTES} min" if TEST_MODE else "Mode production activé")
    await quiz_loop()

if __name__=="__main__":
    asyncio.run(main())
