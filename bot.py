from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime, timedelta
import json, random, os, asyncio

from group_manager import GroupManager
from champion_manager import add_correct_answer, get_week_champion, reset_weekly_data
from quiz_generator import QuizGenerator
from quotes_manager import QuotesManager
from review_game import ReviewGame
from weekly_quiz import WeeklyQuiz

# تحميل الإعدادات
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
API_ID = config["api_id"]
API_HASH = config["api_hash"]
OWNER_ID = config["owner_id"]

app = Client("ScienceTeacherBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# تحميل الأسئلة
QUESTIONS_FILE = "questions_group.json"
if not os.path.exists(QUESTIONS_FILE):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)
with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    questions_data = json.load(f)

# أدوات الإدارة
group_manager = GroupManager()
quiz_generator = QuizGenerator(questions_data)
quotes_manager = QuotesManager()
review_game = ReviewGame()
weekly_quiz = WeeklyQuiz(questions_data)

def save_questions():
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)

def extract_class_term(group_title):
    grade = next((s for s in ["الرابع", "الخامس", "السادس", "الأول", "الثاني", "الثالث"] if s in group_title), None)
    term = "الترم الأول" if "ترم أول" in group_title else ("الترم الثاني" if "ترم ثاني" in group_title else "غير محدد")
    return grade or "غير معروف", term

def add_question_from_message(msg: Message):
    if msg.reply_to_message and msg.reply_to_message.text:
        q_text = msg.reply_to_message.text
        grade, term = extract_class_term(msg.chat.title or "")
        key = f"{msg.chat.id}_{grade}_{term}"
        questions_data.setdefault(key, []).append(q_text)
        save_questions()
        return True
    return False

# /start خاص
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply("👋 أهلاً بك في معلم العلوم الذكي! أضفني إلى جروب وابدأ بـ /quiz")

# /add في الجروبات
@app.on_message(filters.command("add") & filters.group)
async def add_cmd(client, message):
    if not group_manager.is_group_approved(message.chat.id):
        return await message.reply("❌ هذا الجروب غير مصرح به. اطلب من المعلم الموافقة.")
    if add_question_from_message(message):
        await message.reply("✅ تم حفظ السؤال للجروب.")
    else:
        await message.reply("❗️ من فضلك رد على رسالة تحتوي على السؤال.")

# /quiz إرسال سؤال عشوائي
@app.on_message(filters.command("quiz") & filters.group)
async def quiz_cmd(client, message):
    if not group_manager.is_group_approved(message.chat.id):
        return await message.reply("❌ هذا الجروب غير مصرح به.")
    grade, term = extract_class_term(message.chat.title or "")
    question = quiz_generator.get_random_question(message.chat.id, grade, term)
    if not question:
        return await message.reply("❌ لا توجد أسئلة كافية.")
    await message.reply(f"❓ {question['question']}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إظهار الإجابة ✅", callback_data="show_answer")]]))

# إظهار عبارة تحفيزية
@app.on_callback_query()
async def callback_handler(client, callback_query):
    await callback_query.answer("💡 أحسنت! تابع التقدم", show_alert=True)
    await callback_query.message.reply(quotes_manager.get_random_quote())

# /review اختيار طالب للمراجعة
@app.on_message(filters.command("review") & filters.group)
async def review_cmd(client, message):
    if not group_manager.is_group_approved(message.chat.id):
        return await message.reply("❌ هذا الجروب غير مصرح به.")
    members = [m.user.first_name for m in await app.get_chat_members(message.chat.id, limit=50) if m.user and not m.user.is_bot]
    if not members:
        return await message.reply("❌ لا يوجد أعضاء.")
    chosen = review_game.choose_random_player(members, message.chat.id)
    await message.reply(f"🎯 الدور على: {chosen}! استعد للسؤال!")

# /champion عرض بطل الأسبوع
@app.on_message(filters.command("champion") & filters.group)
async def champion_cmd(client, message):
    user_id, score = get_week_champion(message.chat.id)
    if user_id == None:
        return await message.reply("❌ لم يتم تحديد بطل الأسبوع بعد.")
    user = await app.get_users(user_id)
    await message.reply(f"🏆 بطل الأسبوع هو: {user.first_name} بعدد إجابات صحيحة: {score}")

# /approve للموافقة على الجروبات
@app.on_message(filters.command("approve") & filters.user(OWNER_ID))
async def approve_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("❗️ أرسل معرف الجروب للموافقة عليه.\nمثال: /approve -1001234567890")
    chat_id = int(message.command[1])
    group_manager.approve_group(chat_id)
    await message.reply(f"✅ تم السماح للجروب: {chat_id}")
# ✅ مهمة أسبوعية لإعادة تعيين البطل كل أسبوع
async def weekly_reset_task():
    while True:
        now = datetime.now()
        if now.weekday() == 6 and now.hour == 0 and now.minute == 0:
            reset_weekly_data()
        await asyncio.sleep(60)

# ✅ الدالة الرئيسية لتشغيل البوت
async def main():
    await app.start()
    print("✅ البوت يعمل...")
    asyncio.create_task(weekly_reset_task())

    # ⬇️ هذا هو المكان الصحيح لوضع while True:
    while True:
        await asyncio.sleep(60)

# ✅ تشغيل البوت إذا كان هذا الملف هو الرئيسي
if __name__ == "__main__":
    asyncio.run(main())