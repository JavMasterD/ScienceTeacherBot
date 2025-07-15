# group_manager.py

import json
import os
from datetime import datetime, timedelta

APPROVED_GROUPS_FILE = "approved_groups.json"

class GroupManager:
    def __init__(self):
        self.approved_groups = self.load_approved_groups()

    def load_approved_groups(self):
        if os.path.exists(APPROVED_GROUPS_FILE):
            with open(APPROVED_GROUPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_approved_groups(self):
        with open(APPROVED_GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.approved_groups, f, ensure_ascii=False, indent=2)

    def is_group_approved(self, chat_id):
        chat_id_str = str(chat_id)
        if chat_id_str in self.approved_groups:
            expiry_str = self.approved_groups[chat_id_str]
            expiry = datetime.fromisoformat(expiry_str)
            return datetime.now() < expiry
        return False

    def approve_group(self, chat_id, days=29):
        chat_id_str = str(chat_id)
        expiry_date = datetime.now() + timedelta(days=days)
        self.approved_groups[chat_id_str] = expiry_date.isoformat()
        self.save_approved_groups()

    def revoke_group(self, chat_id):
        chat_id_str = str(chat_id)
        if chat_id_str in self.approved_groups:
            del self.approved_groups[chat_id_str]
            self.save_approved_groups()

    def cleanup_expired(self):
        now = datetime.now()
        to_remove = []
        for chat_id_str, expiry_str in self.approved_groups.items():
            expiry = datetime.fromisoformat(expiry_str)
            if now >= expiry:
                to_remove.append(chat_id_str)
        for chat_id_str in to_remove:
            del self.approved_groups[chat_id_str]
        if to_remove:
            self.save_approved_groups()
