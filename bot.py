from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone
import asyncio
import json
import os
import random

# ⚙️ استيراد الوظائف المساعدة من ملفات المشروع
from quiz_generator import send_random_question
from quotes_manager import get_random_quote
from review_game import pick_random_student
from weekly_quiz import handle_weekly_champion
from champion_manager import show_user_stats, reset_weekly_scores
from admin_tools import approve_group, remove_group
from group_manager import is_group_approved, save_question_to_group
from lesson_saver import save_lesson_question

# ✅ تحميل الإعدادات
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
API_ID = config["api_id"]
API_HASH = config["api_hash"]
OWNER_ID = config["owner_id"]

# ✅ تهيئة البوت
app = Client("ScienceTeacherBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ /startMyBot (خاص)
@app.on_message(filters.command("startMyBot") & filters.private)
async def start_my_bot(client, message):
    await message.reply("👋 مرحبًا بك في معلم العلوم الذكي!\nأضفني إلى جروب وابدأ بـ /quizStart")

# ✅ /quizStart (إرسال سؤال)
@app.on_message(filters.command("quizStart") & filters.chat_type.groups)
async def quiz_start(client, message):
    if is_group_approved(message.chat.id):
        await send_random_question(app, message.chat.id)
    else:
        await message.reply("🚫 هذا الجروب غير معتمد. أرسل /approveMe ليتم مراجعته.")

# ✅ /addQues (حفظ سؤال من رد)
@app.on_message(filters.command("addQues") & filters.chat_type.groups)
async def add_question(client, message):
    if is_group_approved(message.chat.id):
        if message.reply_to_message:
            save_question_to_group(message.chat.id, message.reply_to_message.text)
            await message.reply("✅ تم حفظ السؤال.")
        else:
            await message.reply("❗️ من فضلك رد على السؤال المراد حفظه.")
    else:
        await message.reply("🚫 هذا الجروب غير معتمد.")

# ✅ /saveLesson <عنوان>
@app.on_message(filters.command("saveLesson") & filters.chat_type.groups)
async def save_lesson_cmd(client, message):
    if message.reply_to_message and len(message.command) > 1:
        lesson_title = " ".join(message.command[1:])
        saved = save_lesson_question(message.chat.id, lesson_title, message.reply_to_message.text)
        if saved:
            await message.reply(f"✅ تم حفظ السؤال تحت عنوان الدرس: {lesson_title}")
    else:
        await message.reply("❗️ استخدم الأمر هكذا:\n`/saveLesson عنوان الدرس` بالرد على السؤال", quote=True)

# ✅ /reviewStudent (طالب عشوائي)
@app.on_message(filters.command("reviewStudent") & filters.chat_type.groups)
async def review_student_cmd(client, message):
    student = await pick_random_student(app, message.chat.id)
    if student:
        await message.reply(f"🎯 الدور على: {student}!\nاستعد للإجابة 🧠")
    else:
        await message.reply("❗️ لم أستطع اختيار طالب الآن.")

# ✅ /quoteNow (اقتباس)
@app.on_message(filters.command("quoteNow") & filters.chat_type.groups)
async def quote_cmd(client, message):
    quote = get_random_quote()
    await message.reply(f"🌟 اقتباس اليوم:\n\n_{quote}_")

# ✅ /weeklyChampion (بطل الأسبوع)
@app.on_message(filters.command("weeklyChampion") & filters.chat_type.groups)
async def champion_cmd(client, message):
    await handle_weekly_champion(app, message.chat.id)

# ✅ /myPoints (نقاطي)
@app.on_message(filters.command("myPoints") & filters.chat_type.groups)
async def my_points_cmd(client, message):
    await show_user_stats(message)

# ✅ /approveMe (طلب موافقة)
@app.on_message(filters.command("approveMe") & filters.chat_type.groups)
async def approve_me_cmd(client, message):
    await approve_group(app, message)

# ✅ /removeMe (طلب حذف الجروب)
@app.on_message(filters.command("removeMe") & filters.chat_type.groups)
async def remove_me_cmd(client, message):
    await remove_group(app, message)

# ✅ الرد على زر "إظهار الإجابة"
@app.on_callback_query()
async def handle_callback(client, callback_query):
    await callback_query.answer("📌 راجع إجابتك مع المعلم!", show_alert=True)
    await callback_query.message.reply("✅ أحسنت المحاولة! ✨")

# ✅ مهمة أسبوعية لتصفير النقاط كل جمعة
async def weekly_reset_task():
    while True:
        now_utc = datetime.now(timezone.utc)
        next_friday = (7 - now_utc.weekday()) % 7
        wait_seconds = next_friday * 24 * 3600
        await asyncio.sleep(wait_seconds)
        reset_weekly_scores()
        print("✅ تم تصفير النقاط الأسبوعية")

# ✅ تشغيل البوت
async def main():
    await app.start()
    print("✅ البوت يعمل...")
    asyncio.create_task(weekly_reset_task())
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
