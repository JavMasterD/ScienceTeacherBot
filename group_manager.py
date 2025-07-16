import json
import os

APPROVED_GROUPS_FILE = "approved_groups.json"
QUESTIONS_FILE = "questions_group.json"

if not os.path.exists(APPROVED_GROUPS_FILE):
    with open(APPROVED_GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

if not os.path.exists(QUESTIONS_FILE):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

def is_group_approved(group_id):
    with open(APPROVED_GROUPS_FILE, "r", encoding="utf-8") as f:
        approved = json.load(f)
    return group_id in approved

def approve_group_id(group_id):
    with open(APPROVED_GROUPS_FILE, "r+", encoding="utf-8") as f:
        approved = json.load(f)
        if group_id not in approved:
            approved.append(group_id)
            f.seek(0)
            json.dump(approved, f, ensure_ascii=False, indent=2)
            f.truncate()

def save_question_to_group(group_id, question_text):
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    key = str(group_id)
    if key not in data:
        data[key] = []
    data[key].append(question_text)
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
