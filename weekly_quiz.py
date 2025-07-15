import json
import random
import os
from datetime import datetime, timedelta

WEEKLY_QUIZ_FILE = "weekly_quiz_data.json"

class WeeklyQuiz:
    def __init__(self, questions_data):
        self.questions_data = questions_data
        self.results = self.load_results()

    def load_results(self):
        if os.path.exists(WEEKLY_QUIZ_FILE):
            with open(WEEKLY_QUIZ_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_results(self):
        with open(WEEKLY_QUIZ_FILE, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def generate_quiz(self, chat_id, grade, term, num_questions=10):
        key = f"{chat_id}_{grade}_{term}"
        if key not in self.questions_data or not self.questions_data[key]:
            return []
        questions_pool = self.questions_data[key][:]
        random.shuffle(questions_pool)
        return questions_pool[:num_questions]

    def record_score(self, chat_id, user_id, score):
        chat_str = str(chat_id)
        user_str = str(user_id)
        if chat_str not in self.results:
            self.results[chat_str] = {}
        self.results[chat_str][user_str] = score
        self.save_results()

    def get_winner(self, chat_id):
        chat_str = str(chat_id)
        if chat_str not in self.results or not self.results[chat_str]:
            return None, 0
        sorted_users = sorted(self.results[chat_str].items(), key=lambda x: x[1], reverse=True)
        top_user, top_score = sorted_users[0]
        return int(top_user), top_score

    def reset_weekly_results(self):
        self.results = {}
        self.save_results()
