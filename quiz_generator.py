import json
import random
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

QUESTIONS_FILE = "questions_group.json"

def load_questions():
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

async def send_random_question(app, chat_id):
    data = load_questions()
    group_key = str(chat_id)
    if group_key in data and data[group_key]:
        question = random.choice(data[group_key])
        await app.send_message(
            chat_id,
            f"❓ {question}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("إظهار الإجابة ✅", callback_data="show_answer")]
            ])
        )
    else:
        await app.send_message(chat_id, "📭 لا توجد أسئلة بعد في هذا الجروب.")
