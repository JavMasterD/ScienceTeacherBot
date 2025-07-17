from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from quiz_generator import send_random_question
from group_manager import is_group_approved, save_question_to_group
from admin_tools import approve_group
from champion_manager import show_user_stats, reset_weekly_scores, add_point
from quotes_manager import get_random_quote
from review_game import pick_random_student
from weekly_quiz import handle_weekly_champion
import json

import asyncio
from datetime import datetime, timedelta, timezone

print("تم تشغيل الكود 😊")

with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
API_ID = config["api_id"]
API_HASH = config["api_hash"]
OWNER_ID = config["owner_id"]

app = Client(
    name="Science",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    workdir="."
)


@app.on_message(filters.all)
async def debug_all(client, message):
    print(f"[📩] Received message from chat {message.chat.id}: {message.text}")


@app.on_message(filters.command("ping") & filters.group)
async def ping_handler(client, message):
    await message.reply("✅ البوت يعمل الآن بكفاءة!")


# ✅ رسالة بدء خاصة
@app.on_message(filters.command("startMyBot") & filters.private)
async def start_private(client, message):
    await message.reply("👋 أهلاً بك في معلم العلوم الذكي! أضفني إلى جروبك وابدأ بـ /quizStart")


# ✅ اعتماد الجروب - للمشرف فقط
@app.on_message(filters.command("approveGroup") & filters.group)
async def approve_group_cmd(client, message):
    await approve_group(app, message)


# ✅ إضافة سؤال برد
@app.on_message(filters.command("addQues") & filters.group)
async def add_question_cmd(client, message):
    if not is_group_approved(message.chat.id):
        return await message.reply("❌ هذا الجروب غير معتمد. يجب الموافقة عليه أولاً.")
    if message.reply_to_message and message.reply_to_message.text:
        save_question_to_group(message.chat.id, message.reply_to_message.text)
        await message.reply("✅ تم حفظ السؤال.")
    else:
        await message.reply("❗️ من فضلك رد على رسالة تحتوي على السؤال.")


# ✅ إرسال سؤال عشوائي
@app.on_message(filters.command("quizStart") & filters.group)
async def quiz_cmd(client, message):
    if not is_group_approved(message.chat.id):
        return await message.reply("❌ هذا الجروب غير معتمد.")
    await send_random_question(app, message.chat.id)


# ✅ اقتباس عشوائي
@app.on_message(filters.command("quote") & filters.group)
async def quote_cmd(client, message):
    await message.reply(f"🧠 اقتباس اليوم:\n\n{get_random_quote()}")


# ✅ مراجعة طالب عشوائي
@app.on_message(filters.command("reviewNow") & filters.group)
async def review_now(client, message):
    student = await pick_random_student(app, message.chat.id)
    if student:
        await message.reply(f"🎯 الدور على: {student}")
    else:
        await message.reply("❗️ لا يوجد طلاب متاحين حاليًا.")


# ✅ عرض نقاط الطالب
@app.on_message(filters.command("myPoints") & filters.group)
async def points_cmd(client, message):
    await show_user_stats(message)


# ✅ عرض بطل الأسبوع
@app.on_message(filters.command("weeklyChampion") & filters.group)
async def champion_cmd(client, message):
    await handle_weekly_champion(app, message.chat.id)


# ✅ مهمة إعادة تعيين أسبوعية
async def weekly_reset_task():
    print("تم تشغيل المهمة الاسبوعية")
    while True:
        now = datetime.now(timezone.utc)

        # تحديد الجمعة القادمة
        next_friday = now + timedelta((4 - now.weekday()) % 7)
        reset_time = datetime.combine(next_friday.date(), datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=5)

        # لو كنا بعد الجمعة 5 صباحًا، نحسب الجمعة التالية
        if now >= reset_time:
            next_friday += timedelta(days=7)
            reset_time = datetime.combine(next_friday.date(), datetime.min.time(), tzinfo=timezone.utc) + timedelta(
                hours=5)

        wait_time = (reset_time - now).total_seconds()
        print(f"سوف يتم إعادة التعيين الأسبوعي بعد {wait_time / 3600:.2f} ساعة")

        await asyncio.sleep(wait_time)
        reset_weekly_scores()


# ✅ تشغيل البوت
async def main():
    await app.start()
    print("✅ البوت يعمل...")
    asyncio.create_task(weekly_reset_task())  # ← بدون await
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
