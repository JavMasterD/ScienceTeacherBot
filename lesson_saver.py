import json
import os

LESSON_FILE = "lesson_questions.json"

# ✅ تحميل الأسئلة المرتبطة بالدروس
if not os.path.exists(LESSON_FILE):
    with open(LESSON_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

with open(LESSON_FILE, "r", encoding="utf-8") as f:
    lesson_data = json.load(f)

def save_data():
    with open(LESSON_FILE, "w", encoding="utf-8") as f:
        json.dump(lesson_data, f, ensure_ascii=False, indent=2)

# ✅ حفظ سؤال تحت عنوان درس معين
def save_lesson_question(group_id: int, lesson_title: str, question: str):
    group_key = str(group_id)
    lesson_title = lesson_title.strip()

    if not lesson_title or not question:
        return False

    if group_key not in lesson_data:
        lesson_data[group_key] = {}

    lesson_data[group_key].setdefault(lesson_title, []).append(question)
    save_data()
    return True
