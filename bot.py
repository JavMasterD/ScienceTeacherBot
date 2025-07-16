from datetime import datetime, timezone
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import json, os, random, asyncio

from quiz_generator import send_random_question
from review_game import pick_random_student
from quotes_manager import get_random_quote
from weekly_quiz import handle_weekly_champion, reset_weekly_scores
from champion_manager import show_user_stats
from admin_tools import handle_approve_command, handle_remove_command
from group_manager import is_group_approved
from lesson_saver import save_lesson_question

# ✅ تحميل الإعدادات من config.json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
API_ID = config["api_id"]
API_HASH = config["api_hash"]

app = Client("ScienceTeacherBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# ✅ رسالة ترحيب خاصة
@app.on_message(filters.command("startMyBot") & filters.private)
async def start_private(client, message):
    await message.reply("👋 مرحبًا بك في معلم العلوم الذكي!\nأضفني إلى جروب وابدأ بالأوامر: /quizStart أو /addQues")

# ✅ إرسال سؤال عشوائي
@app.on_message(filters.command("quizStart") & filters.group)
async def quiz_command(client, message):
    if not is_group_approved(message.chat.id):
        return
    await send_random_question(app, message.chat.id)

# ✅ حفظ سؤال من رد على رسالة
@app.on_message(filters.command("addQues") & filters.group)
async def add_question_command(client, message):
    if not is_group_approved(message.chat.id):
        return
    if message.reply_to_message and message.reply_to_message.text:
        question = message.reply_to_message.text
        group_title = message.chat.title or "بدون اسم"
        key = f"{message.chat.id}_{group_title}"
        with open("questions_group.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault(key, []).append(question)
        with open("questions_group.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        await message.reply("✅ تم حفظ السؤال.")
    else:
        await message.reply("❗️ من فضلك رد على رسالة تحتوي على السؤال.")

# ✅ حفظ سؤال مرتبط بعنوان درس
@app.on_message(filters.command("saveLesson") & filters.group)
async def save_lesson_cmd(client, message):
    if not is_group_approved(message.chat.id):
        return
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.reply("❗️ من فضلك رد على السؤال الذي تريد حفظه.")
        return

    if len(message.command) < 2:
        await message.reply("❗️ استخدم الأمر بهذا الشكل:\n`/saveLesson عنوان الدرس`", parse_mode="Markdown")
        return

    lesson_title = " ".join(message.command[1:])
    question_text = message.reply_to_message.text
    saved = save_lesson_question(message.chat.id, lesson_title, question_text)

    if saved:
        await message.reply(f"✅ تم حفظ السؤال ضمن الدرس: {lesson_title}")
    else:
        await message.reply("⚠️ حدث خطأ أثناء الحفظ.")

# ✅ مراجعة عشوائية لطالب
@app.on_message(filters.command("reviewStudent") & filters.group)
async def review_student_cmd(client, message):
    if not is_group_approved(message.chat.id):
        return
    name = await pick_random_student(app, message.chat.id)
    await message.reply(f"🎯 الدور على: {name}")

# ✅ إرسال اقتباس تحفيزي
@app.on_message(filters.command("quoteNow"))
async def quote_cmd(client, message):
    await message.reply(get_random_quote())

# ✅ بطل الأسبوع
@app.on_message(filters.command("weeklyChampion") & filters.group)
async def champion_cmd(client, message):
    if not is_group_approved(message.chat.id):
        return
    result = await handle_weekly_champion(message.chat.id)
    await message.reply(result)

# ✅ نقاطي
@app.on_message(filters.command("myPoints") & filters.group)
async def mypoints_cmd(client, message):
    if not is_group_approved(message.chat.id):
        return
    response = show_user_stats(message.from_user.id, message.chat.id)
    await message.reply(response)

# ✅ أوامر الموافقة على الجروب
@app.on_message(filters.command("approveMe") & filters.group)
async def approve_me_cmd(client, message):
    await handle_approve_command(message)

@app.on_message(filters.command("removeMe") & filters.group)
async def remove_me_cmd(client, message):
    await handle_remove_command(message)

# ✅ إعادة تعيين نقاط الأسبوع تلقائيًا كل جمعة
async def weekly_reset_task():
    while True:
        now_utc = datetime.now(timezone.utc)  # ✅ هنا نستخدم timezone
        next_friday = (7 - now_utc.weekday()) % 7
        wait_seconds = next_friday * 24 * 3600
        await asyncio.sleep(wait_seconds)
        reset_weekly_scores()
        print("✅ تم تصفير النقاط الأسبوعية")

# ✅ بدء تشغيل البوت
async def main():
    await app.start()
    print("✅ البوت يعمل...")
    asyncio.create_task(weekly_reset_task())
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
