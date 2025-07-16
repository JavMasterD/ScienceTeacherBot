import json
import os
from datetime import datetime, timedelta

CHAMPION_FILE = "weekly_scores.json"

# ✅ تحميل البيانات أو تهيئتها
if not os.path.exists(CHAMPION_FILE):
    with open(CHAMPION_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

with open(CHAMPION_FILE, "r", encoding="utf-8") as f:
    weekly_scores = json.load(f)

def save_scores():
    with open(CHAMPION_FILE, "w", encoding="utf-8") as f:
        json.dump(weekly_scores, f, ensure_ascii=False, indent=2)

# ✅ تسجيل إجابة صحيحة
def add_correct_answer(user_id, user_name, group_id):
    group_key = str(group_id)
    if group_key not in weekly_scores:
        weekly_scores[group_key] = {}

    user_key = str(user_id)
    user_data = weekly_scores[group_key].get(user_key, {"name": user_name, "score": 0})
    user_data["score"] += 1
    user_data["name"] = user_name  # تحديث الاسم
    weekly_scores[group_key][user_key] = user_data
    save_scores()

# ✅ عرض بطل الأسبوع
async def handle_weekly_champion(group_id):
    group_key = str(group_id)
    if group_key not in weekly_scores or not weekly_scores[group_key]:
        return "📊 لا توجد مشاركات هذا الأسبوع."

    sorted_users = sorted(weekly_scores[group_key].items(), key=lambda x: x[1]["score"], reverse=True)
    top_user = sorted_users[0]
    name = top_user[1]["name"]
    score = top_user[1]["score"]

    return f"🏆 بطل الأسبوع هو: {name} بإجمالي {score} نقطة!"

# ✅ إعادة تعيين النقاط أسبوعيًا (للاستخدام الآلي)
def reset_weekly_scores():
    global weekly_scores
    weekly_scores = {}
    save_scores()
