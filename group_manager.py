
import json
import os
from datetime import datetime, timedelta

APPROVED_GROUPS_FILE = "approved_groups.json"

class GroupManager:
    def __init__(self):
        self.groups = self.load_groups()

    def load_groups(self):
        if os.path.exists(APPROVED_GROUPS_FILE):
            with open(APPROVED_GROUPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_groups(self):
        with open(APPROVED_GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.groups, f, ensure_ascii=False, indent=2)

    def approve_group(self, chat_id, days=29):
        expiration = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        self.groups[str(chat_id)] = expiration
        self.save_groups()

    def is_group_approved(self, chat_id):
        chat_id_str = str(chat_id)
        if chat_id_str not in self.groups:
            return False
        exp_date = datetime.strptime(self.groups[chat_id_str], "%Y-%m-%d")
        if exp_date < datetime.now():
            del self.groups[chat_id_str]
            self.save_groups()
            return False
        return True
