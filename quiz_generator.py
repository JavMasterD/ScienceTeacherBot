import json
import os
import random
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

QUESTIONS_FILE = "questions_group.json"

# تحميل الأسئلة
if not os.path.exists(QUESTIONS_FILE):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    questions_data = json.load(f)

def save_questions():
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)

# استخراج اسم المرحلة من عنوان الجروب
def extract_class_term(group_title):
    grade = next((s for s in ["الرابع", "الخامس", "السادس", "الأول", "الثاني", "الثالث"] if s in group_title), None)
    term = "الترم الأول" if "ترم أول" in group_title else ("الترم الثاني" if "ترم ثاني" in group_title else "غير محدد")
    return grade or "غير معروف", term

# ✅ إضافة سؤال من رد على رسالة
def add_question_from_message(msg: Message) -> bool:
    if msg.reply_to_message and msg.reply_to_message.text:
        q_text = msg.reply_to_message.text
        grade, term = extract_class_term(msg.chat.title or "")
        key = f"{msg.chat.id}_{grade}_{term}"
        questions_data.setdefault(key, []).append(q_text)
        save_questions()
        return True
    return False

# ✅ إرسال سؤال عشوائي
async def send_random_question(chat_id, app=None):
    from pyrogram import Client  # Ensure app is available
    if app is None:
        return

    chat = await app.get_chat(chat_id)
    grade, term = extract_class_term(chat.title or "")
    key = f"{chat_id}_{grade}_{term}"
    if key in questions_data and questions_data[key]:
        question = random.choice(questions_data[key])
        await app.send_message(chat_id, f"❓ {question}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("إظهار الإجابة ✅", callback_data="show_answer")]
        ]))
    else:
        await app.send_message(chat_id, "❌ لا يوجد أسئلة محفوظة لهذا الصف أو الترم بعد.")

# ✅ اختبار quizme (اختياري)
async def start_quiz_session(client, message):
    from_user = message.from_user.first_name
    chat_id = message.chat.id

    # إرسال 5 أسئلة عشوائية
    await message.reply(f"🧪 {from_user}، إليك اختبار صغير مكون من 5 أسئلة:")
    for i in range(5):
        await send_random_question(chat_id, app=client)
