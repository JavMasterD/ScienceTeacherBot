import json
import os
from datetime import datetime, timedelta

CHAMPIONS_FILE = "weekly_champions.json"

def load_data():
    if os.path.exists(CHAMPIONS_FILE):
        with open(CHAMPIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(CHAMPIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تسجيل إجابة صحيحة
def add_correct_answer(chat_id, user_id):
    data = load_data()
    chat_str = str(chat_id)
    user_str = str(user_id)

    if chat_str not in data:
        data[chat_str] = {}

    if user_str not in data[chat_str]:
        data[chat_str][user_str] = 0

    data[chat_str][user_str] += 1
    save_data(data)

# الحصول على بطل الأسبوع لجروب معين
def get_week_champion(chat_id):
    data = load_data()
    chat_str = str(chat_id)
    if chat_str not in data or not data[chat_str]:
        return None, 0
    sorted_users = sorted(data[chat_str].items(), key=lambda x: x[1], reverse=True)
    top_user, top_score = sorted_users[0]
    return int(top_user), top_score

# إعادة تعيين البيانات أسبوعيًا
def reset_weekly_data():
    save_data({})
