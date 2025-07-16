from champion_manager import load_champion_data

async def handle_weekly_champion(app, chat_id):
    data = load_champion_data()
    if not data:
        await app.send_message(chat_id, "📭 لا يوجد مشاركات هذا الأسبوع.")
        return

    top_user = max(data.items(), key=lambda item: item[1]["points"])
    user_id, info = top_user
    name = info["name"]
    points = info["points"]
    await app.send_message(chat_id, f"🏆 بطل الأسبوع هو {name} برصيد {points} نقطة!")
