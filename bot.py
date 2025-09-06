#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "-1002882014486"))  # Mets ton vrai ID de groupe
PORT = int(os.getenv("PORT", "8080"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # l’URL Render de ton service

# ================= QUIZ DATA (exemple A1-C1 simplifié) =================
QUIZ_DATA = [
    {"question": "Choose the correct form: She ____ to school every day.",
     "options": ["go", "goes", "going", "gone"],
     "answer": 1, "lesson": "Avec 'she/he/it', on ajoute -s : She goes to school."},

    {"question": "What is the opposite of 'difficult'?",
     "options": ["Hard", "Easy", "Complicated", "Tough"],
     "answer": 1, "lesson": "Le contraire de 'difficult' est 'easy'."}
]

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot prêt. Tape /quiz pour lancer un quiz !")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(QUIZ_DATA)
    poll = await update.message.reply_poll(
        question=q["question"],
        options=q["options"],
        type="quiz",
        correct_option_id=q["answer"],
        is_anonymous=False
    )
    # Sauvegarde la bonne réponse pour l’expliquer ensuite
    context.chat_data["last_quiz"] = q

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 Session stoppée par l’admin.")

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("stop", stop))

    # Lancement en webhook (pas polling !)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

if name == "__main__":
    main()
