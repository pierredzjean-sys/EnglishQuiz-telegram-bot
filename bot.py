#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-publishing Telegram Quiz Bot for a Channel
- Themes: English learning and Cybersecurity
- Schedules: daily at 09:00 (English) and 18:00 (Cyber) -- Africa/Douala timezone
- Test mode: optional every N minutes
"""

import os
import asyncio
from datetime import time as dtime
from zoneinfo import ZoneInfo
import random

from telegram.ext import Application

# =============== Configuration via Environment Variables =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Required
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g. "@yourchannelusername" or numeric id like -1001234567890

# Scheduling
TIMEZONE = os.getenv("TIMEZONE", "Africa/Douala")
ENGLISH_HOUR = int(os.getenv("ENGLISH_HOUR", "9"))
ENGLISH_MINUTE = int(os.getenv("ENGLISH_MINUTE", "0"))
CYBER_HOUR = int(os.getenv("CYBER_HOUR", "18"))
CYBER_MINUTE = int(os.getenv("CYBER_MINUTE", "0"))

# Delay before revealing the answer (in seconds)
DELAY_SECONDS = int(os.getenv("DELAY_SECONDS", "300"))  # default 5 minutes

# Test mode (overrides daily schedules)
TEST_MODE = os.getenv("TEST_MODE", "0") == "1"
TEST_INTERVAL_MINUTES = int(os.getenv("TEST_INTERVAL_MINUTES", "2"))  # every 2 min by default

# =============================== Quiz Data ==================================
QUIZ_DATA = {
    "english": [
        {
            "question": "Choose the correct form: She ____ to school every day.",
            "options": ["go", "goes", "going", "gone"],
            "answer": 1,
            "lesson": "Avec 'she/he/it', on ajoute -s au verbe : She goes to school."
        },
        {
            "question": "Pick the correct word: I have ____ apple.",
            "options": ["a", "an", "the", "any"],
            "answer": 1,
            "lesson": "On utilise 'an' devant un son vocalique : an apple."
        },
        {
            "question": "Which sentence is correct?",
            "options": [
                "He don't like tea.",
                "He doesn't like tea.",
                "He doesn't likes tea.",
                "He not like tea."
            ],
            "answer": 1,
            "lesson": "À la 3e personne, auxiliaire 'does' + base verbale : He doesn't like tea."
        },
        {
            "question": "Find the synonym of 'begin'.",
            "options": ["Stop", "Finish", "Start", "End"],
            "answer": 2,
            "lesson": "'Begin' et 'start' sont généralement synonymes."
        },
        {
            "question": "Choose the correct preposition: I'm interested ___ music.",
            "options": ["on", "in", "at", "for"],
            "answer": 1,
            "lesson": "On dit 'interested in' : I'm interested in music."
        },
        {
            "question": "Past simple of 'go' is _____.",
            "options": ["goed", "go", "gone", "went"],
            "answer": 3,
            "lesson": "Le prétérit de 'go' est 'went'."
        },
        {
            "question": "Which is a question tag? 'You're from Cameroon, ____?'",
            "options": ["isn't you", "aren't you", "don't you", "won't you"],
            "answer": 1,
            "lesson": "Avec 'You are', le tag correct est 'aren't you?'"
        },
        {
            "question": "Choose the correct word: 'less' is used with ____ nouns.",
            "options": ["countable", "uncountable", "both", "proper"],
            "answer": 1,
            "lesson": "'Less' s'emploie surtout avec les noms indénombrables (uncountable)."
        }
    ],
    "cybersecurity": [
        {
            "question": "Qu’est-ce que le phishing ?",
            "options": [
                "Un virus informatique",
                "Un mail trompeur pour voler des infos",
                "Un antivirus",
                "Un pare-feu"
            ],
            "answer": 1,
            "lesson": "Le phishing vise à voler des données (mots de passe, cartes) via de faux messages."
        },
        {
            "question": "Quel est le plus sûr ?",
            "options": ["123456", "password", "M@n!2025#", "abcdef"],
            "answer": 2,
            "lesson": "Un mot de passe robuste : lettres, chiffres, symboles, au moins 12 caractères."
        },
        {
            "question": "MFA signifie :",
            "options": [
                "Multi-Factor Authentication",
                "Main File Access",
                "Malware Finder App",
                "Micro Firewall Adapter"
            ],
            "answer": 0,
            "lesson": "La MFA ajoute un second facteur (SMS, app, clé) pour se connecter en sécurité."
        },
        {
            "question": "WPA2/3 concerne :",
            "options": ["Sécurité Wi‑Fi", "Sauvegardes", "Navigateur", "Messagerie"],
            "answer": 0,
            "lesson": "WPA2/WPA3 sont des standards de chiffrement pour sécuriser les réseaux Wi‑Fi."
        },
        {
            "question": "Un ransomware :",
            "options": [
                "Chiffre vos fichiers pour rançon",
                "Protège votre PC",
                "Accélère Internet",
                "Supprime les spams"
            ],
            "answer": 0,
            "lesson": "Un rançongiciel chiffre les données et exige un paiement pour la clé."
        },
        {
            "question": "Bonne pratique d’email :",
            "options": [
                "Cliquer tous les liens",
                "Ouvrir les pièces jointes inconnues",
                "Vérifier l’expéditeur et l’URL",
                "Désactiver l’antivirus"
            ],
            "answer": 2,
            "lesson": "Toujours vérifier l'adresse, passer la souris sur les liens, douter des urgences."
        },
        {
            "question": "HTTPS signifie :",
            "options": [
                "Site non sécurisé",
                "Chiffrement entre navigateur et site",
                "Téléchargement rapide",
                "Bloque la pub"
            ],
            "answer": 1,
            "lesson": "HTTPS chiffre la connexion. Cherchez le cadenas dans la barre d'adresse."
        },
        {
            "question": "Sauvegardes recommandées :",
            "options": [
                "Jamais",
                "Une fois par an",
                "Règle 3‑2‑1",
                "Seulement sur USB"
            ],
            "answer": 2,
            "lesson": "3 copies, 2 supports différents, 1 hors site/Cloud = règle 3‑2‑1."
        }
    ]
}

# =========================== Core Functionality ==============================
async def send_quiz(application, chat_id, theme, delay_seconds):
    """Send a quiz poll, then reveal answer and mini-lesson after delay."""
    q = random.choice(QUIZ_DATA[theme])
    # Send poll
    message = await application.bot.send_poll(
        chat_id=chat_id,
        question=q["question"],
        options=q["options"],
        type="quiz",
        correct_option_id=q["answer"],
        is_anonymous=False
    )
    # Wait, then reveal
    await asyncio.sleep(delay_seconds)
    answer_text = f"✅ Réponse : {q['options'][q['answer']]}\n📘 Cours : {q['lesson']}"
    await application.bot.send_message(chat_id=chat_id, text=answer_text)


async def daily_english(context):
    await send_quiz(context.application, CHANNEL_ID, "english", DELAY_SECONDS)


async def daily_cyber(context):
    await send_quiz(context.application, CHANNEL_ID, "cybersecurity", DELAY_SECONDS)


async def test_cycle(context):
    """Alternate English and Cyber every TEST_INTERVAL_MINUTES minutes."""
    # Store last theme in job data
    last = context.job.data.get("last_theme", "cybersecurity")
    new_theme = "english" if last == "cybersecurity" else "cybersecurity"
    context.job.data["last_theme"] = new_theme
    await send_quiz(context.application, CHANNEL_ID, new_theme, DELAY_SECONDS)


async def on_startup(application):
    """Schedule jobs on startup."""
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ BOT_TOKEN or CHANNEL_ID missing. Set them in Environment Variables.")
        return

    tz = ZoneInfo(TIMEZONE)
    jq = application.job_queue

    if TEST_MODE:
        # Start quickly for testing
        first_seconds = 5  # start 5s after boot
        interval = TEST_INTERVAL_MINUTES * 60
        jq.run_repeating(test_cycle, interval=interval, first=first_seconds, data={"last_theme": "cybersecurity"})
        print(f"🧪 Test mode ON: a quiz every {TEST_INTERVAL_MINUTES} min (timezone {TIMEZONE}).")
    else:
        # Daily schedules
        jq.run_daily(daily_english, time=dtime(hour=ENGLISH_HOUR, minute=ENGLISH_MINUTE, tzinfo=tz))
        jq.run_daily(daily_cyber, time=dtime(hour=CYBER_HOUR, minute=CYBER_MINUTE, tzinfo=tz))
        print(f"⏰ Scheduled daily: English {ENGLISH_HOUR:02d}:{ENGLISH_MINUTE:02d} & Cyber {CYBER_HOUR:02d}:{CYBER_MINUTE:02d} ({TIMEZONE}).")

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    # schedule jobs and then run polling (keeps the app alive)
    await on_startup(application)
    await application.run_polling(close_loop=False)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
