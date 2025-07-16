
import random

class ReviewGame:
    def __init__(self):
        self.current_player = {}

    def choose_random_player(self, members, chat_id):
        last_player = self.current_player.get(chat_id)
        candidates = [m for m in members if m != last_player]
        if not candidates:
            candidates = members
        chosen = random.choice(candidates)
        self.current_player[chat_id] = chosen
        return chosen
