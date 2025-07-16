from group_manager import approve_group, remove_group
from pyrogram.types import Message
import json

# ✅ تحميل OWNER_ID من ملف الإعدادات
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

OWNER_ID = config.get("owner_id")

def is_owner(user_id):
    return user_id == OWNER_ID

# ✅ أمر لتفعيل الجروب
async def handle_approve_command(message: Message):
    if not is_owner(message.from_user.id):
        await message.reply("🚫 هذا الأمر مخصص للمدير فقط.")
        return

    title = message.chat.title or "جروب بدون اسم"
    approve_group(message.chat.id, title, permanent=False)
    await message.reply("✅ تم تفعيل هذا الجروب لمدة 29 يومًا.")

# ✅ أمر لإلغاء التفعيل
async def handle_remove_command(message: Message):
    if not is_owner(message.from_user.id):
        await message.reply("🚫 هذا الأمر مخصص للمدير فقط.")
        return

    remove_group(message.chat.id)
    await message.reply("❌ تم إلغاء تفعيل هذا الجروب.")
