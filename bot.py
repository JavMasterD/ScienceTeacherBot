import asyncio
import json
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from group_manager import GroupManager
from champion_manager import add_correct_answer, get_week_champion, reset_weekly_data
from quiz_generator import QuizGenerator
from quotes_manager import QuotesManager
from review_game import ReviewGame
from weekly_quiz import WeeklyQuiz

# تحميل الإعدادات
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
API_ID = config["api_id"]
API_HASH = config["api_hash"]
OWNER_ID = config["owner_id"]

app = Client("ScienceTeacherBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# تحميل بيانات الأسئلة
QUESTIONS_FILE = "questions_group.json"
try:
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions_data = json.load(f)
except FileNotFoundError:
    questions_data = {}

quiz_generator = QuizGenerator(questions_data)
quotes_manager = QuotesManager()
review_game = ReviewGame()
group_manager = GroupManager()
weekly_quiz = WeeklyQuiz(questions_data)

# دالة مساعدة لاستخراج الصف والترم من عنوان الجروب
def extract_class_term(group_title):
    grades = ["الرابع", "الخامس", "السادس", "الأول", "الثاني", "الثالث"]
    grade = next((g for g in grades if g in group_title), "غير معروف")
    if "ترم أول" in group_title:
        term = "الترم الأول"
    elif "ترم ثاني" in group_title:
        term = "الترم الثاني"
    else:
        term = "غير محدد"
    return grade, term

# دالة تحقق من أن الجروب مفعل وموافق عليه
def check_group_allowed(chat_id):
    # السماح تلقائيًا للجروبات المحددة حسب الاسم
    # إذا لم يكن، نتحقق من الموافقة اليدوية
    # نحتاج جلب عنوان الجروب هنا لكن هذا sync فسنعتمد على group_manager فقط
    return group_manager.is_group_approved(chat_id)

# أمر /start في الخاص
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply("👋 أهلاً بك في معلم العلوم الذكي! أضفني إلى جروب وابدأ بـ /quiz")

# أمر /getid في الجروب لعرض معرف الجروب
@app.on_message(filters.command("getid") & filters.group)
async def getid_cmd(client, message):
    await message.reply(f"معرف هذا الجروب هو:\n`{message.chat.id}`", parse_mode="markdown")

# أمر /approve للموافقة على الجروب (للمشرف فقط)
@app.on_message(filters.command("approve") & filters.group)
async def approve_cmd(client, message):
    # تحقق صلاحية المشرف (ممكن تضيف دالة تحقق أكثر تعقيدًا)
    chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.status not in ["administrator", "creator"]:
        await message.reply("❌ هذا الأمر خاص بالمشرفين فقط.")
        return

    group_manager.approve_group(message.chat.id)
    await message.reply("✅ تم الموافقة على الجروب لمدة 29 يومًا.")

# أمر /add لحفظ سؤال (رد على رسالة)
@app.on_message(filters.command("add") & filters.group)
async def add_cmd(client, message):
    if not check_group_allowed(message.chat.id):
        await message.reply("🚫 هذا الجروب غير مفعل، يرجى انتظار الموافقة.")
        return

    if message.reply_to_message and message.reply_to_message.text:
        grade, term = extract_class_term(message.chat.title or "")
        key = f"{message.chat.id}_{grade}_{term}"
        questions_data.setdefault(key, []).append(message.reply_to_message.text)
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        await message.reply("✅ تم حفظ السؤال للجروب.")
    else:
        await message.reply("❗️ من فضلك رد على رسالة تحتوي على السؤال.")

# أمر /quiz لإرسال سؤال عشوائي
@app.on_message(filters.command("quiz") & filters.group)
async def quiz_cmd(client, message):
    if not check_group_allowed(message.chat.id):
        await message.reply("🚫 هذا الجروب غير مفعل، يرجى انتظار الموافقة.")
        return

    grade, term = extract_class_term(message.chat.title or "")
    question_entry = quiz_generator.get_random_question(message.chat.id, grade, term)

    if not question_entry:
        await message.reply("لا توجد أسئلة متاحة لهذه الفئة.")
        return

    text = f"❓ {question_entry['question']}\n"
    for idx, option in enumerate(question_entry.get("options", []), 1):
        text += f"{idx}. {option}\n"

    await message.reply(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("إظهار الإجابة ✅", callback_data=f"show_answer_{question_entry.get('answer', '')}")]
    ]))

# الرد على زر "إظهار الإجابة"
@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data.startswith("show_answer_"):
        answer = data[len("show_answer_"):]
        await callback_query.answer("الإجابة:", show_alert=True)
        await callback_query.message.reply(f"الإجابة الصحيحة هي:\n{answer}")
        quote = quotes_manager.get_random_quote()
        await callback_query.message.reply(quote)

# أمر /review لاختيار عضو عشوائي للدور
@app.on_message(filters.command("review") & filters.group)
async def review_cmd(client, message):
    if not check_group_allowed(message.chat.id):
        await message.reply("🚫 هذا الجروب غير مفعل، يرجى انتظار الموافقة.")
        return

    members = [m.user.first_name for m in await client.get_chat_members(message.chat.id, limit=50)
               if m.user and not m.user.is_bot]
    if not members:
        await message.reply("لا يوجد أعضاء كافيين للمراجعة.")
        return

    chosen = review_game.choose_random_player(members, message.chat.id)
    await message.reply(f"🎯 الدور على: {chosen}! استعد للسؤال! 🧠")

# أمر /champion لإظهار بطل الأسبوع
@app.on_message(filters.command("champion") & filters.group)
async def champion_cmd(client, message):
    if not check_group_allowed(message.chat.id):
        await message.reply("🚫 هذا الجروب غير مفعل، يرجى انتظار الموافقة.")
        return

    user_id, score = get_week_champion(message.chat.id)
    if user_id:
        user = await client.get_users(user_id)
        await message.reply(f"🏆 بطل الأسبوع هو: {user.first_name} 🎉\nعدد الإجابات الصحيحة: {score}")
    else:
        await message.reply("لا توجد بيانات كافية لعرض بطل الأسبوع.")

# أمر /startweeklyquiz لبدء المسابقة الأسبوعية
@app.on_message(filters.command("startweeklyquiz") & filters.group)
async def start_weekly_quiz(client, message):
    if not check_group_allowed(message.chat.id):
        await message.reply("🚫 هذا الجروب غير مفعل، يرجى انتظار الموافقة.")
        return

    grade, term = extract_class_term(message.chat.title or "")
    quiz_questions = weekly_quiz.generate_quiz(message.chat.id, grade, term, num_questions=10)
    if not quiz_questions:
        await message.reply("لا توجد أسئلة كافية للمسابقة الأسبوعية.")
        return

    await message.reply("🔔 تبدأ المسابقة الأسبوعية! أجب على الأسئلة التالية:")

    for q in quiz_questions:
        text = f"❓ {q['question']}\n"
        for idx, option in enumerate(q.get("options", []), 1):
            text += f"{idx}. {option}\n"
        await message.reply(text)
        await asyncio.sleep(5)

    await message.reply("✅ انتهت المسابقة! أرسل إجاباتك الآن.")

# أمر /weeklywinner لإعلان الفائز
@app.on_message(filters.command("weeklywinner") & filters.group)
async def announce_winner(client, message):
    if not check_group_allowed(message.chat.id):
        await message.reply("🚫 هذا الجروب غير مفعل، يرجى انتظار الموافقة.")
        return

    user_id, score = weekly_quiz.get_winner(message.chat.id)
    if user_id:
        user = await client.get_users(user_id)
        await message.reply(f"🏆 بطل المسابقة الأسبوعية هو: {user.first_name} 🎉\nالنقاط: {score}")
    else:
        await message.reply("لا توجد نتائج للمسابقة الأسبوعية حتى الآن.")

# تسجيل إجابة صحيحة (يجب تعديل لتلائم طريقة البوت للتحقق من الإجابة)
@app.on_message(filters.text & filters.group)
async def track_correct_answers(client, message):
    # هنا مثال بسيط: إذا كانت الرسالة تحتوي على "صح" أو "صحيح" نعتبرها إجابة صحيحة
    text = message.text.lower()
    if "صح" in text or "صحيح" in text:
        add_correct_answer(message.chat.id, message.from_user.id)

# مهمة دورية لإعادة ضبط بطل الأسبوع كل 7 أيام
async def weekly_reset_task():
    while True:
        now = datetime.now()
        # إعادة الضبط كل يوم أحد منتصف الليل مثلاً (يمكن تعديل الوقت)
        if now.weekday() == 6 and now.hour == 0 and now.minute == 0:
            reset_weekly_data()
        await asyncio.sleep(60)

# بدء تشغيل البوت
async def main():
    await app.start()
    print("✅ البوت يعمل...")

    # مهمة إعادة الضبط الأسبوعية في الخلفية
    asyncio.create_task(weekly_reset_task())

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
