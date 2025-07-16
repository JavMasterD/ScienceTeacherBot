import json
import os
from datetime import datetime, timedelta

GROUPS_FILE = "approved_groups.json"

# ✅ تحميل ملف الجروبات أو إنشاؤه إن لم يكن موجودًا
if not os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

with open(GROUPS_FILE, "r", encoding="utf-8") as f:
    approved_groups = json.load(f)

def save_groups():
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(approved_groups, f, ensure_ascii=False, indent=2)

# ✅ التحقق من أن الجروب مفعل
def is_group_approved(chat_id: int) -> bool:
    chat_id = str(chat_id)
    group = approved_groups.get(chat_id)
    if not group or not group.get("approved"):
        return False

    if group.get("permanent"):
        return True

    until = group.get("until")
    if until:
        try:
            expiry = datetime.fromisoformat(until)
            if datetime.now() < expiry:
                return True
        except:
            return False
    return False

# ✅ تفعيل جروب جديد لمدة 29 يومًا
def approve_group(chat_id: int, title: str, permanent=False):
    chat_id = str(chat_id)
    approved_groups[chat_id] = {
        "name": title,
        "approved": True,
        "permanent": permanent
    }

    if not permanent:
        expiry = datetime.now() + timedelta(days=29)
        approved_groups[chat_id]["until"] = expiry.isoformat()

    save_groups()

# ✅ حذف جروب من القائمة
def remove_group(chat_id: int):
    chat_id = str(chat_id)
    if chat_id in approved_groups:
        del approved_groups[chat_id]
        save_groups()

# ✅ عرض جميع الجروبات (للتطوير لاحقًا)
def list_approved_groups():
    return approved_groups
