#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "-1002882014486"))  # ID du groupe
PORT = int(os.getenv("PORT", "8080"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL Render

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
        "question": "Which tense is used here: 'I have been studying English for 2 years'?",
        "options": ["Past Simple", "Present Perfect", "Present Perfect Continuous", "Future"],
        "answer": 2,
        "lesson": "C’est du Present Perfect Continuous : action qui continue jusqu’au présent."
    }
]

# ================= SESSION STATE =================
sessions = {}  # chat_id → { "running": bool, "scores": {} }

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot prêt. Utilise /startsession [n] pour lancer un quiz.")

async def startsession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Utilisation : /startsession [nombre_de_questions]")
        return

    try:
        num_q = int(context.args[0])
    except ValueError:
        await update.message.reply_text("⚠️ Mets un nombre valide.")
        return

    sessions[chat_id] = {"running": True, "scores": {}}
    await update.message.reply_text(f"🚀 Session lancée avec {num_q} questions (20 sec chacune) !")

    for i in range(num_q):
        if not sessions[chat_id]["running"]:
            break
        await send_quiz(chat_id, context)

    # Afficher classement
    scores = sessions[chat_id]["scores"]
    if scores:
        classement = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        msg = "🏆 Classement final :\n"
        for idx, (user, pts) in enumerate(classement, 1):
            msg += f"{idx}. {user} → {pts} pts\n"
        await context.bot.send_message(chat_id, msg)
    else:
        await context.bot.send_message(chat_id, "Aucun participant.")

    sessions[chat_id]["running"] = False

async def stopsession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in sessions:
        sessions[chat_id]["running"] = False
        await update.message.reply_text("🛑 Session stoppée par l’admin.")

async def send_quiz(chat_id, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(QUIZ_DATA)
    message = await context.bot.send_message(
        chat_id,
        f"❓ {q['question']}\nOptions: " + ", ".join(
            f"{i+1}. {opt}" for i, opt in enumerate(q["options"])
        ) + "\n\n⏳ Vous avez 20 sec..."
    )

    # attendre 20 sec
    await asyncio.sleep(20)

    await context.bot.send_message(
        chat_id,
        f"✅ Réponse correcte : {q['options'][q['answer']]}\n📘 Cours : {q['lesson']}"
    )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("startsession", startsession))
    app.add_handler(CommandHandler("stopsession", stopsession))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

if name == "__main__":
    main()
