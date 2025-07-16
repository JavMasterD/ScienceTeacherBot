import json
from pyrogram import Client, filters

from group_manager import approve_group_id
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
API_ID = config["api_id"]
API_HASH = config["api_hash"]
OWNER_ID = config["owner_id"]

app = Client(
    name="anon",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    workdir="."
)
async def approve_group(app, message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ فقط مالك البوت يمكنه اعتماد الجروب.")
        return
    group_id = message.chat.id
    approve_group_id(group_id)
    await message.reply("✅ تم اعتماد هذا الجروب بنجاح.")
