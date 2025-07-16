import random
from pyrogram import Client

# ✅ اختيار طالب عشوائي من أعضاء الجروب
async def pick_random_student(app: Client, chat_id: int) -> str:
    try:
        members = []
        async for m in app.get_chat_members(chat_id):
            if m.user and not m.user.is_bot:
                members.append(m.user.first_name)

        if not members:
            return "لا يوجد طلاب"

        return random.choice(members)
    except Exception as e:
        print(f"[review_game] Error: {e}")
        return "حدث خطأ أثناء اختيار الطالب"
