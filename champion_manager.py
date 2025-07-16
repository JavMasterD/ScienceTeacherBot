import json
import os

CHAMPION_FILE = "weekly_scores.json"

# ✅ تحميل نقاط الأسبوع
if not os.path.exists(CHAMPION_FILE):
    with open(CHAMPION_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

with open(CHAMPION_FILE, "r", encoding="utf-8") as f:
    weekly_scores = json.load(f)

# ✅ عرض عدد نقاط مستخدم معين
def show_user_stats(user_id, group_id):
    group_key = str(group_id)
    user_key = str(user_id)

    if group_key not in weekly_scores:
        return "📊 لم يتم تسجيل أي نقاط في هذا الجروب حتى الآن."

    user_data = weekly_scores[group_key].get(user_key)
    if not user_data:
        return "📌 لم تسجل أي إجابات صحيحة بعد."

    return f"👤 {user_data['name']} لديك {user_data['score']} نقطة هذا الأسبوع!"
