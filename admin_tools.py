# admin_tools.py

import json, os
from datetime import datetime, timedelta
from pyrogram.enums import ChatMemberStatus

APPROVED_GROUPS_FILE = "approved_groups.json"

# ✅ الكلمات التي تسمح بالعمل تلقائيًا
ALLOWED_KEYWORDS = ["الرابع", "الخامس", "السادس", "الأول", "الثاني", "الثالث"]

# ✅ تحميل الجروبات الموافق عليها يدويًا
def load_approved_groups():
    if os.path.exists(APPROVED_GROUPS_FILE):
        with open(APPROVED_GROUPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ✅ حفظ الجروبات الموافق عليها
def save_approved_groups(data):
    with open(APPROVED_GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ التحقق من الجروبات المسموحة
def is_allowed_group_by_name(group_title):
    return any(keyword in (group_title or "") for keyword in ALLOWED_KEYWORDS)

# ✅ التحقق إن كان الجروب موافق عليه مؤقتًا
def is_approved_group(chat_id):
    approved = load_approved_groups()
    if str(chat_id) in approved:
        expiry = datetime.fromisoformat(approved[str(chat_id)])
        return datetime.now() < expiry
    return False

# ✅ إضافة موافقة على جروب لمدة 29 يومًا
def approve_group(chat_id):
    approved = load_approved_groups()
    approved[str(chat_id)] = (datetime.now() + timedelta(days=29)).isoformat()
    save_approved_groups(approved)

# ✅ التحقق إن كان المستخدم مشرفًا
async def is_admin(client, message):
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except:
        return False
