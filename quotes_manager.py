import random

class QuotesManager:
    def __init__(self, quotes_list=None):
        if quotes_list is None:
            # مجموعة اقتباسات افتراضية
            self.quotes = [
                "أحسنت! استمر في التفوق!",
                "👏 أنت نجم العلوم اليوم!",
                "ممتاز! keep going",
                "💡 العلم نور... وأنت منوره!"
            ]
        else:
            self.quotes = quotes_list

    def get_random_quote(self):
        return random.choice(self.quotes)
