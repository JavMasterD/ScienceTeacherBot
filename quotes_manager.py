
import random

class QuotesManager:
    def __init__(self):
        self.quotes = [
            "أحسنت! استمر في التفوق!",
            "👏 أنت نجم العلوم اليوم!",
            "ممتاز! Keep going!",
            "💡 العلم نور... وأنت منوره!"
        ]

    def get_random_quote(self):
        return random.choice(self.quotes)
