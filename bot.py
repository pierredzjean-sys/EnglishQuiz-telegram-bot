import os
import asyncio
import random
from telegram import Bot, Poll

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = "@MonGroupePublic"  # ton groupe public
DELAY_AFTER_POLL = 10
TEST_MODE = True
TEST_INTERVAL_MINUTES = 2

QUIZ_DATA = {
    "english": [
        {"question":"Choose the correct form: She ____ to school every day.",
         "options":["go","goes","going","gone"],
         "answer":1,"lesson":"Avec 'she/he/it', on ajoute -s : She goes to school."}
    ],
    "cybersecurity":[
        {"question":"Qu’est-ce que le phishing ?",
         "options":["Un virus informatique","Un mail trompeur pour voler des infos","Un antivirus","Un pare-feu"],
         "answer":1,"lesson":"Le phishing vise à voler des données via de faux messages."}
    ]
}

current_quiz = {}

async def send_quiz(bot, chat_id, theme):
    q = random.choice(QUIZ_DATA[theme])
    poll_message = await bot.send_poll(
        chat_id=chat_id,
        question=q["question"],
        options=q["options"],
        type=Poll.QUIZ,
        correct_option_id=q["answer"],
        is_anonymous=False
    )
    current_quiz[poll_message.poll.id] = {
        "quiz": q,
        "message_id": poll_message.message_id,
        "chat_id": chat_id,
        "answered_users": {}
    }

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
                current_quiz.pop(poll_id)
        await asyncio.sleep(1)

async def quiz_loop(bot):
    last_theme = "cybersecurity"
    while True:
        theme = "english" if last_theme=="cybersecurity" else "cybersecurity"
        last_theme = theme
        await send_quiz(bot, GROUP_ID, theme)
        interval = TEST_INTERVAL_MINUTES*60 if TEST_MODE else 24*60*60
        await asyncio.sleep(interval)

async def main():
    print(f"🧪 Test mode ON: quiz toutes les {TEST_INTERVAL_MINUTES} min" if TEST_MODE else "Mode production activé")
    bot = Bot(BOT_TOKEN)
    await asyncio.gather(
        quiz_loop(bot),
        reveal_answers(bot)
    )

if __name__=="__main__":
    asyncio.run(main())
