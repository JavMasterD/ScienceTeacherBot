import json
import os

CHAMPION_FILE = "champion_data.json"

# تأكد من وجود الملف
if not os.path.exists(CHAMPION_FILE):
    with open(CHAMPION_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_champion_data():
    with open(CHAMPION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_champion_data(data):
    with open(CHAMPION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_point(user_id, name):
    data = load_champion_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"name": name, "points": 0}
    data[str(user_id)]["points"] += 1
    save_champion_data(data)

def show_user_stats(message):
    data = load_champion_data()
    user_id = str(message.from_user.id)
    if user_id in data:
        name = data[user_id]["name"]
        points = data[user_id]["points"]
        return message.reply(f"🏆 {name} لديك {points} نقطة.")
    else:
        return message.reply("❗️ ليس لديك نقاط بعد.")

def reset_weekly_scores():
    data = load_champion_data()
    for user in data.values():
        user["points"] = 0
    save_champion_data(data)
