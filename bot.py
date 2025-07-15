# ✅ ScienceTeacherBot - إصدار كامل
# يعمل كمساعد علوم ذكي داخل مجموعات Telegram
# يدعم الأسئلة التفاعلية، مراجعات، مسابقات، حفظ الأسئلة، تحكم بالجروبات

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime, timedelta
import json, random, os, asyncio

# ✅ تحميل الإعدادات من config.json
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
API_ID = config["api_id"]
API_HASH = config["api_hash"]
OWNER_ID = config["owner_id"]

app = Client("ScienceTeacherBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# ✅ تحميل أو تهيئة ملف الأسئلة
QUESTIONS_FILE = "questions_group.json"
if not os.path.exists(QUESTIONS_FILE):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    questions_data = json.load(f)

# ✅ قائمة تحفيزية
motivation_msgs = [
    "أحسنت! استمر في التفوق!",
    "👏 أنت نجم العلوم اليوم!",
    "ممتاز! keep going",
    "💡 العلم نور... وأنت منوره!"
]

# ✅ المستخدمين المشاركين في spinner
spinner_used = {}

def save_questions():
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)

# ✅ استخراج الصف والترم من اسم الجروب
def extract_class_term(group_title):
    grade = next((s for s in ["الرابع", "الخامس", "السادس", "الأول", "الثاني", "الثالث"] if s in group_title), None)
    term = "الترم الأول" if "ترم أول" in group_title else ("الترم الثاني" if "ترم ثاني" in group_title else "غير محدد")
    return grade or "غير معروف", term

# ✅ حفظ سؤال من الرسالة
def add_question_from_message(msg: Message):
    if msg.reply_to_message and msg.reply_to_message.text:
        q_text = msg.reply_to_message.text
        grade, term = extract_class_term(msg.chat.title or "")
        key = f"{msg.chat.id}_{grade}_{term}"
        questions_data.setdefault(key, []).append(q_text)
        save_questions()
        return True
    return False

# ✅ إرسال سؤال عشوائي
async def send_random_question(chat_id):
    grade, term = extract_class_term((await app.get_chat(chat_id)).title or "")
    key = f"{chat_id}_{grade}_{term}"
    if key in questions_data and questions_data[key]:
        question = random.choice(questions_data[key])
        await app.send_message(chat_id, f"❓ {question}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("إظهار الإجابة ✅", callback_data="show_answer")]
        ]))

# ✅ /start
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply("👋 أهلاً بك في معلم العلوم الذكي! أضفني إلى جروب وابدأ بـ /quiz")

# ✅ /add - حفظ سؤال برد على رسالة
@app.on_message(filters.command("add") & filters.group)
async def add_cmd(client, message):
    if add_question_from_message(message):
        await message.reply("✅ تم حفظ السؤال للجروب.")
    else:
        await message.reply("❗️ من فضلك رد على رسالة تحتوي على السؤال.")

# ✅ /quiz - إرسال سؤال عشوائي
@app.on_message(filters.command("quiz") & filters.group)
async def quiz_cmd(client, message):
    await send_random_question(message.chat.id)

# ✅ /review - spinner لمراجعة اسم طالب
@app.on_message(filters.command("review") & filters.group)
async def review_cmd(client, message):
    members = [m.user.first_name for m in await app.get_chat_members(message.chat.id, limit=50) if m.user and not m.user.is_bot]
    if members:
        last_used = spinner_used.get(message.chat.id)
        name = random.choice([n for n in members if n != last_used] or members)
        spinner_used[message.chat.id] = name
        await message.reply(f"🎯 الدور على: {name}! استعد للسؤال! 🧠")

# ✅ الرد على زر إظهار الإجابة
@app.on_callback_query()
async def callback_handler(client, callback_query):
    await callback_query.answer("الإجابة يمكن أن تكون في الرسالة التالية!", show_alert=True)
    await callback_query.message.reply(random.choice(motivation_msgs))

# ✅ إرسال 20 سؤال يوميًا عند بدء التشغيل (مثال فقط - قابل للتعديل بزمن محدد)
async def daily_questions():
    while True:
        for key in questions_data:
            chat_id = int(key.split("_")[0])
            for _ in range(20):
                await send_random_question(chat_id)
                await asyncio.sleep(2)  # تأخير بين الأسئلة
        await asyncio.sleep(24 * 60 * 60)  # كل 24 ساعة

# ✅ بدء تشغيل البوت
async def main():
    await app.start()
    print("✅ البوت يعمل...")
    asyncio.create_task(daily_questions())
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
